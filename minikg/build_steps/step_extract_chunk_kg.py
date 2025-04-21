from pathlib import Path

import networkx as nx

from minikg.build_steps.base_step import MiniKgBuilderStep
from minikg.extractor import entity_relationship_extractor
from minikg.extractor.entity_extractor import (
    EntityExtractorHead,
    EntityExtractorTail,
    EntityExtractorUndirected,
)
from minikg.extractor.entity_relationship_extractor import EntityRelationshipExtractor
from minikg.models import Entity, FileFragment, MiniKgConfig
from minikg.build_output import BuildStepOutput_Graph


class Step_ExtractChunkKg(MiniKgBuilderStep[BuildStepOutput_Graph]):
    def __init__(self, config: MiniKgConfig, *, fragment: FileFragment) -> None:
        super().__init__(config)
        self.fragment = fragment
        return

    def get_id(self) -> str:
        return self.fragment.fragment_id

    @staticmethod
    def get_output_type():
        return BuildStepOutput_Graph

    def _extract_entities(self) -> tuple[list[Entity], list[Entity]]:
        """
        Return (head entities, tail entities)
        """
        if self.config.extraction_entities_undirected:
            entity_extactor = EntityExtractorUndirected(
                config=self.config,
                fragment=self.fragment,
            )
            entities = entity_extactor.extract()
            return (entities, entities)
        head_entity_extactor = EntityExtractorHead(
            config=self.config,
            fragment=self.fragment,
        )
        tail_entity_extactor = EntityExtractorTail(
            config=self.config,
            fragment=self.fragment,
        )
        head_entities = head_entity_extactor.extract()
        tail_entities = tail_entity_extactor.extract()
        return (head_entities, tail_entities)

    def _execute(self):
        head_entities, tail_entities = self._extract_entities()

        entity_relationship_extractor = EntityRelationshipExtractor(
            config=self.config,
            fragment=self.fragment,
            head_entities=head_entities,
            tail_entities=tail_entities,
        )
        entity_relationships = entity_relationship_extractor.extract()

        G = nx.Graph()
        for entity in head_entities:
            G.add_node(
                entity.name,
                entity_type=entity.entity_type,
                description=entity.description,
                defining_fragment=self.fragment.model_dump(),
            )
            pass
        for entity in tail_entities:
            # I'm going to move this to a separate step
            pass

        for relationship in entity_relationships:
            G.add_edge(
                relationship.source_entity,
                relationship.target_entity,
                description=relationship.relationship_description,
                weight=relationship.weight,
            )
            pass

        graph_label = f"doc-{self.get_id()}"
        return BuildStepOutput_Graph(
            G=G,
            label=graph_label,
        )

    pass
