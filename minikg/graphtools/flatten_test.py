from pathlib import Path
import unittest

import networkx as nx

from minikg.build_output import BuildStepOutput_Communities
from minikg.graphtools.flatten import flatten_multigraph
from minikg.models import Community


class Test_flatten(unittest.TestCase):
    def test_one(self):
        multi_G = nx.MultiGraph()
        multi_G.add_nodes_from(
            [
                "A",
                "B",
                "C",
                "D",
            ]
        )
        multi_G.add_edges_from(
            [
                ("A", "B"),
                ("A", "B"),
                ("A", "B"),
                ("B", "C"),
                ("B", "C"),
                ("C", "D"),
                ("A", "D"),
            ]
        )
        self.assertEqual(
            len(multi_G.edges),
            7,
        )
        flat_G = flatten_multigraph(multi_G)
        self.assertEqual(
            len(flat_G.edges),
            4,
        )
        self.assertEqual(
            list(sorted(flat_G.nodes)),
            ["A", "B", "C", "D"],
        )
        self.assertEqual(
            list(sorted(flat_G.edges, key=lambda tup: f"{tup[0]}-{tup[1]}")),
            [
                ("A", "B"),
                ("A", "D"),
                ("B", "C"),
                ("C", "D"),
            ],
        )
        return

    pass


if __name__ == "__main__":
    unittest.main()
