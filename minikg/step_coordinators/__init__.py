from minikg.step_coordinators.apply_edges_to_entities import (
    StepCoordinator_ApplyEdgesToEntities,
)
from minikg.step_coordinators.cluster_groups import StepCoordinator_ClusterGroups
from minikg.step_coordinators.detect_communities import (
    StepCoordinator_DetectCommunities,
)
from minikg.step_coordinators.identify_edges import StepCoordinator_IdentifyEdges
from minikg.step_coordinators.identify_entities import StepCoordinator_IdentifyEntities
from minikg.step_coordinators.package import StepCoordinator_Package
from minikg.step_coordinators.summarize_communities import (
    StepCoordinator_SummarizeCommunities,
)

STEP_COORDINATOR_ORDER = [
    StepCoordinator_IdentifyEntities,
    StepCoordinator_IdentifyEdges,
    StepCoordinator_ApplyEdgesToEntities,
    StepCoordinator_DetectCommunities,
    StepCoordinator_SummarizeCommunities,
    StepCoordinator_ClusterGroups,
    StepCoordinator_Package,
]
