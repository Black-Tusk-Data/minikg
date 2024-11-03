from pathlib import Path
from minikg.builder.base_step import MiniKgBuilderStep
from minikg.models import MiniKgConfig


class Step_MergeKgs(MiniKgBuilderStep[None]):
    def __init__(
            self,
            config: MiniKgConfig,
            *,
            graphA,
            graphB
    ) -> None:
        super().__init__(config)
        self.graphA = graphA
        self.graphB = graphB
        return

    def _execute(self):
        # merge nodes
        # merge edges
        return
    pass
