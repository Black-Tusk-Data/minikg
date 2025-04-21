import logging
from typing import Type

from btdcore.utils import batched
import networkx as nx

from minikg.build_output import (
    BuildStepOutput_IndexedCommunity,
    BuildStepOutput_MultiGraph,
)
from minikg.build_steps.base_step import MiniKgBuilderStep
from minikg.graph_semantic_db import GraphSemanticDb
from minikg.models import Community, Edge, MiniKgConfig, Node


class Step_IndexCommunity(MiniKgBuilderStep[BuildStepOutput_IndexedCommunity]):
    ENTITY_CHUNK_SIZE = 50

    def __init__(
        self,
        config: MiniKgConfig,
        *,
        master_graph: BuildStepOutput_MultiGraph,
        community: Community,
    ):
        super().__init__(config)
        self.master_graph = master_graph
        self.community = community
        return

    def get_id(self) -> str:
        return f"community-index:{self.community.id}"

    @staticmethod
    def get_output_type() -> Type[BuildStepOutput_IndexedCommunity]:
        return BuildStepOutput_IndexedCommunity

    def _execute(self) -> BuildStepOutput_IndexedCommunity:
        # revisit the name of this DB
        semantic_db = GraphSemanticDb(self.config, name=self.community.id)

        subgraph = nx.subgraph(self.master_graph.G, self.community.child_node_ids)

        valid_nodes = [
            node for node in subgraph.nodes if subgraph.nodes[node].get("description")
        ]
        if len(valid_nodes) < len(subgraph.nodes):
            logging.info(
                "saving %d valid nodes (%d %% of the community)",
                len(valid_nodes),
                len(valid_nodes) * 100.0 / len(subgraph.nodes),
            )
            pass

        # subgraph.nodes
        for node_chunk in batched(list(valid_nodes), self.ENTITY_CHUNK_SIZE):
            semantic_db.add_nodes(
                [
                    Node(
                        name=node,
                        description=subgraph.nodes[node]["description"],
                        entity_type=subgraph.nodes[node]["entity_type"],
                    )
                    for node in node_chunk
                ]
            )
            pass
        for edge_chunk in batched(list(subgraph.edges), self.ENTITY_CHUNK_SIZE):
            semantic_db.add_edges(
                [
                    Edge(
                        nodes=tuple(sorted([edge[0], edge[1]])),
                        description=subgraph.edges[edge]["description"],
                        edge_id=0 if len(edge) < 3 else edge[2],
                    )
                    for edge in edge_chunk
                ]
            )
            pass
        return BuildStepOutput_IndexedCommunity(semantic_db_name=semantic_db.name)

    pass
