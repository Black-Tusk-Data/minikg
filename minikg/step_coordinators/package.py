from minikg.build_steps.base_step import MiniKgBuilderStep
from minikg.build_steps.step_apply_edges_to_entities import Step_ApplyEdgesToEntities
from minikg.build_steps.step_cluster_groups import Step_ClusterGroups
from minikg.build_steps.step_define_communities import Step_DefineCommunities
from minikg.build_steps.step_package import Step_Package
from minikg.build_steps.step_summarize_community import Step_SummarizeCommunity
from minikg.step_coordinators.base import StepCoordinator


class StepCoordinator_Package(StepCoordinator):
    def get_required_step_types(self) -> list[type[MiniKgBuilderStep]]:
        return [
            Step_ApplyEdgesToEntities,
            Step_DefineCommunities,
            Step_SummarizeCommunity,
            Step_ClusterGroups,
        ]

    def get_step_type(self) -> type[Step_Package]:
        return Step_Package

    def get_steps_to_execute(
        self,
        *,
        steps_ApplyEdgesToEntities: list[Step_ApplyEdgesToEntities],
        steps_DefineCommunities: list[Step_DefineCommunities],
        steps_SummarizeCommunity: list[Step_SummarizeCommunity],
        steps_ClusterGroups: list[Step_ClusterGroups],
        **kwargs,
    ) -> list[Step_Package]:
        assert len(steps_ApplyEdgesToEntities) == 1

        master_graph = steps_ApplyEdgesToEntities[0].output
        assert master_graph
        communities = steps_DefineCommunities[0].output
        assert communities

        return [
            Step_Package(
                self.config,
                master_graph=master_graph,
                communities=communities,
                summaries_by_id={
                    step.community.id: step.output
                    for step in steps_SummarizeCommunity
                    if step.output
                },
                cluster_groups={
                    group.group_id: group
                    for step in steps_ClusterGroups
                    for group in step.get_output().groups
                },
            )
        ]

    pass
