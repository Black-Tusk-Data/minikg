from pathlib import Path

import numpy as np


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


# TODO: move this to a better home module
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
