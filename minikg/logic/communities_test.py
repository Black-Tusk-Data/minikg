import unittest

from minikg.logic.communities import get_communites_hierarchy
from minikg.models import Community


class Test_get_communites_hierarchy(unittest.TestCase):

    def _assert_levels_equal(self, actual: list[list[str]], target: list[list[str]]):
        self.assertListEqual(
            [set(level) for level in target],
            [set(level) for level in actual],
        )
        return

    def test_one_level(self):
        self._assert_levels_equal(
            get_communites_hierarchy(
                [
                    Community(
                        id="1",
                        child_community_ids=[],
                        child_node_ids=[],
                    ),
                    Community(
                        id="2",
                        child_community_ids=[],
                        child_node_ids=[],
                    ),
                    Community(
                        id="3",
                        child_community_ids=[],
                        child_node_ids=[],
                    ),
                ]
            ),
            [["1", "2", "3"]],
        )
        return

    def test_two_levels(self):
        self._assert_levels_equal(
            get_communites_hierarchy(
                [
                    Community(
                        id="1",
                        child_community_ids=["2", "3"],
                        child_node_ids=[],
                    ),
                    Community(
                        id="2",
                        child_community_ids=[],
                        child_node_ids=[],
                    ),
                    Community(
                        id="3",
                        child_community_ids=[],
                        child_node_ids=[],
                    ),
                ]
            ),
            [
                ["1"],
                ["2", "3"],
            ],
        )
        self._assert_levels_equal(
            get_communites_hierarchy(
                [
                    Community(
                        id="1",
                        child_community_ids=["3"],
                        child_node_ids=[],
                    ),
                    Community(
                        id="2",
                        child_community_ids=["3"],
                        child_node_ids=[],
                    ),
                    Community(
                        id="3",
                        child_community_ids=[],
                        child_node_ids=[],
                    ),
                ]
            ),
            [
                ["1", "2"],
                ["3"],
            ],
        )
        return

    def test_three_levels(self):
        self._assert_levels_equal(
            get_communites_hierarchy(
                [
                    Community(
                        id="1",
                        child_community_ids=["2"],
                        child_node_ids=[],
                    ),
                    Community(
                        id="2",
                        child_community_ids=["3"],
                        child_node_ids=[],
                    ),
                    Community(
                        id="3",
                        child_community_ids=[],
                        child_node_ids=[],
                    ),
                ]
            ),
            [
                ["1"],
                ["2"],
                ["3"],
            ],
        )
        return

    def test_mixed_levels(self):
        self._assert_levels_equal(
            get_communites_hierarchy(
                [
                    Community(
                        id="1",
                        child_community_ids=["2"],
                        child_node_ids=[],
                    ),
                    Community(
                        id="2",
                        child_community_ids=[],
                        child_node_ids=[],
                    ),
                    Community(
                        id="3",
                        child_community_ids=["1"],
                        child_node_ids=[],
                    ),
                    Community(
                        id="4",
                        child_community_ids=["2"],
                        child_node_ids=[],
                    ),
                    Community(
                        id="5",
                        child_community_ids=[],
                        child_node_ids=[],
                    ),
                ]
            ),
            [
                ["3", "4", "5"],
                ["2", "1"],
            ],
        )
        return

    pass
