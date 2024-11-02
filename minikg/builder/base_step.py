import abc
from typing import Generic, TypeVar
from minikg.models import MiniKgConfig


T = TypeVar("T")

class MiniKgBuilderStep(Generic[T], abc.ABC):
    def __init__(
            self,
            config: MiniKgConfig,
    ):
        self.config = config
        self.executed = False
        self.output: None | T = None
        return

    def execute(self) -> None:
        if self.executed:
            this_id = self.get_id()
            raise Exception(f"Step {this_id} has already executed")
        self._execute()
        pass

    def get_output(self) -> T:
        assert self.executed
        assert self.output != None
        return self.output

    @abc.abstractmethod
    def _execute(self) -> None:
        pass

    @abc.abstractmethod
    def get_id(self) -> str:
        """
        A unique identifier for caching.
        """
        pass

    @classmethod
    def load_from_raw(cls: type["MiniKgBuilderStep"], raw: bytes) -> "MiniKgBuilderStep":
        loaded = cls._load_from_raw(raw)
        loaded.executed = True
        return loaded

    @abc.abstractmethod
    @classmethod
    def _load_from_raw(cls: type["MiniKgBuilderStep"], raw: bytes) -> "MiniKgBuilderStep":
        pass

    @abc.abstractmethod
    @staticmethod
    def dump_output_to_raw() -> bytes:
        pass

    pass
