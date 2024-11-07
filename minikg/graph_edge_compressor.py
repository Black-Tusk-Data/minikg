import networkx as nx

from minikg.models import MiniKgConfig


class GraphEdgeCompressor:
    def __init__(
        self,
        config: MiniKgConfig,
        *,
        G: nx.MultiGraph,
    ):
        self.config = config
        self.G = G
        return

    def compress_redundant(self) -> nx.MultiGraph:
        """
        For every neighbours u and v, detect and merge any redundant edges between them.
         - Redundancy is assesed via cosine similarity above a certain threshold
         - Edge weight is averaged
         - Edge descriptions are sumamrized via an LLM call

        (This enables the Louvain community-detection algorithm)
        """
        G_new = nx.MultiGraph()
        # nodes
        for node_label in self.G.nodes:
            G_new.add_node(
                node_label,
                **self.G[node_label],
            )
            pass

        # edges
        # TODO
        return G_new

    def compress_fully(self) -> nx.Graph:
        """
        Compress all parallel edges, to output a strict graph.
         - Edge weights are summed (edges are assumed to be not-redundant)
         - Edge descriptions are sumamrized via an LLM call

        (This enables the Leiden community-detection algorithm)
        """
        G_new = nx.Graph()
        return G_new

    pass
