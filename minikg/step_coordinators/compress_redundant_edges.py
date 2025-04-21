import logging

from minikg.build_steps.base_step import MiniKgBuilderStep
from minikg.build_steps.step_apply_edges_to_entities import Step_ApplyEdgesToEntities
from minikg.build_steps.step_compress_kg_edges import Step_CompressRedundantEdges
from minikg.build_steps.step_merge_kgs import Step_MergeKgs
from minikg.step_coordinators.apply_edges_to_entities import (
    StepCoordinator_ApplyEdgesToEntities,
)
from minikg.step_coordinators.base import StepCoordinator


class StepCoordinator_CompressRedundantEdges(StepCoordinator):
    def get_required_step_types(self) -> list[type[MiniKgBuilderStep]]:
        return [Step_ApplyEdgesToEntities]

    def get_step_type(self) -> type[Step_CompressRedundantEdges]:
        return Step_CompressRedundantEdges

    def get_steps_to_execute(
        self,
        *,
        steps_ApplyEdgesToEntities: list[StepCoordinator_ApplyEdgesToEntities],
        **kwargs,
    ) -> list[Step_CompressRedundantEdges]:
        return [
            Step_CompressRedundantEdges(
                self.config,
                graph=step.output,
            )
            for step in steps_ApplyEdgesToEntities
        ]

    pass
