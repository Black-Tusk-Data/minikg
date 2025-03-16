import logging

from minikg.build_steps.base_step import MiniKgBuilderStep
from minikg.build_steps.step_compress_kg_edges import Step_CompressRedundantEdges
from minikg.build_steps.step_define_communities import Step_DefineCommunities
from minikg.build_steps.step_extract_chunk_kg import Step_ExtractChunkKg
from minikg.build_steps.step_index_community import Step_IndexCommunity
from minikg.build_steps.step_merge_kgs import Step_MergeKgs
from minikg.build_steps.step_package import Step_Package
from minikg.build_steps.step_summarize_community import Step_SummarizeCommunity
from minikg.step_coordinators.base import StepCoordinator


class StepCoordinator_Package(StepCoordinator):
    def get_required_step_types(self) -> list[type[MiniKgBuilderStep]]:
        return [
            Step_CompressRedundantEdges,
            Step_DefineCommunities,
            Step_IndexCommunity,
            Step_SummarizeCommunity,
        ]

    def get_step_type(self) -> type[Step_Package]:
        return Step_Package

    def get_steps_to_execute(
        self,
        *,
        steps_CompressRedundantEdges: list[Step_CompressRedundantEdges],
        steps_DefineCommunities: list[Step_DefineCommunities],
        steps_IndexCommunity: list[Step_IndexCommunity],
        steps_SummarizeCommunity: list[Step_SummarizeCommunity],
        **kwargs,
    ) -> list[Step_Package]:
        assert len(steps_CompressRedundantEdges) == 1
        return [
            Step_Package(
                self.config,
                master_graph=steps_CompressRedundantEdges[0].output,
                communities=steps_DefineCommunities[0].output,
                community_indexes=[
                    step.output for step in steps_IndexCommunity if step.output
                ],
                communitiy_summaries=[
                    step.output for step in steps_SummarizeCommunity if step.output
                ],
            )
        ]

    pass
