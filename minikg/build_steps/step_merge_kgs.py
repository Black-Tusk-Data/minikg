import networkx as nx

from minikg.build_steps.base_step import MiniKgBuilderStep
from minikg.graph_merger import GraphMerger
from minikg.models import BuildStepOutput_Graph, MiniKgConfig


class Step_MergeKgs(MiniKgBuilderStep[BuildStepOutput_Graph]):
    def __init__(
            self,
            config: MiniKgConfig,
            *,
            graphs: list[BuildStepOutput_Graph],
    ) -> None:
        super().__init__(config)
        self.graphs = graphs
        return

    def get_id(self) -> str:
        return self._get_merged_graphs_id()

    def _get_merged_graphs_id(self) -> str:
        return ":".join(sorted([
            graph.label
            for graph in self.graphs
        ]))

    @staticmethod
    def get_output_type():
        return BuildStepOutput_Graph

    def _execute(self) -> BuildStepOutput_Graph:
        merger = GraphMerger(
            self.config,
            graphs=[step.G for step in self.graphs],
        )
        merged_graph = merger.merge()

        graph_label = f"merged-{self._get_merged_graphs_id()}"
        return BuildStepOutput_Graph(
            G=merged_graph,
            label=graph_label,
        )

    pass
