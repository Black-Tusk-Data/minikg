import logging

from minikg.build_steps.base_step import MiniKgBuilderStep
from minikg.build_steps.step_apply_edges_to_entities import Step_ApplyEdgesToEntities
from minikg.build_steps.step_compress_kg_edges import Step_CompressRedundantEdges
from minikg.build_steps.step_define_communities import Step_DefineCommunities
from minikg.build_steps.step_extract_chunk_kg import Step_ExtractChunkKg
from minikg.graphtools.community_detection import (
    CommunityDetector,
    CommunityDetectorLeiden,
    CommunityDetectorLouvain,
)
from minikg.step_coordinators.base import StepCoordinator


class StepCoordinator_DetectCommunities(StepCoordinator):
    def _get_community_detection_algorithm(self) -> CommunityDetector:
        if self.config.community_algorithm == "leiden":
            return CommunityDetectorLeiden()
        return CommunityDetectorLouvain()

    def get_required_step_types(self) -> list[type[MiniKgBuilderStep]]:
        return [
            # Step_CompressRedundantEdges,
            Step_ApplyEdgesToEntities,
        ]

    def get_step_type(self) -> type[Step_DefineCommunities]:
        return Step_DefineCommunities

    def get_steps_to_execute(
        self,
        *,
        steps_ApplyEdgesToEntities: list[Step_ApplyEdgesToEntities],
        # steps_CompressRedundantEdges: list[Step_CompressRedundantEdges],
        **kwargs,
    ) -> list[Step_DefineCommunities]:
        community_detection_algo = self._get_community_detection_algorithm()
        logging.info(
            "using community detection algo %s",
            community_detection_algo.__class__.__name__,
        )
        return [
            Step_DefineCommunities(
                self.config,
                graph=step.output,
                community_detector=community_detection_algo,
            )
            for step in steps_ApplyEdgesToEntities
            if step.output
        ]

    pass
