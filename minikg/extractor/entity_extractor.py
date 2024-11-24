from typing import Type
from pydantic import BaseModel
from minikg.extractor.base_extractor import BaseExtractor
from minikg.models import Entity


class EntityExtractor(BaseExtractor[Entity]):
    def _get_llm_extraction_item_type(self) -> type[Entity]:
        return Entity

    def _post_process(self, extractions: list[Entity]) -> list[Entity]:
        # could group these if they are too similar
        for entity in extractions:
            entity.name = entity.name.upper()
            pass
        return extractions

    def _get_llm_extraction_item_shape(self) -> dict:
        raw = Entity.prompt_json_schema()
        # TODO: find a more elegant way to do this...
        raw["properties"]["entity_type"]["enum"] = self.config.entity_types
        return raw

    def _get_user_prompt_lines(self) -> list[str]:
        return [
            "-GOAL-",
            f"Given a {self.config.document_desc} that is potentially relevant to this activity, identify all entities from within that text that capture the information and ideas it contains.",
            " ".join([
                "Only identify entities of the following types:",
                *self.config.entity_types,
            ]),
            "-TEXT-",
            self._get_fragment_contents(),
        ]

    pass
