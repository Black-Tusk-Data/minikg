from typing import Type
from pydantic import BaseModel
from minikg.extractor.base_extractor import BaseExtractor
from minikg.models import (
    EntityRelationshipUndirected,
    EntityWithFragment,
    FileFragment,
    MiniKgConfig,
)


class EntityRelationshipExtractorUndirected(
    BaseExtractor[EntityRelationshipUndirected]
):
    def __init__(
        self,
        *,
        config: MiniKgConfig,
        fragment: FileFragment,
        entities: list[EntityWithFragment],
    ):
        super().__init__(config=config, fragment=fragment)
        self.entities = entities
        return

    def _get_system_prompt_lines(self) -> list[str]:
        elected_goal = next(
            goal for goal in self._get_prompt_goal_preference_order() if goal
        )
        return [
            f"You are {self.config.role_desc}.",
            elected_goal,
        ]

    def _get_prompt_goal_preference_order(self) -> list[str]:
        return [
            self.config.extraction_prompt_override_entity_relationship_undirected,
            f"Given a {self.config.document_desc} and a list of entities, identify the meaningful relationships between the provided entities.",
            "Be specific about the relationships you identify - only a few entities should be related by a single relationship.",
        ]

    def _get_llm_extraction_item_type(self) -> type[EntityRelationshipUndirected]:
        return EntityRelationshipUndirected

    def _get_llm_extraction_item_shape(self) -> dict:
        raw = EntityRelationshipUndirected.prompt_json_schema()
        # TODO: find a more elegant way to do this...
        raw["properties"]["related_entities"]["items"]["enum"] = [
            entity.get_qualified_name() for entity in self.entities
        ]
        return raw

    def _get_entity_blurb(self, entity: EntityWithFragment) -> str:
        return f"'{entity.name}' - {entity.description}"

    def _get_entities_blurb(self, entities: list[EntityWithFragment]) -> str:
        return "\n".join([self._get_entity_blurb(entity) for entity in entities])

    def _get_user_prompt_lines(self) -> list[str]:
        return [
            "<ENTITIES_DESCRIPTION>",
            self._get_entities_blurb(self.entities),
            "</ENTITIES_DESCRIPTION>",
            "<FRAGMENT_CONTENTS>",
            self._get_fragment_contents(),
            "</FRAGMENT_CONTENTS>",
        ]

    pass
