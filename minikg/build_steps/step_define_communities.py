import logging
from pathlib import Path
from typing import Type

import networkx as nx

from minikg.build_steps.base_step import MiniKgBuilderStep
from minikg.graphtools.flatten import flatten_multigraph
from minikg.models import Community, MiniKgConfig
from minikg.build_output import (
    BuildStepOutput_Graph,
    BuildStepOutput_MultiGraph,
    BuildStepOutput_Communities,
)


class Step_DefineCommunitiesLouvain(MiniKgBuilderStep[BuildStepOutput_Communities]):
    def __init__(
        self,
        config: MiniKgConfig,
        *,
        graph: BuildStepOutput_MultiGraph,
    ) -> None:
        super().__init__(config)
        self.graph = graph
        return

    def get_id(self) -> str:
        return self.graph.label

    @staticmethod
    def get_output_type() -> Type[BuildStepOutput_Communities]:
        return BuildStepOutput_Communities

    def _execute(self) -> BuildStepOutput_Communities:
        communities: list[set[str]] = nx.community.louvain_communities(self.graph.G)
        # louvain has no nesting, these are just lists of node IDs
        return BuildStepOutput_Communities([
            Community(
                id=str(i),
                child_node_ids=list(node_ids),
            )
            for i, node_ids in enumerate(communities)
        ])

    pass


class Step_DefineCommunitiesLeiden(MiniKgBuilderStep[BuildStepOutput_Communities]):
    def __init__(
        self,
        config: MiniKgConfig,
        *,
        graph: BuildStepOutput_MultiGraph,
    ) -> None:
        super().__init__(config)
        self.graph = graph
        return

    def get_id(self) -> str:
        return self.graph.label

    @staticmethod
    def get_output_type() -> Type[BuildStepOutput_Communities]:
        return BuildStepOutput_Communities

    def _execute(self) -> BuildStepOutput_Communities:
        from graspologic.partition import hierarchical_leiden, HierarchicalCluster

        logging.info("normal G: %s", self.graph.G.nodes)
        flat_G = flatten_multigraph(self.graph.G)
        logging.info("flat G: %s", flat_G.nodes)

        hierarchy_rows: list[HierarchicalCluster] = hierarchical_leiden(
            flat_G.to_undirected(),
            # TODO: iss-3
            max_cluster_size=10,
            random_seed=42,
            resolution=1,  # larger -> smaller communities
        )

        communities_by_id: dict[str, Community] = {}
        for row in hierarchy_rows:
            # all
            community_id = str(row.cluster)
            if row.is_final_cluster:
                # a node
                if community_id not in communities_by_id:
                    communities_by_id[community_id] = Community(
                        id=community_id,
                    )
                    pass
                # - 'community.node' is the node ID
                communities_by_id[community_id].child_node_ids.append(row.node)
                pass
            # o/w, a true community
            if community_id in communities_by_id:
                # we've already computed the children of this community
                continue

            child_clusters = [
                row2
                for row2 in hierarchy_rows
                if row2.parent_cluster == row.cluster
            ]

            communities_by_id[community_id] = Community(
                id=community_id,
                child_community_ids=list(set(
                    cluster.cluster
                    for cluster in child_clusters
                    if not cluster.is_final_cluster
                )),
                child_node_ids=list(set(
                    cluster.cluster
                    for cluster in child_clusters
                    if cluster.is_final_cluster
                )),
            )
            pass

        # TODO: please check the above on a more complex graph

        return BuildStepOutput_Communities(
            list(communities_by_id.values())
        )

    pass
