"""그래프 및 정렬 알고리즘 검증"""

import unittest
from datetime import datetime

from mini_git.graph import CommitGraph
from mini_git.models import Commit
from mini_git.sorting import bubble_sort, merge_sort


class AlgorithmTests(unittest.TestCase):
    def test_shortest_path_uses_undirected_edges_and_lexical_tie_break(self) -> None:
        graph = CommitGraph()
        moment = datetime(2024, 1, 1)
        graph.add(Commit("a", "root", "A", moment, ()))
        graph.add(Commit("b", "left", "A", moment, ("a",)))
        graph.add(Commit("c", "right", "A", moment, ("a",)))
        graph.add(Commit("d", "merge", "A", moment, ("b", "c")))

        self.assertEqual(graph.shortest_path("b", "c"), ["b", "a", "c"])
        self.assertEqual(
            [commit.hash for commit in graph.ancestors("d")],
            ["a", "b", "c"],
        )

    def test_graph_rejects_duplicate_hash_and_unknown_parent(self) -> None:
        graph = CommitGraph()
        moment = datetime(2024, 1, 1)
        root = Commit("root", "root", "A", moment, ())
        graph.add(root)
        with self.assertRaises(ValueError):
            graph.add(root)
        with self.assertRaises(ValueError):
            graph.add(Commit("child", "child", "A", moment, ("missing",)))

    def test_sorts_are_stable_and_preserve_input(self) -> None:
        values = [(2, "first"), (1, "middle"), (2, "last")]
        expected = [(1, "middle"), (2, "first"), (2, "last")]
        def compare(left, right):
            return (left[0] > right[0]) - (left[0] < right[0])
        for algorithm in (merge_sort, bubble_sort):
            with self.subTest(algorithm=algorithm.__name__):
                original = list(values)
                self.assertEqual(algorithm(values, compare), expected)
                self.assertEqual(values, original)
