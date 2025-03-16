from minikg.step_coordinators.compress_redundant_edges import (
    StepCoordinator_CompressRedundantEdges,
)
from minikg.step_coordinators.detect_communities import (
    StepCoordinator_DetectCommunities,
)
from minikg.step_coordinators.extract_chunk_level_kgs import (
    StepCoordinator_ExtractChunkLevelKgs,
)
from minikg.step_coordinators.index_communities import StepCoordinator_IndexCommunity
from minikg.step_coordinators.merge_chunk_level_kgs import (
    StepCoordinator_MergeChunkLevelKgs,
)
from minikg.step_coordinators.package import StepCoordinator_Package
from minikg.step_coordinators.split_docs import StepCoordinator_SplitDocs
from minikg.step_coordinators.summarize_communities import (
    StepCoordinator_SummarizeCommunities,
)


STEP_COORDINATOR_ORDER = [
    StepCoordinator_SplitDocs,
    StepCoordinator_ExtractChunkLevelKgs,
    StepCoordinator_MergeChunkLevelKgs,
    StepCoordinator_CompressRedundantEdges,
    StepCoordinator_DetectCommunities,
    StepCoordinator_SummarizeCommunities,
    StepCoordinator_IndexCommunity,
    StepCoordinator_Package,
]
