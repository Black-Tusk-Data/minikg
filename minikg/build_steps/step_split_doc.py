import logging
from pathlib import Path

import networkx as nx

from minikg.build_steps.base_step import MiniKgBuilderStep
from minikg.models import MiniKgConfig
from minikg.splitter import Splitter
from minikg.build_output import (
    BuildStepOutput_Chunks,
    BuildStepOutput_Graph,
    BuildStepOutput_MultiGraph,
)


class Step_SplitDoc(MiniKgBuilderStep[BuildStepOutput_Chunks]):
    def __init__(
        self,
        config: MiniKgConfig,
        *,
        doc_path: Path,
    ) -> None:
        super().__init__(config)
        self.doc_path = doc_path
        self.splitter = Splitter(config=config)
        return

    def get_id(self) -> str:
        return str(self.doc_path).replace("/", "_")

    @staticmethod
    def get_output_type():
        return BuildStepOutput_Chunks

    def _execute(self) -> BuildStepOutput_Chunks:
        chunks = self.splitter.split_file(self.doc_path)
        logging.debug(
            "split %s into %d chunks",
            self.doc_path,
            len(chunks),
        )
        return BuildStepOutput_Chunks(chunks=chunks)

    pass
