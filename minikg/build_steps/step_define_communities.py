from pathlib import Path
from typing import Type

import networkx as nx

from minikg.build_steps.base_step import MiniKgBuilderStep
from minikg.models import MiniKgConfig
from minikg.build_output import (
    BuildStepOutput_Graph,
    BuildStepOutput_MultiGraph,
    BuildStepOutput_Communities,
)


class Step_DefineCommunitiesLouvain(MiniKgBuilderStep[BuildStepOutput_Communities]):
    def __init__(
        self,
        config: MiniKgConfig,
        *,
        graph: BuildStepOutput_MultiGraph,
    ) -> None:
        super().__init__(config)
        self.graph = graph
        return

    def get_id(self) -> str:
        return self.graph.label

    @staticmethod
    def get_output_type() -> Type[BuildStepOutput_Communities]:
        return BuildStepOutput_Communities

    def _execute(self) -> BuildStepOutput_Communities:
        communities: list[set[str]] = nx.community.louvain_communities(self.graph.G)
        return BuildStepOutput_Communities(
            [list(community) for community in communities]
        )

    pass


# TODO: Leiden algorithm
