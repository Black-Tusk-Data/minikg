import logging
import time
from typing import Type

from btdcore.utils import batched
import networkx as nx

from minikg.build_output import (
    BuildStepOutput_Communities,
    BuildStepOutput_IndexedCommunity,
    BuildStepOutput_MultiGraph,
    BuildStepOutput_Package,
)
from minikg.build_steps.base_step import MiniKgBuilderStep
from minikg.graph_semantic_db import GraphSemanticDb
from minikg.models import Edge, MiniKgConfig, Node


class Step_Package(MiniKgBuilderStep[BuildStepOutput_Package]):
    def __init__(
        self,
        config: MiniKgConfig,
        *,
        master_graph: BuildStepOutput_MultiGraph,
        communities: BuildStepOutput_Communities,
        community_indexes: list[BuildStepOutput_IndexedCommunity],
        # TODO: iss-1
        community_names: list[str],
    ):
        super().__init__(config)
        self.communities = communities
        self.master_graph = master_graph
        self.community_indexes = community_indexes
        self.community_names = community_names
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
            communities=self.communities.communities,
            community_db_names=[idx.semantic_db_name for idx in self.community_indexes],
            community_names=self.community_names,
        )

    pass
