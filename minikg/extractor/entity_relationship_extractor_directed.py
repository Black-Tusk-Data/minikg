from typing import Type
from pydantic import BaseModel
from minikg.extractor.base_extractor import BaseExtractor
from minikg.models import (
    CompletionShape,
    Entity,
    EntityRelationship,
    EntityWithFragment,
    FileFragment,
    MiniKgConfig,
)


class EntityRelationshipExtractor(BaseExtractor[EntityRelationship]):
    def __init__(
        self,
        *,
        config: MiniKgConfig,
        fragment: FileFragment,
        head_entities: list[EntityWithFragment],
        tail_entities: list[EntityWithFragment],
    ):
        super().__init__(config=config, fragment=fragment)
        self.head_entities = head_entities
        self.tail_entities = tail_entities
        return

    def _get_llm_extraction_item_type(self) -> type[EntityRelationship]:
        return EntityRelationship

    def _get_llm_extraction_item_shape(self) -> dict:
        raw = EntityRelationship.prompt_json_schema()
        # TODO: find a more elegant way to do this...
        raw["properties"]["source_entity"]["enum"] = [
            entity.get_qualified_name() for entity in self.head_entities
        ]
        raw["properties"]["target_entity"]["enum"] = [
            entity.get_qualified_name() for entity in self.tail_entities
        ]
        return raw

    def _get_entity_blurb(self, entity: EntityWithFragment) -> str:
        return f"'{entity.name}' - {entity.description}"

    def _get_entities_blurb(self, entities: list[EntityWithFragment]) -> str:
        return "\n".join([self._get_entity_blurb(entity) for entity in entities])

    def _get_user_prompt_lines(self) -> list[str]:
        return [
            "-GOAL-",
            f"Given a {self.config.document_desc} and a list of entities, identify the meaningful relationships FROM the source entities TO the target entities.",
            "-SOURCE ENTITIES-",
            self._get_entities_blurb(self.head_entities),
            "-TARGET ENTITIES-",
            self._get_entities_blurb(self.tail_entities),
            "-TEXT-",
            self._get_fragment_contents(),
        ]

    pass
