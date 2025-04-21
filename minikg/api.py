import os
from pathlib import Path

from minikg.build_output import (
    BuildStepOutput_Package,
)
from minikg.build_steps.base_step import MiniKgBuilderStep
from minikg.build_steps.step_package import Step_Package
from minikg.models import MiniKgConfig
from minikg.progress_emitter import ProgressEmitter
from minikg.step_coordinators import STEP_COORDINATOR_ORDER
from minikg.step_executor import StepExecutor


class Api:

    def __init__(
        self,
        *,
        config: MiniKgConfig,
        progress_emitter: ProgressEmitter | None = None,
    ):
        self.config = config
        self.progress_emitter = progress_emitter
        self.executor = StepExecutor(
            config,
            progress_emitter=self.progress_emitter,
        )
        for dirpath in [
            config.persist_dir,
        ]:
            if not dirpath.exists():
                os.makedirs(dirpath)
                pass
            pass
        self.executed_steps: dict[type[MiniKgBuilderStep], list[MiniKgBuilderStep]] = {}
        return

    def _load_package(self) -> BuildStepOutput_Package:
        return Step_Package.load_from_cache(
            config=self.config,
            instance_id="1",
        )

    def build_kg(self) -> None:
        step_coordinators = [
            coordinator(config=self.config) for coordinator in STEP_COORDINATOR_ORDER
        ]
        self.executor.run_all_coordinators(step_coordinators)
        return

    # TODO
    def update_kg(
        self,
        source_paths: list[Path],
    ) -> None:
        return

    pass
