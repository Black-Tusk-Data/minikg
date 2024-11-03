from pathlib import Path
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
        return
    pass
