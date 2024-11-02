from minikg.models import MiniKgBuildPlanStep, MiniKgConfig


class MiniKgPlanner:
    def __init__(
            self,
            config: MiniKgConfig,
    ):
        self.config = config
        return

    def get_next_steps(
            self,
            *,
            completed_steps: list[MiniKgBuildPlanStep],
    ) -> list[MiniKgBuildPlanStep]:
        return

    pass
