import unittest

import networkx as nx


class Test_Step_DefineCommunitiesLeiden(unittest.TestCase):
    def test_one(self):
        G = nx.MultiGraph()
        G.add_nodes_from(
            [
                "a",
                "b",
                "c",
                "d",
                "e",
                "f",
            ]
        )
        G.add_edges_from([])
        return

    pass
