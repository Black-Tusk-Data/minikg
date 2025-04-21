import logging

from minikg.build_steps.base_step import MiniKgBuilderStep
from minikg.build_steps.step_define_communities import Step_DefineCommunities
from minikg.build_steps.step_extract_chunk_kg import Step_ExtractChunkKg
from minikg.build_steps.step_index_community import Step_IndexCommunity
from minikg.build_steps.step_split_doc import Step_SplitDoc
from minikg.step_coordinators.base import StepCoordinator


class StepCoordinator_IndexCommunity(StepCoordinator):
    def get_required_step_types(self) -> list[type[MiniKgBuilderStep]]:
        return [Step_DefineCommunities]

    def get_step_type(self) -> type[Step_IndexCommunity]:
        return Step_IndexCommunity

    def get_steps_to_execute(
        self,
        *,
        steps_DefineCommunities: list[Step_DefineCommunities],
        **kwargs,
    ) -> list[Step_IndexCommunity]:
        if not self.config.index_graph:
            return []
        assert len(steps_DefineCommunities) == 1
        step_DefineCommunities = steps_DefineCommunities[0]
        return [
            Step_IndexCommunity(
                self.config,
                master_graph=step_DefineCommunities.graph,
                community=community,
            )
            for i, community in enumerate(step_DefineCommunities.output.communities)
        ]

    pass
