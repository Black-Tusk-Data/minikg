import networkx as nx

from minikg.build_steps.base_step import MiniKgBuilderStep
from minikg.models import BuildStepOutput_Graph, MiniKgConfig


class Step_MergeKgs(MiniKgBuilderStep[BuildStepOutput_Graph]):
    def __init__(
            self,
            config: MiniKgConfig,
            *,
            graphA: BuildStepOutput_Graph,
            graphB: BuildStepOutput_Graph,
    ) -> None:
        super().__init__(config)
        self.graphA = graphA
        self.graphB = graphB
        return

    def get_id(self) -> str:
        return super().get_id()

    @staticmethod
    def get_output_type():
        return BuildStepOutput_Graph


    def _execute(self):
        # merge nodes
        # merge edges

        graph_label = f"merged-{self.graphA.label}-with-{self.graphB.label}"
        self.output = BuildStepOutput_Graph(
            G=nx.Graph(),
            label=graph_label,
        )
        return
    pass
