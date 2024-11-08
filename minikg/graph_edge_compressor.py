from expert_llm.models import ChatBlock
from expert_llm.remote.openai_shaped_client_implementations import OpenAIApiClient
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
        self.llm_client = OpenAIApiClient("gpt-4o")
        self.embedding_client = OpenAIApiClient("text-embedding-3-small")
        return

    def _summarize_edge_descriptions(
            self,
            *,
            between_node_names: tuple[str, str],
            edge_descriptions: list[str],
    ) -> str:
        r = self.llm_client.chat_completion([
            ChatBlock(
                role="system",
                content=f"You are a helpful {self.config.knowledge_domain} expert.",
            ),
            ChatBlock(
                role="user",
                content="\n".join([
                    " ".join([
                        "Summarize the relationship between",
                        between_node_names[0], "and", between_node_names[1],
                        "Given the following information about their relationship.",
                        "Your summary should be based ONLY upon the following information:",
                    ]),
                    *edge_descriptions,
                ]),
            ),
        ])
        return r.content

    def compress_redundant(self) -> nx.MultiGraph:
        """
        For every neighbours u and v, detect and merge any redundant edges between them.
         - Redundancy is assesed via cosine similarity above a certain threshold
         - Edge weight is averaged
         - Edge descriptions are summarized via an LLM call

        (This enables the Louvain community-detection algorithm)
        """
        G_new = nx.MultiGraph()

        return G_new

    def compress_fully(self) -> nx.Graph:
        """
        Compress all parallel edges, to output a strict graph.
         - Edge weights are summed (edges are assumed to be not-redundant)
         - Edge descriptions are sumamrized via an LLM call

        (This enables the Leiden community-detection algorithm)
        """
        G_new = nx.Graph()
        # nodes
        for node_label in self.G.nodes:
            G_new.add_node(
                node_label,
                **self.G[node_label],
            )
            pass

        # edges
        for u, v, idx in self.G.edges: # multi-graphs have a third item in the tuple
            # TODO we're assuming that all the edge descriptions will fit into a prompt
            if G_new.has_edge(u, v):
                continue
            # grab all the edges between u and v
            edges_to_summarize = G_new.subgraph((u, v)).edges
            summarized_description = self._summarize_edge_descriptions(
                between_node_names=(u, v),
                edge_descriptions=[
                    self.G.edges[edge]["description"]
                    for edge in edges_to_summarize
                ]
            )
            total_weight = sum([
                self.G.edges[edge]["weight"]
                for edge in edges_to_summarize
            ])
            # / len(edges_to_summarize)
            G_new.add_edge(u, v, description=summarized_description, weight=total_weight)
            pass
        return G_new

    pass
