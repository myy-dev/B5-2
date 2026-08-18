"""Automated requirement tests for the Mini Git implementation."""

from __future__ import annotations

import ast
import subprocess
import sys
import tempfile
import unittest
from datetime import datetime
from pathlib import Path

from main import Commit, CommitGraph, MiniGit, insertion_sort, line_diff, merge_sort


class MiniGitTests(unittest.TestCase):
    """Exercise required commands and the underlying algorithms."""

    def setUp(self) -> None:
        self.app = MiniGit()

    def _commit(self, message: str) -> str:
        result = self.app.execute(f'commit "{message}"')
        self.assertTrue(result.startswith("["), result)
        head = self.app.branches[self.app.current_branch or ""]
        self.assertIsNotNone(head)
        return head or ""

    def test_init_is_case_insensitive_and_resets_repository(self) -> None:
        result = self.app.execute('InIt "Alice Kim"')
        self.assertIn("Initialized repository.", result)
        self.assertEqual(self.app.current_branch, "main")
        self.assertEqual(self.app.author, "Alice Kim")
        temporary = self._commit("temporary")
        self.assertIn(temporary, self.app.execute('SEARCH --author="Alice Kim"'))

        self.app.execute("init Bob")
        self.assertEqual(self.app.author, "Bob")
        self.assertEqual(self.app.graph.commits, {})
        self.assertEqual(self.app.branches, {"main": None})

    def test_reinitialization_does_not_reuse_a_session_hash(self) -> None:
        self.app.execute("init Alice")
        first = self._commit("same")
        self.app.execute("init Alice")
        second = self._commit("same")
        self.assertNotEqual(first, second)

    def test_branch_switch_commit_log_and_indexes(self) -> None:
        self.app.execute("init Alice")
        root = self._commit("Initial commit")
        self.assertEqual(self.app.execute("branch feature"), "Created branch: feature")
        self.assertEqual(self.app.execute("switch feature"), "Switched to branch: feature")
        feature = self._commit("Add login feature")
        self.app.execute("switch main")
        main = self._commit("Add payment feature")

        log = self.app.execute("log")
        self.assertLess(log.index(root), log.index(feature))
        self.assertLess(log.index(root), log.index(main))
        self.assertIn("Alice", log)
        self.assertIn("Initial commit", log)
        self.assertIsInstance(self.app.graph.commits[root].timestamp, datetime)
        self.assertEqual(self.app.graph.commits[feature].parents, (root,))
        self.assertEqual(self.app.graph.commits[main].parents, (root,))
        self.assertEqual(self.app.branches["feature"], feature)
        self.assertEqual(self.app.branches["main"], main)
        self.assertIn(feature, self.app.index.keyword_to_hashes["login"])
        self.assertIn(feature, self.app.execute("search login"))
        author_result = self.app.execute("search --author=Alice")
        self.assertIn(root, author_result)
        self.assertIn(feature, author_result)
        self.assertIn(main, author_result)

    def test_quoted_phrase_search_uses_index_candidates(self) -> None:
        self.app.execute("init Alice")
        expected = self._commit("Add login feature now")
        self._commit("Feature without the phrase login")
        result = self.app.execute('search "login feature"')
        self.assertIn(expected, result)
        self.assertEqual(result.count("\n- "), 1)

    def test_log_sort_options_use_stable_manual_sort(self) -> None:
        moment = datetime(2024, 1, 1)
        earlier = datetime(2023, 1, 1)
        commits = [
            Commit("b", "second", "zoe", moment, ()),
            Commit("a", "first", "Amy", earlier, ()),
            Commit("c", "third", "amy", moment, ()),
        ]
        by_author = merge_sort(commits, MiniGit._compare_author)
        self.assertEqual([commit.hash for commit in by_author], ["a", "c", "b"])
        by_date = merge_sort(commits, MiniGit._compare_date)
        self.assertEqual([commit.hash for commit in by_date], ["a", "b", "c"])
        self.assertEqual(insertion_sort([3, 1, 2], MiniGit._compare_number), [1, 2, 3])

        self.app.execute("init Alice")
        self._commit("one")
        self._commit("two")
        self.assertIn("commit", self.app.execute("log --sort-by=date"))
        self.assertIn("commit", self.app.execute("log --sort-by=author"))

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

    def test_disconnected_commits_have_no_path(self) -> None:
        self.app.execute("init Alice")
        self.app.execute("branch island")
        first = self._commit("main root")
        self.app.execute("switch island")
        second = self._commit("island root")
        self.assertEqual(self.app.execute(f"path {first} {second}"), "No path")

    def test_merge_creates_two_parent_commit_and_updates_index(self) -> None:
        self.app.execute("init Alice")
        root = self._commit("root")
        self.app.execute("branch feature")
        main = self._commit("main work")
        self.app.execute("switch feature")
        feature = self._commit("feature work")
        result = self.app.execute("merge main")
        merge_hash = self.app.branches["feature"] or ""

        self.assertIn(merge_hash, result)
        self.assertEqual(self.app.graph.commits[merge_hash].parents, (feature, main))
        ancestor_hashes = [commit.hash for commit in self.app.graph.ancestors(merge_hash)]
        self.assertEqual(set(ancestor_hashes), {root, main, feature})
        self.assertIn(merge_hash, self.app.execute("search Merge"))
        self.assertEqual(self.app.execute("merge feature"), "Invalid args")

        same_head = MiniGit()
        same_head.execute("init Alice")
        same_head.execute("commit root")
        same_head.execute("branch feature")
        self.assertEqual(same_head.execute("merge feature"), "Invalid args")
        self.assertEqual(same_head.execute("merge missing"), "Unknown branch: missing")

    def test_ancestors_and_standard_errors(self) -> None:
        self.app.execute("init Alice")
        root = self._commit("root")
        child = self._commit("child")
        self.assertIn(root, self.app.execute(f"ancestors {child}"))
        self.assertNotIn(child, self.app.execute(f"ancestors {child}"))
        self.assertEqual(self.app.execute("switch missing"), "Unknown branch: missing")
        self.assertEqual(self.app.execute("path missing also-missing"), "Unknown commit: missing")
        self.assertEqual(self.app.execute("commit"), "Invalid args")
        self.assertEqual(self.app.execute("nonsense"), "Invalid args")

    def test_malformed_and_whitespace_only_arguments_are_invalid(self) -> None:
        self.assertEqual(self.app.execute("nonsense"), "Invalid args")
        self.assertEqual(self.app.execute('init "unterminated'), "Invalid args")
        self.app.execute("init Alice")
        self.assertEqual(self.app.execute('branch "   "'), "Invalid args")
        self.assertEqual(self.app.execute('commit "   "'), "Invalid args")
        self.assertEqual(self.app.execute('search "   "'), "Invalid args")
        self.assertEqual(self.app.execute('search --author="   "'), "Invalid args")

    def test_graph_rejects_duplicate_hash_and_unknown_parent(self) -> None:
        graph = CommitGraph()
        moment = datetime(2024, 1, 1)
        root = Commit("root", "root", "A", moment, ())
        graph.add(root)
        with self.assertRaises(ValueError):
            graph.add(root)
        with self.assertRaises(ValueError):
            graph.add(Commit("child", "child", "A", moment, ("missing",)))

    def test_line_diff_marks_common_deleted_and_added_lines(self) -> None:
        self.assertEqual(
            line_diff(["same", "old"], ["same", "new"]),
            ["  same", "- old", "+ new"],
        )
        with tempfile.TemporaryDirectory() as directory:
            old_path = Path(directory) / "old.txt"
            new_path = Path(directory) / "new.txt"
            old_path.write_text("same\nold\n", encoding="utf-8")
            new_path.write_text("same\nnew\n", encoding="utf-8")
            self.app.execute("init Alice")
            result = self.app.execute(f'diff "{old_path}" "{new_path}"')
            self.assertEqual(result, "  same\n- old\n+ new")
            self.assertEqual(
                self.app.execute(f'diff "{old_path}" "{old_path}"'),
                "  same\n  old",
            )
            missing = Path(directory) / "missing.txt"
            self.assertTrue(self.app.execute(f'diff "{missing}" "{new_path}"').startswith("File error:"))

    def test_benchmark_compares_two_algorithms(self) -> None:
        self.app.execute("init Alice")
        result = self.app.execute("benchmark 100")
        self.assertIn("Merge sort:", result)
        self.assertIn("Insertion sort:", result)
        self.assertEqual(self.app.execute("benchmark 0"), "Invalid args")
        self.assertEqual(self.app.execute("benchmark 5001"), "Invalid args")
        self.assertEqual(self.app.execute("benchmark many"), "Invalid args")

    def test_hashes_are_unique_and_parent_references_are_older(self) -> None:
        self.app.execute("init Alice")
        hashes = [self._commit("same") for _ in range(100)]
        self.assertEqual(len(set(hashes)), 100)
        position = {commit.hash: index for index, commit in enumerate(self.app.graph.topological_order())}
        for commit in self.app.graph.commits.values():
            for parent in commit.parents:
                self.assertLess(position[parent], position[commit.hash])

    def test_source_uses_python_310_grammar_and_no_standard_sort_calls(self) -> None:
        source = Path(__file__).with_name("main.py").read_text(encoding="utf-8")
        tree = ast.parse(source, feature_version=(3, 10))
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue
            self.assertFalse(isinstance(node.func, ast.Name) and node.func.id == "sorted")
            self.assertFalse(isinstance(node.func, ast.Attribute) and node.func.attr == "sort")

    def test_repl_entry_point_runs_and_quits(self) -> None:
        project = Path(__file__).resolve().parent
        result = subprocess.run(
            [sys.executable, "main.py"],
            cwd=project,
            input="init Alice\nquit\n",
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0)
        self.assertGreaterEqual(result.stdout.count("mini-git> "), 2)
        self.assertIn("Initialized repository.", result.stdout)


if __name__ == "__main__":
    unittest.main()
