import abc
from typing import Type
from pydantic import BaseModel
from minikg.extractor.base_extractor import BaseExtractor
from minikg.models import Entity


class EntityExtractor(BaseExtractor[Entity], abc.ABC):
    def _get_llm_extraction_item_type(self) -> type[Entity]:
        return Entity

    def _post_process(self, extractions: list[Entity]) -> list[Entity]:
        if self.config.force_uppercase_node_names:
            for entity in extractions:
                entity.name = entity.name.upper()
                pass
            pass
        return extractions

    def _get_system_prompt_lines(self) -> list[str]:
        elected_goal = next(
            goal for goal in self._get_prompt_goal_preference_order() if goal
        )
        return [
            f"You are {self.config.role_desc}.",
            elected_goal,
            " ".join(
                [
                    "Only identify entities of the following types:",
                    *self.config.entity_types,
                ]
            ),
        ]

    def _get_llm_extraction_item_shape(self) -> dict:
        raw = Entity.prompt_json_schema(
            description_overrides={
                k: v
                for k, v in [
                    ("description", self.config.entity_description_desc),
                    ("entity_type", self.config.entity_type_desc),
                    ("name", self.config.entity_name_desc),
                ]
                if v
            }
        )
        # TODO: find a more elegant way to do this...
        raw["properties"]["entity_type"]["enum"] = self.config.entity_types
        return raw

    def _get_user_prompt_lines(self) -> list[str]:
        return [
            "<FRAGMENT_CONTENTS>",
            self._get_fragment_contents(),
            "</FRAGMENT_CONTENTS>",
        ]

    @abc.abstractmethod
    def _get_prompt_goal_preference_order(self) -> list[str]:
        pass

    pass


class EntityExtractorUndirected(EntityExtractor):
    def _get_prompt_goal_preference_order(self) -> list[str]:
        return [
            self.config.extraction_prompt_override_entity_head,
            self.config.extraction_prompt_override_entity_tail,
            f"Given a {self.config.document_desc} that is potentially relevant to this activity, identify all entities from within that text that capture the information and ideas it contains.",
        ]

    pass


class EntityExtractorHead(EntityExtractor):
    def _get_prompt_goal_preference_order(self) -> list[str]:
        return [
            self.config.extraction_prompt_override_entity_head,
            f"Given a {self.config.document_desc} that is potentially relevant to this activity, identify all entities DEFINED within that text that capture the information and ideas it contains.",
        ]

    pass


class EntityExtractorTail(EntityExtractor):
    def _get_prompt_goal_preference_order(self) -> list[str]:
        return [
            self.config.extraction_prompt_override_entity_tail,
            f"Given a {self.config.document_desc} that is potentially relevant to this activity, identify all entities REFERENCED BUT NOT DEFINED within that text that capture the information and ideas it contains.",
        ]

    pass
