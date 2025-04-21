import json
import logging

import lancedb
from lancedb.pydantic import LanceModel, Vector
from pydantic import BaseModel

from expert_llm.cached_embedder import CachedEmbedder
from expert_llm.remote.jina_ai_client import JinaAiClient

from minikg.models import MiniKgConfig, Node, Edge

DB_FNAME = "vectors.lancedb"


class GraphSemanticDb:
    EMBEDDING_BATCH_SIZE = 20

    def __init__(self, config: MiniKgConfig, *, name: str):
        class IndexedItem(LanceModel):
            vector: Vector(config.embedding_size)
            pass

        class _IndexedNode(IndexedItem, Node):
            pass

        class _IndexedEdge(IndexedItem, Edge):
            pass

        self.name = name
        self.index_node_class = _IndexedNode
        self.index_edge_class = _IndexedEdge

        self.config = config
        self.db_path = self.config.persist_dir / self.name / DB_FNAME
        is_fresh = not self.db_path.exists()
        self.db = lancedb.connect(self.db_path)
        self.embedding_client = CachedEmbedder(
            client=JinaAiClient(self.config.embedding_model),
            cache_dir=self.config.persist_dir,
        )

        if is_fresh:
            logging.info("creating new vector db...")
            # could keep nodes and edges separate?
            self.nodes = self.db.create_table(
                "node", schema=_IndexedNode.to_arrow_schema()
            )
            self.edges = self.db.create_table(
                "edge", schema=_IndexedEdge.to_arrow_schema()
            )
            pass
        else:
            logging.debug("loading existing vector db...")
            self.nodes = self.db.open_table("node")
            self.edges = self.db.open_table("edge")
            pass
        return

    def add_nodes(self, nodes: list[Node]):
        embeddings = self.embedding_client.embed([node.description for node in nodes])
        self.nodes.add(
            [
                self.index_node_class(**node.model_dump(), vector=embedding)
                for embedding, node in zip(embeddings, nodes)
            ]
        )
        return

    def add_edges(self, edges: list[Edge]):
        embeddings = self.embedding_client.embed([edge.description for edge in edges])
        self.edges.add(
            [
                self.index_edge_class(**edge.model_dump(), vector=embedding)
                for embedding, edge in zip(embeddings, edges)
            ]
        )
        return

    def search_nodes(
        self,
        query: str,
        *,
        k=10,
    ) -> tuple[list[float], list[Node]]:
        query_vec = self.embedding_client.embed([query])[0]
        # Note the key '_distance' is added to each item!
        results = self.nodes.search(query_vec).metric("cosine").limit(k).to_list()
        return (
            [r["_distance"] for r in results],
            [Node(**{attr: r[attr] for attr in Node.model_fields}) for r in results],
        )

    def search_edges(
        self,
        query: str,
        *,
        k=10,
    ) -> tuple[list[float], list[Edge]]:
        query_vec = self.embedding_client.embed([query])[0]
        # Note the key '_distance' is added to each item!
        results = self.edges.search(query_vec).metric("cosine").limit(k).to_list()
        return (
            [r["_distance"] for r in results],
            [Edge(**{attr: r[attr] for attr in Edge.model_fields}) for r in results],
        )

    pass
