"""CLI와 독립적인 저장소 기능 검증"""

import unittest

from mini_git.repository import Repository, RepositoryError


class RepositoryTests(unittest.TestCase):
    def setUp(self) -> None:
        self.repository = Repository()

    def test_operations_require_initialization(self) -> None:
        operations = [
            lambda: self.repository.create_branch("feature"),
            lambda: self.repository.switch("main"),
            lambda: self.repository.commit("root"),
            lambda: self.repository.merge("feature"),
            lambda: self.repository.log(),
            lambda: self.repository.path("a", "b"),
            lambda: self.repository.ancestors("a"),
            lambda: self.repository.search("root"),
        ]
        for operation in operations:
            with self.subTest(operation=operation):
                with self.assertRaises(RepositoryError) as caught:
                    operation()
                self.assertEqual(caught.exception.code, "not_initialized")
        self.assertEqual(self.repository.graph.commits, {})

    def test_reinitialize_clears_all_data_but_preserves_hash_uniqueness(self) -> None:
        self.repository.initialize("Alice")
        first = self.repository.commit("root")
        self.repository.create_branch("feature")
        self.repository.initialize("Alice")
        self.assertEqual(self.repository.branches, {"main": None})
        self.assertEqual(self.repository.graph.commits, {})
        self.assertEqual(self.repository.graph.children, {})
        self.assertEqual(self.repository.index.keyword_to_hashes, {})
        self.assertEqual(self.repository.index.author_to_hashes, {})
        second = self.repository.commit("root")
        self.assertNotEqual(first.hash, second.hash)
        self.assertEqual(second.parents, ())

    def test_merge_updates_graph_index_and_only_current_branch(self) -> None:
        repository = self.repository
        repository.initialize("Alice")
        root = repository.commit("root")
        repository.create_branch("feature")
        main = repository.commit("main work")
        repository.switch("feature")
        feature = repository.commit("feature work")
        merged = repository.merge("main")
        self.assertEqual(merged.parents, (feature.hash, main.hash))
        self.assertEqual(repository.branches, {"main": main.hash, "feature": merged.hash})
        self.assertEqual(repository.head, merged.hash)
        self.assertEqual(repository.search("merge"), [merged])
        self.assertIn(merged, repository.search("ALICE", by_author=True))
        self.assertEqual(repository.ancestors(merged.hash), [root, main, feature])
        self.assertEqual(repository.path(feature.hash, main.hash), [feature.hash, root.hash, main.hash])

    def test_domain_errors_preserve_state(self) -> None:
        repository = self.repository
        repository.initialize("Alice")
        root = repository.commit("root")
        repository.create_branch("same")
        failures = [
            (lambda: repository.initialize(" "), "invalid_args", ""),
            (lambda: repository.create_branch("main"), "invalid_args", ""),
            (lambda: repository.commit(" "), "invalid_args", ""),
            (lambda: repository.switch("missing"), "unknown_branch", "missing"),
            (lambda: repository.merge("same"), "invalid_args", ""),
            (lambda: repository.merge("missing"), "unknown_branch", "missing"),
            (lambda: repository.path("missing", root.hash), "unknown_commit", "missing"),
            (lambda: repository.ancestors("missing"), "unknown_commit", "missing"),
            (lambda: repository.log("invalid"), "invalid_args", ""),
        ]
        for operation, code, detail in failures:
            with self.subTest(code=code, detail=detail):
                with self.assertRaises(RepositoryError) as caught:
                    operation()
                self.assertEqual((caught.exception.code, caught.exception.detail), (code, detail))
                self.assertEqual(repository.log(), [root])
                self.assertEqual(repository.head, root.hash)
                self.assertEqual(repository.search("root"), [root])
        self.assertEqual(repository.commit("next").hash[:8], "00000002")
