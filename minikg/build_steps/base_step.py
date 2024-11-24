import abc
import logging
import os
from pathlib import Path
from typing import Generic, Type, TypeVar

from minikg.models import MiniKgConfig
from minikg.build_output import MiniKgBuildPlanStepOutput


T = TypeVar("T", bound=MiniKgBuildPlanStepOutput)


class MiniKgBuilderStep(Generic[T], abc.ABC):
    def __init__(self, config: MiniKgConfig, *, ignore_cache: bool = False):
        self.config = config
        self.executed = False
        self.output: None | T = None
        self.ignore_cache = ignore_cache
        return

    def _get_cache_output_path(self) -> Path:
        clsname = self.__class__.__name__
        instance_id = self.get_id()
        assert instance_id
        return self.config.persist_dir / clsname / instance_id

    def _write_output_to_cache(self):
        output = self.get_output()
        output_path = self._get_cache_output_path()
        os.makedirs(
            os.path.dirname(output_path),
            exist_ok=True,
        )
        output.to_file(output_path)
        return

    def _get_cached_output(self) -> T | None:
        cached_output_path = self._get_cache_output_path()
        if not cached_output_path.exists():
            return None
        output_type = self.__class__.get_output_type()
        try:
            return output_type.from_file(cached_output_path)
        except Exception as e:
            logging.error(
                "Failed to load cached KG build step from %s: %s", cached_output_path, e
            )
            pass
        return None

    def execute(self) -> None:
        if self.executed:
            this_id = self.get_id()
            raise Exception(f"Step {this_id} has already executed")

        cached_output = self._get_cached_output()
        if not self.ignore_cache and cached_output:
            logging.debug(
                "Using cached %s %s",
                self.__class__.__name__,
                self.get_id(),
            )
            self.output = cached_output
            self.executed = True
            return

        self.output = self._execute()
        self.executed = True
        self._write_output_to_cache()
        return

    def get_output(self) -> T:
        assert self.executed
        assert self.output != None
        return self.output

    @abc.abstractmethod
    def _execute(self) -> T:
        raise NotImplementedError()

    @staticmethod
    @abc.abstractmethod
    def get_output_type() -> Type[T]:
        raise NotImplementedError()

    @abc.abstractmethod
    def get_id(self) -> str:
        """
        A unique identifier for caching.
        Note it must only be unique among classes of the same type.
        """
        raise NotImplementedError()

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

    pass
