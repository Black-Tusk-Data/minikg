import logging
from minikg.build_steps.base_step import MiniKgBuilderStep
from minikg.build_steps.step_identify_entities import Step_IdentifyEntities
from minikg.logic.path import get_all_input_files
from minikg.step_coordinators.base import StepCoordinator


class StepCoordinator_IdentifyEntities(StepCoordinator):
    def get_required_step_types(self) -> list[type[MiniKgBuilderStep]]:
        return []

    def get_step_type(self) -> type[Step_IdentifyEntities]:
        return Step_IdentifyEntities

    def get_steps_to_execute(
        self,
        **kwargs,
    ) -> list[Step_IdentifyEntities]:
        source_paths = get_all_input_files(self.config)
        logging.info("found %d source files", len(source_paths))
        return [
            Step_IdentifyEntities(
                self.config,
                file_path=path,
            )
            for path in source_paths
        ]

    pass
