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
    def _get_output_shape(self) -> Type[BaseModel]:
        pass

    @abc.abstractmethod
    def _get_system_prompt_lines(self) -> list[str]:
        pass

    @abc.abstractmethod
    def _get_user_prompt_lines(self) -> list[str]:
        pass

    def _get_system_prompt(self) -> str:
        return "\n".join(self._get_system_prompt_lines())

    def _get_user_prompt(self) -> str:
        return "\n".join(self._get_user_prompt_lines())

    def _run_extraction(self) -> list[BaseModel]:
        system_prompt = self._get_system_prompt()
        user_prompt = self._get_user_prompt()
        # TODO: run this through a structured completion, the result of which is the list[S]
        res = []
        return res

    def _reshape_output(self, raw: BaseModel) -> T:
        """Override as necessary to reshape the LLM output."""
        return cast(T, raw)

    def extract(self) -> list[T]:
        return [
            self._reshape_output(row)
            for row in self._run_extraction()
        ]

    pass
