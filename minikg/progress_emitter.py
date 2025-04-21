import abc


class ProgressEmitter(abc.ABC):
    @abc.abstractmethod
    def step_transition(
        self,
        *,
        new_step_name: str,
        n_steps: int,
    ) -> None:
        pass

    @abc.abstractmethod
    def step_is_iterating(
        self,
        step_name: str,
        n_steps: int,
    ) -> None:
        pass

    pass
