import logging
from pathlib import Path
from minikg.build_steps.base_step import MiniKgBuilderStep
from minikg.build_steps.step_apply_edges_to_entities import Step_ApplyEdgesToEntities
from minikg.build_steps.step_identify_edges import Step_IdentifyEdges
from minikg.build_steps.step_identify_entities import Step_IdentifyEntities
from minikg.models import EntityWithFragment
from minikg.step_coordinators.base import StepCoordinator


class StepCoordinator_ApplyEdgesToEntities(StepCoordinator):
    def get_required_step_types(self) -> list[type[MiniKgBuilderStep]]:
        return [Step_IdentifyEntities, Step_IdentifyEdges]

    def get_step_type(self) -> type[Step_ApplyEdgesToEntities]:
        return Step_ApplyEdgesToEntities

    def get_steps_to_execute(
        self,
        *,
        steps_IdentifyEdges: list[Step_IdentifyEdges],
        steps_IdentifyEntities: list[Step_IdentifyEntities],
        **kwargs,
    ) -> list[Step_ApplyEdgesToEntities]:
        entities = [
            entity for step in steps_IdentifyEntities for entity in step.output.entities
        ]
        edges = [edge for step in steps_IdentifyEdges for edge in step.output.edges]
        return [
            Step_ApplyEdgesToEntities(
                self.config,
                edges=edges,
                entities=entities,
            )
        ]

    pass
