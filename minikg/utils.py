from collections import deque
from pathlib import Path

import networkx as nx
import numpy as np

from minikg.build_output import BuildStepOutput_Communities, BuildStepOutput_CommunitySummary
from minikg.models import Community


def scrub_title_key(d: dict):
    """
    Helpful because pydantic schema dumps include an unecessary 'title' attribute;
    """
    d.pop("title", None)
    if d.get("type") == "object":
        assert "properties" in d
        for prop in d["properties"].keys():
            scrub_title_key(d["properties"][prop])
    return d


def cluster_from_similarities(
    *,
    pairwise_similarities: np.ndarray,
    threshold_similarity: float,
) -> list[list[int]]:
    """
    Returns a list of clusters.
    Each cluster is a list of the indices that belong to that cluster.

    Similarities are assumed to be between 0-1, and any two items
    more similar than 'threshold_similarity' will be assigned to the same cluster.
    """
    A = pairwise_similarities
    n = A.shape[0]
    assert n

    # start with item 0 in its own cluster
    clusters = [[0]]
    index_to_cluster = {
        0: 0,
    }
    for i in range(1, n):
        if i in index_to_cluster:
            # already assigned to a cluster
            continue

        # o/w we look for a place to put it
        for j in range(n):
            if A[i][j] > threshold_similarity and j in index_to_cluster:
                # found a place to put it
                target_cluster = index_to_cluster[j]
                index_to_cluster[i] = target_cluster
                clusters[target_cluster].append(i)
                break
            pass
        else:
            # found no match
            clusters.append([i])
            index_to_cluster[i] = len(clusters) - 1
            pass
        pass

    return clusters


def draw_graph(G, path: Path):
    import pygraphviz as pgv

    G_viz = pgv.AGraph()
    for node in G.nodes:
        G_viz.add_node(
            node,
            label="\n".join(
                [
                    node,
                    G.nodes[node]["entity_type"],
                ]
            ),
        )
        pass
    for edge in G.edges:
        G_viz.add_edge(
            (edge[0], edge[1]),
            label=G.edges[edge]["description"],
        )
        pass

    G_viz.draw(path, prog="dot")
    return


def flatten_multigraph(G: nx.MultiGraph) -> nx.Graph:
   flat_G = nx.Graph()
   flat_G.add_nodes_from(G.nodes)

   # TODO: iss-5
   for u, v, _weight in G.edges:
       flat_G.add_edge(u, v)
       pass

   return flat_G


# TODO TEST
def get_prompt_context_lines_for_graph(G: nx.Graph) -> list[str]:
    if not G.nodes:
        return []
    node_sections: list[str] = []
    for node_id in G.nodes:
        node_data = G.nodes[node_id]
        lines = [
            " ".join([node_data["entity_type"], node_id]),
            node_data.description,
        ]
        for v in G.neighbors(node):
            edge_datas = G.get_edge_data(node_id, v)
            for edge_data in edge_datas.values():
                edge_description = edge_data["description"]
                lines.append(f" - {edge_description}")
                pass
            pass
        lines.append("")
        pass

    return node_sections


def get_prompt_context_lines_for_community_summary(
        *,
        community_id: str,
        summary_output: BuildStepOutput_CommunitySummary
) -> list[str]:
    lines: list[str] = [f"Community {community_id}"]
    for attr, summary in summary_output.data.items():
        lines.append(f" - {attr}: {summary}")
        pass
    return lines


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
