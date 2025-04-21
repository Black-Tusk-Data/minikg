import logging
from pathlib import Path
from typing import Type

from minikg.build_steps.base_step import MiniKgBuilderStep
from minikg.graphtools.community_detection import CommunityDetector
from minikg.graphtools.flatten import flatten_multigraph
from minikg.models import Community, MiniKgConfig
from minikg.build_output import (
    BuildStepOutput_Graph,
    BuildStepOutput_MultiGraph,
    BuildStepOutput_Communities,
)


class Step_DefineCommunities(MiniKgBuilderStep[BuildStepOutput_Communities]):
    def __init__(
        self,
        config: MiniKgConfig,
        *,
        graph: BuildStepOutput_MultiGraph,
        community_detector: CommunityDetector,
    ) -> None:
        super().__init__(config)
        self.graph = graph
        self.community_detector = community_detector
        return

    def get_id(self) -> str:
        return self.graph.label

    @staticmethod
    def get_output_type() -> Type[BuildStepOutput_Communities]:
        return BuildStepOutput_Communities

    def _execute(self) -> BuildStepOutput_Communities:
        return BuildStepOutput_Communities(
            self.community_detector.get_communities(self.graph.G)
        )

    pass
