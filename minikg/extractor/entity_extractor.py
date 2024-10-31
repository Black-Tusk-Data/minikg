from typing import Type
from pydantic import BaseModel
from minikg.extractor.base_extractor import BaseExtractor
from minikg.models import Entity, FileFragment


class EntityExtractor(BaseExtractor[Entity]):
    def _get_output_shape(self) -> Type[BaseModel]:
        return Entity

    def _get_user_prompt_lines(self) -> list[str]:
        text: str
        with open(self.fragment.source_path) as f:
            lines = f.readlines()
            text = "".join(lines[
                self.fragment.start_line_incl:
                self.fragment.end_line_excl
            ])
            pass
        return [
            "-GOAL-",
            "Given a text document that is potentially relevant to this activity, identify all the entities from within that text that capture the information and ideas it contains.",
            "-TEXT-",
            text,
        ]

    def _get_system_prompt_lines(self) -> list[str]:
        return [
            f"You are a {self.config.knowledge_domain} expert.",
        ]

    pass
