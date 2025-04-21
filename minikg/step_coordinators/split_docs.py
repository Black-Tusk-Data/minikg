from fnmatch import fnmatch
import logging
from pathlib import Path
import re

from pydantic import config

from minikg.build_steps.base_step import MiniKgBuilderStep
from minikg.build_steps.step_split_doc import Step_SplitDoc
from minikg.logic.path import get_all_input_files
from minikg.step_coordinators.base import StepCoordinator


class StepCoordinator_SplitDocs(StepCoordinator):
    def get_required_step_types(self) -> list[type[MiniKgBuilderStep]]:
        return []

    def get_step_type(self) -> type[Step_SplitDoc]:
        return Step_SplitDoc

    def get_steps_to_execute(self, **kwargs) -> list[Step_SplitDoc]:
        source_paths = get_all_input_files(self.config)
        logging.info("found %d source files", len(source_paths))
        # split docs
        return [
            Step_SplitDoc(self.config, doc_path=doc_path) for doc_path in source_paths
        ]

    pass
