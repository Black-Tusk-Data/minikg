import networkx as nx

from minikg.models import MiniKgConfig


class GraphMerger:
    def __init__(
        self,
        config: MiniKgConfig,
        *,
        graphs: list[nx.Graph],  # TODO: could be multigraph already
    ):
        self.config = config
        self.graphs = graphs
        return

    def merge(self) -> nx.MultiGraph:
        G_new = nx.MultiGraph()
        # nodes
        for G in self.graphs:
            # 'node_label' is just a string
            for node_label in G.nodes:
                if node_label in G_new:
                    # TODO: could merge the attrs potentially
                    continue
                G_new.add_node(
                    node_label,
                    **G.nodes[node_label],
                )
                pass
            pass

        # edges
        for G in self.graphs:
            # TODO:
            #  - change to multigraph and just gather up edges
            #  - we can add a 'flatten edges' step after

            # 'edge' is a tuple of strings
            for edge in G.edges:
                # if edge in G_new:
                #     # TODO: again, could merge these more intelligently
                #     continue
                G_new.add_edge(*edge, **G.edges[edge])
                pass
            pass
        return G_new

    pass
