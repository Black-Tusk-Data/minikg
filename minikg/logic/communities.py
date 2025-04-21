from collections import deque
from minikg.models import Community


def get_communites_hierarchy(communities: list[Community]) -> list[list[str]]:
    """
    Hierarchy is defined such that communities with no parents appear in the first row,
    their child in the next, and so on (like the levels of a breadth-first-search, for every connected component).
    """
    by_id = {com.id: com for com in communities}

    # first level is everything without a parent
    reffed_by_a_parent: set[str] = set()
    for com in communities:
        for child_com_id in com.child_community_ids:
            reffed_by_a_parent.add(child_com_id)
            pass
        pass

    root_com_ids = set(by_id.keys()).difference(reffed_by_a_parent)
    levels: list[list[str]] = [list(root_com_ids)]
    q = deque(root_com_ids)
    seen = set(root_com_ids)
    while q:
        this_level: list[str] = []
        for _ in range(len(q)):
            cur_id = q.popleft()
            for child_com_id in by_id[cur_id].child_community_ids:
                if child_com_id in seen:
                    continue
                this_level.append(child_com_id)
                q.append(child_com_id)
                seen.add(child_com_id)
                pass
            pass
        if this_level:
            levels.append(this_level)
            pass
        pass

    assert set(com_id for level in levels for com_id in level) == set(
        by_id.keys()
    ), "failed to construct community hierarchy correctly"
    return levels


def get_all_descendant_node_ids(
    communities: dict[str, Community], community_id: str
) -> list[str]:
    descendant_node_ids = set()
    q = deque([communities[community_id]])
    while q:
        for _ in range(len(q)):
            cur = q.popleft()
            for node_id in cur.child_node_ids:
                descendant_node_ids.add(node_id)
                pass
            for com_id in cur.child_community_ids:
                q.append(communities[com_id])
                pass
            pass
        pass
    return list(descendant_node_ids)
