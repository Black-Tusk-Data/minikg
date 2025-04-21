import logging
from typing import Type

from minikg.build_output import (
    BuildStepOutput_Communities,
    BuildStepOutput_CommunitySummary,
    BuildStepOutput_Groups,
    BuildStepOutput_MultiGraph,
    BuildStepOutput_Package,
)
from minikg.build_steps.base_step import MiniKgBuilderStep
from minikg.logic.communities import get_communites_hierarchy
from minikg.models import Group, MiniKgConfig


class Step_Package(MiniKgBuilderStep[BuildStepOutput_Package]):
    def __init__(
        self,
        config: MiniKgConfig,
        *,
        master_graph: BuildStepOutput_MultiGraph,
        communities: BuildStepOutput_Communities,
        summaries_by_id: dict[str, BuildStepOutput_CommunitySummary],
        cluster_groups: list[Group],
    ):
        super().__init__(config)
        self.communities = communities
        self.master_graph = master_graph
        self.summaries_by_id = summaries_by_id
        self.cluster_groups = cluster_groups
        return

    @staticmethod
    def get_output_type() -> Type[BuildStepOutput_Package]:
        return BuildStepOutput_Package

    def get_id(self) -> str:
        return str(self.config.version)

    def _execute(self) -> BuildStepOutput_Package:
        logging.info("packaging knowledge graph...")
        return BuildStepOutput_Package(
            G=self.master_graph.G,
            communities={com.id: com for com in self.communities.communities},
            community_db_names=[],
            community_hierarchy=get_communites_hierarchy(self.communities.communities),
            summaries_by_id={
                community_id: output.data
                for community_id, output in self.summaries_by_id.items()
            },
            cluster_groups=self.cluster_groups,
        )

    pass
