import logging

from minikg.build_steps.base_step import MiniKgBuilderStep
from minikg.build_steps.step_extract_chunk_kg import Step_ExtractChunkKg
from minikg.build_steps.step_split_doc import Step_SplitDoc
from minikg.step_coordinators.base import StepCoordinator


class StepCoordinator_ExtractChunkLevelKgs(StepCoordinator):
    def get_required_step_types(self) -> list[type[MiniKgBuilderStep]]:
        return [Step_SplitDoc]

    def get_step_type(self) -> type[Step_ExtractChunkKg]:
        return Step_ExtractChunkKg

    def get_steps_to_execute(
        self,
        *,
        steps_SplitDoc: list[Step_SplitDoc],
        **kwargs,
    ) -> list[Step_ExtractChunkKg]:
        return [
            Step_ExtractChunkKg(self.config, fragment=fragment)
            for split_doc in steps_SplitDoc
            for fragment in split_doc.output.chunks
            if split_doc.output
        ]

    pass
