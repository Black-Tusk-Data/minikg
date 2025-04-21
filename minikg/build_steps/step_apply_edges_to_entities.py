from pathlib import Path

import networkx as nx

from minikg.services import services
from minikg.build_steps.base_step import MiniKgBuilderStep
from minikg.extractor import entity_relationship_extractor
from minikg.extractor.entity_extractor import (
    EntityExtractor,
    EntityExtractorHead,
    EntityExtractorTail,
    EntityExtractorUndirected,
)
from minikg.extractor.entity_relationship_extractor import EntityRelationshipExtractor
from minikg.models import (
    Entity,
    EntityRelationship,
    EntityWithFragment,
    FileFragment,
    MiniKgConfig,
)
from minikg.build_output import (
    BuildStepOutput_Edges,
    BuildStepOutput_Graph,
    BuildStepOutput_MultiGraph,
)
from minikg.splitter import Splitter


class Step_ApplyEdgesToEntities(MiniKgBuilderStep[BuildStepOutput_MultiGraph]):
    DELIMITER = "::"

    def __init__(
        self,
        config: MiniKgConfig,
        *,
        entities: list[EntityWithFragment],
        edges: list[EntityRelationship],
    ) -> None:
        super().__init__(config)
        self.entities = entities
        self.edges = edges
        return

    @staticmethod
    def get_output_type():
        return BuildStepOutput_MultiGraph

    def get_id(self) -> str:
        return "v1"

    def _execute(self):
        G = nx.MultiGraph()
        for entity in self.entities:
            G.add_node(
                entity.get_qualified_name(),
                entity_type=entity.entity_type,
                description=entity.description,
                defining_fragment=entity.fragment.model_dump(),
            )
            pass
        for relationship in self.edges:
            G.add_edge(
                relationship.source_entity,
                relationship.target_entity,
                description=relationship.relationship_description,
                # weight=relationship.weight,
            )
            pass
        graph_label = f"doc-{self.get_id()}"
        return BuildStepOutput_MultiGraph(
            G=G,
            label=graph_label,
        )

    pass
