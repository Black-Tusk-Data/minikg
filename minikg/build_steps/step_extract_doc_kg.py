from pathlib import Path

import networkx as nx

from minikg.build_steps.base_step import MiniKgBuilderStep
from minikg.models import BuildStepOutput_Graph, MiniKgConfig


class Step_ExtractDocKg(MiniKgBuilderStep[BuildStepOutput_Graph]):
    def __init__(
            self,
            config: MiniKgConfig,
            *,
            doc_path: Path,
    ) -> None:
        super().__init__(config)
        self.doc_path = doc_path
        return

    def get_id(self) -> str:
        return str(self.doc_path).replace("/", "_")

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
