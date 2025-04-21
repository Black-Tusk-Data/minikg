import logging
import pickle

from sklearn.metrics.pairwise import cosine_similarity
import networkx as nx

from minikg import utils
from minikg.models import GraphType, MiniKgConfig
from minikg.services import services


class GraphEdgeCompressor:
    THRESHOLD_SIMILARITY = 0.8
    BACKUP_INTERVAL = 100

    def __init__(
        self,
        config: MiniKgConfig,
        *,
        G: nx.MultiGraph,
    ):
        self.config = config
        self.G = G
        self.graph_cache = (
            self.config.persist_dir / f"compress-cache-v{self.config.version}"
        )
        return

    def _backup(self, G_new: GraphType) -> None:
        logging.info(
            "saving partially compressed graph with %d edges",
            len(G_new.edges),
        )
        with open(self.graph_cache, "wb") as f:
            pickle.dump(G_new, f)
            pass
        return

    def _load_from_backup(self) -> GraphType | None:
        if not self.graph_cache.exists():
            return None
        with open(self.graph_cache, "rb") as f:
            logging.info("found partially compressed graph!")
            return pickle.load(f)
        pass

    def _summarize_edge_descriptions(
        self,
        *,
        between_node_names: tuple[str, str],
        edge_descriptions: list[str],
    ) -> str:
        r = services.llm_api.completion(
            req_name="summarize_edges",
            system=f"You are a helpful {self.config.knowledge_domain} expert.",
            user="\n".join(
                [
                    " ".join(
                        [
                            "Summarize the relationship between",
                            between_node_names[0],
                            "and",
                            between_node_names[1],
                            "Given the following information about their relationship.",
                            "Your summary should be based ONLY upon the following information:",
                        ]
                    ),
                    *edge_descriptions,
                ]
            ),
        )
        return r.message

    def _copy_nodes(
        self,
        G_new: nx.Graph | nx.MultiGraph,
    ) -> None:
        for node_label in self.G.nodes:
            G_new.add_node(
                node_label,
                **self.G.nodes[node_label],
            )
            pass
        return

    def compress_redundant(self) -> nx.MultiGraph:
        """
        For every neighbours u and v, detect and merge any redundant edges between them.
         - Redundancy is assesed via cosine similarity above a certain threshold
         - Edge weight is averaged
         - Redundant edge descriptions couuld summarized via an LLM call, but we're just picking one for now

        (This enables the Louvain community-detection algorithm)
        """
        G_new = self._load_from_backup() or nx.MultiGraph()
        self._copy_nodes(G_new)
        logging.info("compressing %d edges", len(self.G.edges))

        i = 0
        for u, v, idx in self.G.edges:
            i += 1
            if i % self.BACKUP_INTERVAL == 0:
                self._backup(G_new)
                pass
            if G_new.has_edge(u, v):
                continue
            # grab all the edges between u and v
            uv_edges = list(self.G.subgraph((u, v)).edges)
            if len(uv_edges) < 2:
                G_new.add_edge(
                    u,
                    v,
                    **self.G.edges[u, v, idx],
                )
                continue
            description_embeddings = services.embedding_api.embed(
                [self.G.edges[edge]["description"] for edge in uv_edges]
            )
            similarities = cosine_similarity(description_embeddings)
            # partition into clusters, pick a leader
            clusters = utils.cluster_from_similarities(
                pairwise_similarities=similarities,
                threshold_similarity=self.THRESHOLD_SIMILARITY,
            )
            logging.debug(
                "compressed %d edges into %d",
                len(uv_edges),
                len(clusters),
            )

            # we'll just take the first entry of each cluster as the 'leader'
            compressed_edge_indexes = [cluster[0] for cluster in clusters]
            for edge_idx in compressed_edge_indexes:
                edge = uv_edges[edge_idx]
                G_new.add_edge(
                    u,
                    v,
                    **self.G.edges[*edge],
                )
                pass
            pass
        return G_new

    def compress_fully(self) -> nx.Graph:
        """
        Compress all parallel edges, to output a strict graph.
         - Edge weights are summed (edges are assumed to be not-redundant)
         - Edge descriptions are sumamrized via an LLM call

        (This enables the Leiden community-detection algorithm)
        """
        G_new = nx.Graph()
        self._copy_nodes(G_new)

        for u, v, idx in self.G.edges:  # multi-graphs have a third item in the tuple
            # TODO we're assuming that all the edge descriptions will fit into a prompt
            if G_new.has_edge(u, v):
                continue
            # grab all the edges between u and v
            edges_to_summarize = G_new.subgraph((u, v)).edges
            if len(edges_to_summarize) < 2:
                G_new.add_edge(
                    u,
                    v,
                    **self.G.edges[u, v, idx],
                )
                pass
            summarized_description = self._summarize_edge_descriptions(
                between_node_names=(u, v),
                edge_descriptions=[
                    self.G.edges[edge]["description"] for edge in edges_to_summarize
                ],
            )
            total_weight = sum(
                [self.G.edges[edge]["weight"] for edge in edges_to_summarize]
            )
            # / len(edges_to_summarize)
            G_new.add_edge(
                u, v, description=summarized_description, weight=total_weight
            )
            pass
        return G_new

    pass
