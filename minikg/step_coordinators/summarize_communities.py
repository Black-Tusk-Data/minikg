from collections import deque
import logging

from minikg.build_output import BuildStepOutput_CommunitySummary
from minikg.build_steps.base_step import MiniKgBuilderStep
from minikg.build_steps.step_define_communities import Step_DefineCommunities
from minikg.build_steps.step_extract_chunk_kg import Step_ExtractChunkKg
from minikg.build_steps.step_split_doc import Step_SplitDoc
from minikg.build_steps.step_summarize_community import Step_SummarizeCommunity
from minikg.graphtools.community_summaries import get_community_summary_compute_order
from minikg.models import Community
from minikg.step_coordinators.base import StepCoordinator


class StepCoordinator_SummarizeCommunities(StepCoordinator):
    communities_by_id: dict[str, Community] = {}
    summaries_by_id: dict[str, BuildStepOutput_CommunitySummary] = {}
    summary_compute_order: deque[list[str]] = deque()
    step_DefineCommunities: Step_DefineCommunities | None = None

    def get_required_step_types(self) -> list[type[MiniKgBuilderStep]]:
        return [Step_DefineCommunities]

    def get_step_type(self) -> type[Step_SummarizeCommunity]:
        return Step_SummarizeCommunity

    def get_steps_to_execute(
        self,
        *,
        steps_DefineCommunities: list[Step_DefineCommunities],
        **kwargs,
    ) -> list[Step_SummarizeCommunity]:
        if not self.config.summary_prompts:
            return []

        # we only handle a single one of these right now
        assert len(steps_DefineCommunities) == 1
        self.step_DefineCommunities = steps_DefineCommunities[0]

        for community in self.step_DefineCommunities.get_output().communities:
            self.communities_by_id[community.id] = community
            pass

        self.summary_compute_order.extend(
            get_community_summary_compute_order(
                self.step_DefineCommunities.get_output()
            )
        )

        first_stage = self.summary_compute_order.popleft()
        return [
            Step_SummarizeCommunity(
                self.config,
                community=self.communities_by_id[community_id],
                community_summaries=self.summaries_by_id,
                graph_output=self.step_DefineCommunities.graph,
            )
            for community_id in first_stage
        ]

    def iterate_on_steps(
        self, executed_steps_this_coordinator: list[Step_SummarizeCommunity], **kwargs
    ) -> list[Step_SummarizeCommunity]:
        assert self.step_DefineCommunities

        if not self.config.summary_prompts:
            return []
        if not self.summary_compute_order:
            return []

        for step in executed_steps_this_coordinator:
            assert step.output  # typing
            self.summaries_by_id[step.community.id] = step.output
            pass

        stage = self.summary_compute_order.popleft()
        return [
            Step_SummarizeCommunity(
                self.config,
                community=self.communities_by_id[community_id],
                community_summaries=self.summaries_by_id,
                graph_output=self.step_DefineCommunities.graph,
            )
            for community_id in stage
        ]

    pass
