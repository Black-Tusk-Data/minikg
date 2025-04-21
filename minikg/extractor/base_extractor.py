"""
Use larger chunk sizes with multiple rounds
"""

import abc
from typing import Generic, Type, TypeVar, cast

from expert_llm.models import ChatBlock
from expert_llm.remote.openai_shaped_client_implementations import (
    OpenAIApiClient,
    TogetherAiClient,
)
from pydantic import Field, create_model, BaseModel

from minikg.services import services
from minikg.models import CompletionShape, FileFragment, MiniKgConfig

T = TypeVar("T", bound=CompletionShape)


class BaseExtractor(Generic[T], abc.ABC):
    def __init__(
        self,
        *,
        config: MiniKgConfig,
        fragment: FileFragment,
    ):
        self.config = config
        self.fragment = fragment
        return

    def _get_llm_extraction_item_shape(self) -> dict:
        return self._get_llm_extraction_item_type().prompt_json_schema()

    @abc.abstractmethod
    def _get_llm_extraction_item_type(self) -> type[T]:
        pass

    @abc.abstractmethod
    def _get_user_prompt_lines(self) -> list[str]:
        pass

    def _get_fragment_contents(self) -> str:
        with open(self.config.input_dir / self.fragment.source_path) as f:
            lines = f.readlines()
            text = "".join(
                lines[self.fragment.start_line_incl : self.fragment.end_line_excl]
            )
            return text
        pass

    def _get_system_prompt_lines(self) -> list[str]:
        return [
            f"You are {self.config.role_desc}.",
        ]

    def _get_system_prompt(self) -> str:
        return "\n".join(self._get_system_prompt_lines())

    def _get_user_prompt(self) -> str:
        return "\n".join(self._get_user_prompt_lines())

    def _llm_extraction(self) -> list[BaseModel]:
        system_prompt = self._get_system_prompt()
        user_prompt = self._get_user_prompt()
        response_type = self._get_llm_extraction_item_type()

        extraction_item_shape = self._get_llm_extraction_item_shape()

        res = services.llm_api.completion(
            req_name="extract",
            system=system_prompt,
            user=user_prompt,
            output_schema={
                "type": "object",
                # "required": ["extractions"],
                "properties": {
                    "extractions": {
                        "type": "array",
                        "items": extraction_item_shape,
                        "description": "Extractions derived from text",
                    },
                },
            },
        )
        assert res.structured_output
        return [
            response_type.model_validate(row)
            for row in res.structured_output["extractions"]
        ]

    def _post_process(self, extractions: list[T]) -> list[T]:
        return extractions

    def extract(self) -> list[T]:
        return self._post_process(
            cast(list[T], self._llm_extraction()),
        )

    pass
