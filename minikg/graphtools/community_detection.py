import abc
import logging

import networkx as nx

from minikg.graphtools.flatten import flatten_multigraph
from minikg.models import Community


class CommunityDetector(abc.ABC):
    # expect a multigraph!
    @abc.abstractmethod
    def get_communities(self, G: nx.MultiGraph) -> list[Community]:
        pass

    pass


class CommunityDetectorLouvain(CommunityDetector):
    def get_communities(self, G: nx.MultiGraph) -> list[Community]:
        # louvain has no nesting, these are just lists of node IDs
        community_ids: list[set[str]] = nx.community.louvain_communities(G)
        return [
            Community(
                id=str(i),
                child_node_ids=list(node_ids),
            )
            for i, node_ids in enumerate(community_ids)
        ]

    pass


class CommunityDetectorLeiden(CommunityDetector):
    def get_communities(self, G: nx.MultiGraph) -> list[Community]:
        from graspologic.partition import hierarchical_leiden, HierarchicalCluster

        if not G.nodes:
            return []

        # leiden doesn't like multigraphs
        flat_G = flatten_multigraph(G)

        hierarchy_rows: list[HierarchicalCluster] = hierarchical_leiden(
            flat_G.to_undirected(),
            # TODO: iss-3
            max_cluster_size=7,
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
                row2 for row2 in hierarchy_rows if row2.parent_cluster == row.cluster
            ]

            communities_by_id[community_id] = Community(
                id=community_id,
                child_community_ids=list(
                    set(
                        str(cluster.cluster)
                        for cluster in child_clusters
                        if not cluster.is_final_cluster
                    )
                ),
                child_node_ids=list(
                    set(
                        str(cluster.node)
                        for cluster in child_clusters
                        if cluster.is_final_cluster
                    )
                ),
            )
            pass
        return list(communities_by_id.values())

    pass
