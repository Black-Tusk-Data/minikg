import networkx as nx


# TODO TEST
from minikg.build_output import BuildStepOutput_CommunitySummary


def get_prompt_context_lines_for_graph(G: nx.Graph) -> list[str]:
    if not G.nodes:
        return []
    node_sections: list[str] = []
    for node_id in G.nodes:
        node_data = G.nodes[node_id]
        lines = [
            " ".join([node_data["entity_type"], node_id]),
            node_data["description"],
        ]
        for v in G.neighbors(node_id):
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
    *, community_id: str, summary_output: BuildStepOutput_CommunitySummary
) -> list[str]:
    lines: list[str] = [f"Community {community_id}"]
    for attr, summary in summary_output.data.items():
        lines.append(f" - {attr}: {summary}")
        pass
    return lines
