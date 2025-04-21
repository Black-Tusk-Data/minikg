from pathlib import Path
import unittest

from minikg.build_output import BuildStepOutput_Communities
from minikg.graphtools.community_summaries import get_community_summary_compute_order
from minikg.models import Community


class Test_get_community_summary_compute_order(unittest.TestCase):
    def test_one_phase(self):
        order = get_community_summary_compute_order(
            BuildStepOutput_Communities(
                communities=[
                    Community(
                        id="1",
                        child_community_ids=[],
                        child_node_ids=["node1", "node2"],
                    ),
                    Community(
                        id="2",
                        child_community_ids=[],
                        child_node_ids=["node3", "node4"],
                    ),
                    Community(
                        id="3",
                        child_community_ids=[],
                        child_node_ids=["node5", "node6"],
                    ),
                ]
            )
        )
        self.assertEqual(
            order,
            [
                ["1", "2", "3"],
            ],
        )
        return

    def test_two_phases(self):
        order = get_community_summary_compute_order(
            BuildStepOutput_Communities(
                communities=[
                    Community(
                        id="1",
                        child_community_ids=[],
                        child_node_ids=["node1", "node2"],
                    ),
                    Community(
                        id="2",
                        child_community_ids=[],
                        child_node_ids=["node3", "node4"],
                    ),
                    Community(
                        id="3",
                        child_community_ids=[],
                        child_node_ids=["node5", "node6"],
                    ),
                    Community(
                        id="4",
                        child_community_ids=["1", "2"],
                        child_node_ids=[],
                    ),
                    Community(
                        id="5",
                        child_community_ids=["3"],
                        child_node_ids=[],
                    ),
                ]
            )
        )
        self.assertEqual(
            order,
            [
                ["1", "2", "3"],
                ["4", "5"],
            ],
        )
        return

    def test_three_phases(self):
        order = get_community_summary_compute_order(
            BuildStepOutput_Communities(
                communities=[
                    Community(
                        id="1",
                        child_community_ids=[],
                        child_node_ids=["node1", "node2"],
                    ),
                    Community(
                        id="2",
                        child_community_ids=[],
                        child_node_ids=["node3", "node4"],
                    ),
                    Community(
                        id="3",
                        child_community_ids=[],
                        child_node_ids=["node5", "node6"],
                    ),
                    Community(
                        id="4",
                        child_community_ids=["1", "2"],
                        child_node_ids=[],
                    ),
                    Community(
                        id="5",
                        child_community_ids=["3"],
                        child_node_ids=[],
                    ),
                    Community(
                        id="6",
                        child_community_ids=["4", "5"],
                        child_node_ids=[],
                    ),
                ]
            )
        )
        self.assertEqual(
            order,
            [
                ["1", "2", "3"],
                ["4", "5"],
                ["6"],
            ],
        )
        return

    pass


if __name__ == "__main__":
    unittest.main()
