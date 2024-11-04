from collections import deque
from concurrent.futures import ProcessPoolExecutor
import logging
import os
from pathlib import Path

from minikg.build_steps.base_step import MiniKgBuilderStep
from minikg.build_steps.step_extract_chunk_kg import Step_ExtractChunkKg
from minikg.build_steps.step_merge_kgs import Step_MergeKgs
from minikg.build_steps.step_split_doc import Step_SplitDoc
from minikg.models import MiniKgConfig


class StepExecutor:
    MAX_CONCURRENCY = 5         # arbitrary

    def __init__(
            self,
            config: MiniKgConfig,
    ):
        self.config = config
        return

    def execute_all(self, steps: list[MiniKgBuilderStep]):
        with ProcessPoolExecutor(max_workers=self.MAX_CONCURRENCY) as ex:
            for step in steps:
                ex.submit(lambda: step.execute)
                pass
            pass
        return


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
        return list(
            self.config.input_dir.rglob(
                self.config.input_file_exp
            )
        )

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
        self.executor.execute_all(split_doc_steps)

        logging.info("extracting chunk-level knowledge graphs")
        extract_chunk_kg_steps = [
            Step_ExtractChunkKg(
                self.config,
                fragment=fragment
            )
            for split_doc in split_doc_steps
            for fragment in split_doc.output.chunks
        ]
        self.executor.execute_all(extract_chunk_kg_steps)

        logging.info("merging knowledge graphs")
        graphs_to_merge = deque([
            step.output
            for step in extract_chunk_kg_steps
            if step.output      # for typing
        ])
        while 2 <= len(graphs_to_merge):
            merge_tasks: list[Step_MergeKgs] = []
            while 2 <= len(graphs_to_merge):
                merge_tasks.append(
                    Step_MergeKgs(
                        self.config,
                        graphA=graphs_to_merge.popleft(),
                        graphB=graphs_to_merge.popleft(),
                    )
                )
                pass
            self.executor.execute_all(merge_tasks)
            graphs_to_merge.extend([
                task.output
                for task in merge_tasks
            ])
            pass


        assert len(graphs_to_merge) == 1
        # GET THIS TO WORK UP TO HERE

        # build community KG
        return

    def update_kg(
            self,
            source_paths: list[Path],
    ) -> None:
        return

    pass
