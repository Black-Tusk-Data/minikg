import abc
from typing import Generic, TypeVar

from minikg.build_steps.base_step import MiniKgBuilderStep
from minikg.models import MiniKgConfig

T = TypeVar("T", bound=MiniKgBuilderStep)


class StepCoordinator(abc.ABC, Generic[T]):
    def __init__(
        self,
        *,
        config: MiniKgConfig,
    ):
        self.config = config
        return

    @abc.abstractmethod
    def get_required_step_types(self) -> list[type[MiniKgBuilderStep]]:
        pass

    @abc.abstractmethod
    def get_step_type(self) -> type[T]:
        pass

    @abc.abstractmethod
    def get_steps_to_execute(self, **kwargs) -> list[T]:
        pass

    def iterate_on_steps(
        self,
        executed_steps_this_coordinator: list[T],
        **kwargs,
    ) -> list[T]:
        return []

    pass
