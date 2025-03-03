from collections import deque

from minikg.models import Community
from minikg.build_output import BuildStepOutput_Communities


def get_community_summary_compute_order(
        communities_output: BuildStepOutput_Communities,
) -> list[list[str]]:
    """
    Return a list of 'stages', the idea being that each stage depends on the previous stages,
    but can be computed entirely in parallel.
    """
    # first layer communities only have nodes as children
    stages: list[list[str]] = [[]]
    to_summarize: deque[Community] = deque([])
    for community in communities_output.communities:
        if community.child_community_ids:
            to_summarize.append(community)
            pass
        else:
            # only nodes as children!
            stages[0].append(community.id)
            pass
        pass
    available_summaries = set(stages[0])
    while to_summarize:
        stages.append([])
        for i in range(len(to_summarize)):
            community = to_summarize.popleft()
            if all(com_id in available_summaries for com_id in community.child_community_ids):
                # it's computable
                stages[-1].append(community.id)
                pass
            else:
                # try again next round
                to_summarize.append(community)
                pass
            pass
        pass
    return stages
