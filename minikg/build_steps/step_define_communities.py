from pathlib import Path
from typing import Type

import networkx as nx

from minikg.build_steps.base_step import MiniKgBuilderStep
from minikg.models import MiniKgConfig
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
        return BuildStepOutput_Communities(
            [list(community) for community in communities]
        )

    pass


# TODO: Leiden algorithm
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

        flat_G = nx.Graph()
        flat_G.add_nodes_from(self.graph.G.nodes)

        # TODO: iss-5
        for u, v, _weight in self.graph.G.edges:
            flat_G.add_edge(u, v)
            pass


        communities: list[HierarchicalCluster] = hierarchical_leiden(
            flat_G.to_undirected(),
            # TODO: iss-3
            max_cluster_size=10,
            random_seed=42,
            resolution=1,  # larger -> smaller communities
        )

        clusters: dict[str, list[str]] = {}
        for com in communities:
            cluster_id = str(com.cluster)
            if com.is_final_cluster:
                if cluster_id not in clusters:
                    clusters[cluster_id] = []
                    pass
                clusters[cluster_id].append(com.node)
                pass
            if cluster_id in clusters:
                # already computed
                continue
            child_cluster_ids = set(
                [
                    str(com2.cluster)
                    for com2 in communities
                    if com2.parent_cluster == com.cluster
                ]
            )
            clusters[cluster_id] = list(child_cluster_ids)
            pass

        return BuildStepOutput_Communities(
            # TODO: iss-4 - this is fairly broken without
            list(clusters.values())
        )

    pass
