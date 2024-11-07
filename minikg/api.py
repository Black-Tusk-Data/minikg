from collections import deque
from concurrent.futures import ProcessPoolExecutor
from concurrent.futures import ThreadPoolExecutor
import logging
import os
from pathlib import Path
from typing import Generic, TypeVar

from minikg.build_steps.base_step import MiniKgBuilderStep
from minikg.build_steps.step_extract_chunk_kg import Step_ExtractChunkKg
from minikg.build_steps.step_merge_kgs import Step_MergeKgs
from minikg.build_steps.step_split_doc import Step_SplitDoc
from minikg.models import MiniKgConfig


DEBUG = bool(int(os.environ.get("DEBUG", 0)))
if DEBUG:
    logging.warning("EXECUTING IN DEBUG MODE")
    pass


T = TypeVar("T", bound=MiniKgBuilderStep)

def execute_step(step: T) -> T:
    step.execute()
    return step


class StepExecutor(Generic[T]):
    MAX_CONCURRENCY = 5         # arbitrary

    def __init__(
            self,
            config: MiniKgConfig,
    ):
        self.config = config
        return

    def execute_all(self, steps: list[T]) -> list[T]:
        if not steps:
            return []
        logging.debug(
            "executing %d steps of type %s",
            len(steps),
            steps[0].__class__.__name__,
        )
        if DEBUG:
            for step in steps:
                return [
                    execute_step(step)
                    for step in steps
                ]
            pass
        with ProcessPoolExecutor(max_workers=self.MAX_CONCURRENCY) as ex:
            completed_steps = list(ex.map(execute_step, steps))
            return completed_steps
        pass


class Api:
    def __init__(
            self,
            *,
            config: MiniKgConfig,
    ):
        self.config = config
        self.executor = StepExecutor(config)
        for dirpath in [
                config.persist_dir,
        ]:
            if not dirpath.exists():
                os.makedirs(dirpath)
                pass
            pass
        return

    def _gather_input_files(self) -> list[Path]:
        return list(self.config.input_dir.rglob(
            self.config.input_file_exp
        ))
        # return [
        #     path.relative_to(self.config.input_dir)
        #     for path in self.config.input_dir.rglob(
        #             self.config.input_file_exp
        #     )
        # ]

    def build_kg(self) -> None:
        source_paths = self._gather_input_files()
        logging.info("found %d source files", len(source_paths))

        logging.info("splitting documents")
        # split docs
        split_doc_steps = [
            Step_SplitDoc(
                self.config,
                doc_path=doc_path
            )
            for doc_path in source_paths
        ]
        split_doc_steps = self.executor.execute_all(split_doc_steps)

        logging.info("extracting chunk-level knowledge graphs")
        extract_chunk_kg_steps = [
            Step_ExtractChunkKg(
                self.config,
                fragment=fragment
            )
            for split_doc in split_doc_steps
            for fragment in split_doc.output.chunks
        ]
        extract_chunk_kg_steps = self.executor.execute_all(extract_chunk_kg_steps)

        logging.info("merging knowledge graphs")
        graphs_to_merge = [
            step.output
            for step in extract_chunk_kg_steps
            if step.output      # for typing
        ]
        merge_step = Step_MergeKgs(
            self.config,
            graphs=graphs_to_merge,
        )
        self.executor.execute_all([merge_step])

        print("DONE FOR NOW!")

        # build community KG
        return

    def update_kg(
            self,
            source_paths: list[Path],
    ) -> None:
        return

    pass
