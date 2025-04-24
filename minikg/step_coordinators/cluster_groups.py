from collections import deque
import logging

from minikg.build_output import BuildStepOutput_CommunitySummary
from minikg.build_steps.base_step import MiniKgBuilderStep
from minikg.build_steps.step_cluster_groups import Step_ClusterGroups
from minikg.build_steps.step_define_communities import Step_DefineCommunities
from minikg.build_steps.step_extract_chunk_kg import Step_ExtractChunkKg
from minikg.build_steps.step_split_doc import Step_SplitDoc
from minikg.build_steps.step_summarize_community import Step_SummarizeCommunity
from minikg.graphtools.community_summaries import get_community_summary_compute_order
from minikg.logic.communities import get_communites_hierarchy
from minikg.models import Community, Group
from minikg.step_coordinators.base import StepCoordinator


class StepCoordinator_ClusterGroups(StepCoordinator):
    communities_by_id: dict[str, Community] = {}
    summaries_by_id: dict[str, BuildStepOutput_CommunitySummary] = {}
    summary_compute_order: deque[list[str]] = deque()

    def get_required_step_types(self) -> list[type[MiniKgBuilderStep]]:
        return [Step_SummarizeCommunity]

    def get_step_type(self) -> type[Step_ClusterGroups]:
        return Step_ClusterGroups

    def get_steps_to_execute(
        self,
        *,
        # steps_DefineCommunities: list[Step_DefineCommunities],
        steps_SummarizeCommunity: list[Step_SummarizeCommunity],
        **kwargs,
    ) -> list[Step_SummarizeCommunity]:
        if not self.config.summary_prompts:
            return []

        # our initial groups are just the top-level communities
        top_level_com_ids = get_communites_hierarchy(
            [step.community for step in steps_SummarizeCommunity]
        )[0]
        coms_by_id = {
            step.community.id: step.community for step in steps_SummarizeCommunity
        }
        com_summaries_by_id = {
            step.community.id: step.get_output().data
            for step in steps_SummarizeCommunity
        }
        top_level_communities: list[Community] = [
            coms_by_id[com_id] for com_id in top_level_com_ids
        ]

        return [
            Step_ClusterGroups(
                self.config,
                groups=[
                    Group(
                        group_id=com.id,
                        child_community_ids=com.child_community_ids,
                        child_group_ids=[],
                        summary=com_summaries_by_id[com.id],
                    )
                    for com in top_level_communities
                ],
                clustering_round=0,
            )
        ]

    def iterate_on_steps(
        self, executed_steps_this_coordinator: list[Step_ClusterGroups], **kwargs
    ) -> list[Step_ClusterGroups]:
        last_step = executed_steps_this_coordinator[-1]
        last_step_groups = last_step.get_output().groups
        if len(last_step_groups) <= 1:
            return []
        return [
            Step_ClusterGroups(
                self.config,
                groups=last_step_groups,
                clustering_round=len(executed_steps_this_coordinator),
            )
        ]

    pass
