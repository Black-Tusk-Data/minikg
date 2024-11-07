from pathlib import Path
from minikg.build_steps.base_step import MiniKgBuilderStep
from minikg.models import MiniKgConfig


class Step_DefineCommunities(MiniKgBuilderStep[None]):
    def __init__(
        self,
        config: MiniKgConfig,
        *,
        G,
    ) -> None:
        super().__init__(config)
        self.G = G
        return

    def _execute(self):
        # Leiden algorthim
        return

    pass
