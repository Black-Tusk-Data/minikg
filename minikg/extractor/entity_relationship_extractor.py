from typing import Type
from pydantic import BaseModel
from minikg.extractor.base_extractor import BaseExtractor
from minikg.models import CompletionShape, Entity, EntityRelationship, FileFragment, MiniKgConfig


class EntityRelationshipExtractor(BaseExtractor[EntityRelationship]):
    def __init__(self, *, config: MiniKgConfig, fragment: FileFragment, entities: list[Entity]):
        super().__init__(config=config, fragment=fragment)
        self.entities = entities
        return
    def _get_llm_extraction_item_type(self) -> type[EntityRelationship]:
        return EntityRelationship

    def _get_llm_extraction_item_shape(self) -> dict:
        raw = EntityRelationship.prompt_json_schema()
        # TODO: find a more elegant way to do this...
        entity_names = [entity.name for entity in self.entities]
        raw["properties"]["source_entity"]["enum"] = entity_names
        raw["properties"]["target_entity"]["enum"] = entity_names
        return raw

    def _get_entity_blurb(self, entity: Entity) -> str:
        return f"'{entity.name}' - {entity.description}"

    def _get_all_entities_blurb(self) -> str:
        return "\n".join([
            self._get_entity_blurb(entity)
            for entity in self.entities
        ])

    def _get_user_prompt_lines(self) -> list[str]:
        return [
            "-GOAL-",
            "Given a text document that is potentially relevant to this activity and a list of entity types, identify all the meaningful relationships between those entities.",
            "-ENTITIES-",
            self._get_all_entities_blurb(),
            "-TEXT-",
            self._get_fragment_contents(),
        ]

    pass
