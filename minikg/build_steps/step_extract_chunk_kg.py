from pathlib import Path

import networkx as nx

from minikg.build_steps.base_step import MiniKgBuilderStep
from minikg.models import BuildStepOutput_Graph, MiniKgConfig


class Step_ExtractChunkKg(MiniKgBuilderStep[BuildStepOutput_Graph]):
    def __init__(
            self,
            config: MiniKgConfig,
            *,
            chunk_id: str,
            chunk_contents: str,
    ) -> None:
        super().__init__(config)
        self.chunk_id = chunk_id
        self.chunk_contents = chunk_contents
        return

    def get_id(self) -> str:
        return self.chunk_id

    @staticmethod
    def get_output_type():
        return BuildStepOutput_Graph

    def _execute(self):
        # - read file
        # - run the KG extractor on it
        # - set the output to be a wrapped version of the NetworkX graph that handles reading / writing from disk
        graph_label = f"doc-{self.get_id()}"
        self.output = BuildStepOutput_Graph(
            G=nx.Graph(),
            label=graph_label,
        )
        return
    pass
