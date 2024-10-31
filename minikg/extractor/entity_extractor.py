from typing import Type
from pydantic import BaseModel
from minikg.extractor.base_extractor import BaseExtractor
from minikg.models import CompletionShape, Entity


class EntityExtractor(BaseExtractor[Entity]):
    def _get_llm_output_shape(self) -> Type[CompletionShape]:
        return Entity

    def _get_user_prompt_lines(self) -> list[str]:
        return [
            "-GOAL-",
            "Given a text document that is potentially relevant to this activity, identify all the entities from within that text that capture the information and ideas it contains.",
            "-TEXT-",
            self._get_fragment_contents(),
        ]

    pass
