import networkx as nx


def flatten_multigraph(G: nx.MultiGraph) -> nx.Graph:
    flat_G = nx.Graph()
    flat_G.add_nodes_from(G.nodes)

    # TODO: iss-5
    for u, v, _weight in G.edges:
        flat_G.add_edge(u, v)
        pass

    return flat_G
