from concurrent.futures import ProcessPoolExecutor
import logging
import os
import time
from typing import TypeVar

from minikg.build_steps.base_step import MiniKgBuilderStep
from minikg.models import MiniKgConfig
from minikg.progress_emitter import ProgressEmitter
from minikg.step_coordinators.base import StepCoordinator

DEBUG = bool(int(os.environ.get("DEBUG", 0)))
if DEBUG:
    logging.warning("EXECUTING IN DEBUG MODE")
    pass

MAX_ATTEMPTS = 5
SLEEP_ON_FAIL_S = 5

T = TypeVar("T", bound=MiniKgBuilderStep)


def execute_step(step: T) -> T:
    step.execute()
    return step


class StepExecutor:
    def __init__(
        self, config: MiniKgConfig, *, progress_emitter: ProgressEmitter | None = None
    ):
        self.config = config
        self.progress_emitter = progress_emitter
        return

    def _execute_all_steps(self, steps: list[T]) -> list[T]:

        if not steps:
            return []
        logging.debug(
            "executing %d steps of type %s",
            len(steps),
            steps[0].__class__.__name__,
        )
        if DEBUG:
            for step in steps:
                return [execute_step(step) for step in steps]
            pass
        with ProcessPoolExecutor(max_workers=self.config.max_concurrency) as ex:
            completed_steps = list(ex.map(execute_step, steps))
            return completed_steps
        pass

    def run_all_coordinators(self, coordinators: list[StepCoordinator]) -> None:
        executed_steps: dict[type[MiniKgBuilderStep], list[MiniKgBuilderStep]] = {}
        for coordinator in coordinators:
            step_kwargs = {}
            for required_step_type in coordinator.get_required_step_types():
                if required_step_type not in executed_steps:
                    logging.error(
                        "coordinator %s depends on step %s, which has not executed yet!",
                        coordinator.__class__.__name__,
                        required_step_type,
                    )
                    raise Exception(f"missing required step '{required_step_type}'")
                _, step_name = required_step_type.__name__.split("Step_", 1)
                step_kwargs[f"steps_{step_name}"] = executed_steps[required_step_type]
                pass
            logging.info("running coordinator %s", coordinator.__class__.__name__)

            step_type = coordinator.get_step_type()
            coordinator_steps = coordinator.get_steps_to_execute(**step_kwargs)

            if self.progress_emitter:
                self.progress_emitter.step_transition(
                    new_step_name=str(step_type),
                    n_steps=len(coordinator_steps),
                )
                pass

            logging.info(
                "running %d steps of type %s", len(coordinator_steps), step_type
            )
            coordinator_steps = self._execute_all_steps(coordinator_steps)
            assert all(step.output for step in coordinator_steps)
            executed_steps[step_type] = coordinator_steps
            # extra
            while True:
                extra_steps = coordinator.iterate_on_steps(
                    executed_steps_this_coordinator=executed_steps[step_type],
                    **step_kwargs,
                )
                if not extra_steps:
                    break

                if self.progress_emitter:
                    self.progress_emitter.step_is_iterating(
                        step_name=str(step_type),
                        n_steps=len(extra_steps),
                    )
                    pass

                logging.info(
                    "iterating on %d steps of type %s", len(extra_steps), step_type
                )
                extra_steps = self._execute_all_steps(extra_steps)
                assert all(step.output for step in extra_steps)
                executed_steps[step_type].extend(extra_steps)
                pass
            pass
        return
