import logging
from pathlib import Path
import re

from minikg.build_steps.base_step import MiniKgBuilderStep
from minikg.build_steps.step_split_doc import Step_SplitDoc
from minikg.step_coordinators.base import StepCoordinator


class StepCoordinator_SplitDocs(StepCoordinator):
    def _gather_input_files(self) -> list[Path]:
        # this can be its own step, where we check with the LLM if it's a code file or not
        ignore_expressions = [re.compile(rf"{self.config.input_dir}/\.git/?")]
        return [
            path
            for path in self.config.input_dir.rglob(self.config.input_file_exp)
            if not any(expr.search(str(path)) for expr in ignore_expressions)
            and path.is_file()
        ]

    def get_required_step_types(self) -> list[type[MiniKgBuilderStep]]:
        return []

    def get_step_type(self) -> type[Step_SplitDoc]:
        return Step_SplitDoc

    def get_steps_to_execute(self, **kwargs) -> list[Step_SplitDoc]:
        source_paths = self._gather_input_files()
        logging.info("found %d source files", len(source_paths))
        # split docs
        return [
            Step_SplitDoc(self.config, doc_path=doc_path) for doc_path in source_paths
        ]

    pass
