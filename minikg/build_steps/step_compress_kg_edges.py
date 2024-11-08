import networkx as nx

from minikg.build_steps.base_step import MiniKgBuilderStep
from minikg.graph_edge_compressor import GraphEdgeCompressor
from minikg.graph_merger import GraphMerger
from minikg.models import BuildStepOutput_Graph, BuildStepOutput_MultiGraph, MiniKgConfig


class Step_CompressRedundantEdges(MiniKgBuilderStep[BuildStepOutput_MultiGraph]):
    def __init__(
        self,
        config: MiniKgConfig,
        *,
        graph: BuildStepOutput_Graph,
    ) -> None:
        super().__init__(config)
        self.graph = graph
        return

    def get_id(self) -> str:
        return f"compressed-redundant:{self.graph.label}"

    @staticmethod
    def get_output_type():
        return BuildStepOutput_MultiGraph

    def _execute(self) -> BuildStepOutput_MultiGraph:
        compressor = GraphEdgeCompressor(self.config, G=self.graph.G)
        compressed_graph = compressor.compress_redundant()

        return BuildStepOutput_MultiGraph(
            G=compressed_graph,
            label=self.get_id(),
        )

    pass
