import logging

from minikg.build_steps.base_step import MiniKgBuilderStep
from minikg.build_steps.step_compress_kg_edges import Step_CompressRedundantEdges
from minikg.build_steps.step_extract_chunk_kg import Step_ExtractChunkKg
from minikg.build_steps.step_merge_kgs import Step_MergeKgs
from minikg.step_coordinators.base import StepCoordinator


class StepCoordinator_CompressRedundantEdges(StepCoordinator):
    def get_required_step_types(self) -> list[type[MiniKgBuilderStep]]:
        return [Step_MergeKgs]

    def get_step_type(self) -> type[Step_CompressRedundantEdges]:
        return Step_CompressRedundantEdges

    def get_steps_to_execute(
            self,
            *,
            steps_MergeKgs: list[Step_MergeKgs],
            **kwargs,
    ) -> list[Step_CompressRedundantEdges]:
        return [Step_CompressRedundantEdges(
            self.config,
            graph=step.output,
        ) for step in steps_MergeKgs]
    pass
