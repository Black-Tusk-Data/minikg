from pathlib import Path

import networkx as nx

from minikg.build_steps.base_step import MiniKgBuilderStep
from minikg.extractor import entity_relationship_extractor
from minikg.extractor.entity_extractor import (
    EntityExtractor,
    EntityExtractorHead,
    EntityExtractorTail,
    EntityExtractorUndirected,
)
from minikg.extractor.entity_relationship_extractor import EntityRelationshipExtractor
from minikg.models import Entity, EntityWithFragment, FileFragment, MiniKgConfig
from minikg.build_output import BuildStepOutput_Entities, BuildStepOutput_Graph
from minikg.splitter import Splitter


class Step_IdentifyEntities(MiniKgBuilderStep[BuildStepOutput_Entities]):
    def __init__(self, config: MiniKgConfig, *, file_path: Path) -> None:
        super().__init__(config)
        self.file_path = file_path
        self.splitter = Splitter(config=config)
        return

    def get_id(self) -> str:
        return str(self.file_path).replace("/", ":")

    @staticmethod
    def get_output_type():
        return BuildStepOutput_Entities

    def _get_entity_extractor_cls(self) -> type[EntityExtractor]:
        """
        Return (head entities, tail entities)
        """
        if self.config.extraction_entities_undirected:
            return EntityExtractorUndirected
        return EntityExtractorHead

    def _execute(self):
        extractor_cls = self._get_entity_extractor_cls()
        file_chunks = self.splitter.split_file(self.file_path)
        entities: list[EntityWithFragment] = []
        for chunk in file_chunks:
            extractor = extractor_cls(
                config=self.config,
                fragment=chunk,
            )
            fragment_entities = extractor.extract()
            entities.extend(
                EntityWithFragment(
                    **entity.model_dump(),
                    fragment=chunk,
                )
                for entity in fragment_entities
            )
            pass

        return BuildStepOutput_Entities(entities=entities)

    pass
