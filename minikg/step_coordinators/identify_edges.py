import logging
from pathlib import Path
from minikg.build_steps.base_step import MiniKgBuilderStep
from minikg.build_steps.step_identify_edges import Step_IdentifyEdges
from minikg.build_steps.step_identify_entities import Step_IdentifyEntities
from minikg.models import EntityWithFragment
from minikg.step_coordinators.base import StepCoordinator


class StepCoordinator_IdentifyEdges(StepCoordinator):
    def get_required_step_types(self) -> list[type[MiniKgBuilderStep]]:
        return [Step_IdentifyEntities]

    def get_step_type(self) -> type[Step_IdentifyEdges]:
        return Step_IdentifyEdges

    def get_steps_to_execute(
        self,
        *,
        steps_IdentifyEntities: list[Step_IdentifyEntities],
        **kwargs,
    ) -> list[Step_IdentifyEdges]:
        entities_by_file_path: dict[Path, list[EntityWithFragment]] = {}
        for entity_step in steps_IdentifyEntities:
            for entity in entity_step.get_output().entities:
                file_path = Path(entity.fragment.source_path)
                if file_path not in entities_by_file_path:
                    entities_by_file_path[file_path] = []
                    pass
                entities_by_file_path[file_path].append(entity)
                pass
            pass

        return [
            Step_IdentifyEdges(
                self.config,
                file_path=path,
                entities_by_file_path=entities_by_file_path,
            )
            for path in entities_by_file_path.keys()
        ]

    pass
