from pathlib import Path

import networkx as nx

from minikg.build_steps.base_step import MiniKgBuilderStep
from minikg.models import BuildStepOutput_Chunks, BuildStepOutput_Graph, MiniKgConfig
from minikg.splitter import Splitter


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

    def _execute(self):
        chunks = self.splitter.split_file(self.doc_path)
        self.output = BuildStepOutput_Chunks(chunks=chunks)
        return
    pass
