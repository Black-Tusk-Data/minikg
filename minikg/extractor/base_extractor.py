import abc
from typing import Generic, Type, TypeVar, cast

from pydantic import BaseModel

from minikg.models import FileFragment, MiniKgConfig


T = TypeVar("T")
# S = TypeVar("S", bound=BaseModel)

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

    @abc.abstractmethod
    def _get_llm_output_shape(self) -> dict:
        pass

    @abc.abstractmethod
    def _get_user_prompt_lines(self) -> list[str]:
        pass

    def _get_fragment_contents(self) -> str:
        with open(self.fragment.source_path) as f:
            lines = f.readlines()
            text = "".join(lines[
                self.fragment.start_line_incl:
                self.fragment.end_line_excl
            ])
            return text
        pass

    def _get_system_prompt_lines(self) -> list[str]:
        return [
            f"You are a {self.config.knowledge_domain} expert.",
        ]

    def _get_system_prompt(self) -> str:
        return "\n".join(self._get_system_prompt_lines())

    def _get_user_prompt(self) -> str:
        return "\n".join(self._get_user_prompt_lines())

    def _llm_extraction(self) -> list[BaseModel]:
        system_prompt = self._get_system_prompt()
        user_prompt = self._get_user_prompt()
        # TODO: run this through a structured completion, the result of which is the list[S]
        res = []
        return res

    def extract(self) -> list[T]:
        """Override as necessary."""
        return cast(list[T], self._llm_extraction())

    pass
