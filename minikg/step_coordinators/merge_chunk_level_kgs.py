import logging

from minikg.build_steps.base_step import MiniKgBuilderStep
from minikg.build_steps.step_extract_chunk_kg import Step_ExtractChunkKg
from minikg.build_steps.step_merge_kgs import Step_MergeKgs
from minikg.step_coordinators.base import StepCoordinator


class StepCoordinator_MergeChunkLevelKgs(StepCoordinator):
    def get_required_step_types(self) -> list[type[MiniKgBuilderStep]]:
        return [Step_ExtractChunkKg]

    def get_step_type(self) -> type[Step_MergeKgs]:
        return Step_MergeKgs

    def get_steps_to_execute(
        self,
        *,
        steps_ExtractChunkKg: list[Step_ExtractChunkKg],
        **kwargs,
    ) -> list[Step_MergeKgs]:
        graphs_to_merge = [step.output for step in steps_ExtractChunkKg]
        return [
            Step_MergeKgs(
                self.config,
                graphs=graphs_to_merge,
            )
        ]

    pass
