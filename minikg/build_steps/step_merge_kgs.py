import base64
from hashlib import md5

import networkx as nx

from minikg.build_steps.base_step import MiniKgBuilderStep
from minikg.graph_merger import GraphMerger
from minikg.models import MiniKgConfig
from minikg.build_output import BuildStepOutput_Graph, BuildStepOutput_MultiGraph


class Step_MergeKgs(MiniKgBuilderStep[BuildStepOutput_MultiGraph]):
    def __init__(
        self,
        config: MiniKgConfig,
        *,
        graphs: list[BuildStepOutput_Graph],
    ) -> None:
        super().__init__(config)
        self.graphs = graphs
        self.merged_id = self._compute_merged_graphs_id()
        return

    def get_id(self) -> str:
        return self.merged_id

    def _compute_merged_graphs_id(self) -> str:
        # these start to get too long, so we'll hash
        md5_hash = md5()
        md5_hash.update(
            ":".join(sorted([graph.label for graph in self.graphs])).encode("utf-8")
        )
        digest = md5_hash.digest()
        return base64.urlsafe_b64encode(digest).decode("utf-8")

    @staticmethod
    def get_output_type():
        return BuildStepOutput_MultiGraph

    def _execute(self) -> BuildStepOutput_MultiGraph:
        merger = GraphMerger(
            self.config,
            graphs=[step.G for step in self.graphs],
        )
        merged_graph = merger.merge()

        graph_label = f"merged-{self.merged_id}"
        return BuildStepOutput_MultiGraph(
            G=merged_graph,
            label=graph_label,
        )

    pass
