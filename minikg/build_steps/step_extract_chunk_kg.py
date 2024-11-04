from pathlib import Path

import networkx as nx

from minikg.build_steps.base_step import MiniKgBuilderStep
from minikg.models import BuildStepOutput_Graph, FileFragment, MiniKgConfig


class Step_ExtractChunkKg(MiniKgBuilderStep[BuildStepOutput_Graph]):
    def __init__(
            self,
            config: MiniKgConfig,
            *,
            fragment: FileFragment
    ) -> None:
        super().__init__(config)
        self.fragment = fragment
        return

    def get_id(self) -> str:
        return self.fragment.fragment_id

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
