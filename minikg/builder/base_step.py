import abc
from typing import Generic, TypeVar
from minikg.models import MiniKgBuildPlanStepOutput, MiniKgConfig


T = TypeVar("T", bound=MiniKgBuildPlanStepOutput)

class MiniKgBuilderStep(Generic[T], abc.ABC):
    def __init__(
            self,
            config: MiniKgConfig,
    ):
        self.config = config
        self.executed = False
        self.output: None | T = None
        return

    def _write_output_to_cache(self):
        output = self.get_output()
        clsname = self.__class__.__name__
        output_path = self.config.persist_dir / clsname / self.get_id()
        with open(output_path, "wb") as f:
            f.write(output.to_raw())
            pass
        return

    def execute(self) -> None:
        if self.executed:
            this_id = self.get_id()
            raise Exception(f"Step {this_id} has already executed")
        self._execute()
        self._write_output_to_cache()
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
    def load_from_output(
            cls: type["MiniKgBuilderStep"],
            *,
            output: MiniKgBuildPlanStepOutput,
            config: MiniKgConfig,
    ) -> "MiniKgBuilderStep":
        loaded = cls(config)
        loaded.output = output
        loaded.executed = True
        return loaded

    # @abc.abstractmethod
    # @classmethod
    # def _load_from_raw(cls: type["MiniKgBuilderStep"], raw: bytes) -> "MiniKgBuilderStep":
    #     pass

    # @abc.abstractmethod
    # @staticmethod
    # def dump_output_to_raw() -> bytes:
    #     pass

    pass
