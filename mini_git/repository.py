"""Repository state and operations, independent of CLI parsing and output."""

from __future__ import annotations

import hashlib
from datetime import datetime

from .graph import CommitGraph
from .index import InvertedIndex
from .models import Commit
from .sorting import compare_author, compare_date, merge_sort


class RepositoryError(ValueError):
    """A domain failure for the caller to translate into user-facing output."""

    def __init__(self, code: str, detail: str = "") -> None:
        super().__init__(code, detail)
        self.code = code
        self.detail = detail


class Repository:
    """Manage branches and keep commits, indexes, and HEAD in sync."""

    def __init__(self) -> None:
        self.graph = CommitGraph()
        self.index = InvertedIndex()
        self.branches: dict[str, str | None] = {}
        self.current_branch: str | None = None
        self.author: str | None = None
        self._commit_counter = 0

    @property
    def initialized(self) -> bool:
        """Whether a user and current branch have been configured."""

        return self.author is not None and self.current_branch is not None

    @property
    def head(self) -> str | None:
        """Return the current branch tip, if present."""

        return None if self.current_branch is None else self.branches[self.current_branch]

    def require_initialized(self) -> None:
        """Reject operations before repository initialization."""

        if not self.initialized:
            raise RepositoryError("not_initialized")

    def _require_commit(self, commit_hash: str) -> None:
        if commit_hash not in self.graph.commits:
            raise RepositoryError("unknown_commit", commit_hash)

    def initialize(self, author: str) -> None:
        """Reset repository data while preserving the session hash counter."""

        if not author.strip():
            raise RepositoryError("invalid_args")
        self.graph.clear()
        self.index.clear()
        self.branches = {"main": None}
        self.current_branch = "main"
        self.author = author

    def create_branch(self, name: str) -> None:
        """Create a branch at HEAD, rejecting empty or duplicate names."""

        self.require_initialized()
        if not name.strip() or name in self.branches:
            raise RepositoryError("invalid_args")
        self.branches[name] = self.head

    def switch(self, name: str) -> None:
        """Select an existing branch without changing its tip."""

        self.require_initialized()
        if name not in self.branches:
            raise RepositoryError("unknown_branch", name)
        self.current_branch = name

    def _new_hash(self, message: str, parents: tuple[str, ...]) -> str:
        """Create a session-unique hash with a monotonic prefix."""

        self._commit_counter += 1
        unique_prefix = f"{self._commit_counter:08x}"
        payload = f"{unique_prefix}\0{self.author}\0{message}\0{'|'.join(parents)}"
        digest = hashlib.sha256(payload.encode("utf-8")).hexdigest()[:8]
        return f"{unique_prefix}{digest}"

    def _create_commit(self, message: str, parents: tuple[str, ...]) -> Commit:
        commit = Commit(
            hash=self._new_hash(message, parents),
            message=message,
            author=self.author or "",
            timestamp=datetime.now(),
            parents=parents,
        )
        self.graph.add(commit)
        self.index.add(commit)
        if self.current_branch is not None:
            self.branches[self.current_branch] = commit.hash
        return commit

    def commit(self, message: str) -> Commit:
        """Create a commit at HEAD and update all repository references."""

        self.require_initialized()
        if not message.strip():
            raise RepositoryError("invalid_args")
        parents = () if self.head is None else (self.head,)
        return self._create_commit(message, parents)

    def merge(self, target_branch: str) -> Commit:
        """Create a two-parent commit from distinct, nonempty branch tips."""

        self.require_initialized()
        if target_branch not in self.branches:
            raise RepositoryError("unknown_branch", target_branch)
        current_head = self.head
        target_head = self.branches[target_branch]
        if (
            target_branch == self.current_branch
            or current_head is None
            or target_head is None
            or current_head == target_head
        ):
            raise RepositoryError("invalid_args")
        return self._create_commit(
            f"Merge branch '{target_branch}'", (current_head, target_head)
        )

    def log(self, sort_by: str | None = None) -> list[Commit]:
        """Return parent-first commits or an explicitly sorted commit list."""

        self.require_initialized()
        if sort_by is None:
            return self.graph.topological_order()
        comparators = {"date": compare_date, "author": compare_author}
        if sort_by not in comparators:
            raise RepositoryError("invalid_args")
        return merge_sort(self.graph.commits.values(), comparators[sort_by])

    def path(self, start: str, end: str) -> list[str] | None:
        """Return the shortest undirected path between existing commits."""

        self.require_initialized()
        self._require_commit(start)
        self._require_commit(end)
        return self.graph.shortest_path(start, end)

    def ancestors(self, commit_hash: str) -> list[Commit]:
        """Return unique ancestors in parent-first order."""

        self.require_initialized()
        self._require_commit(commit_hash)
        return self.graph.ancestors(commit_hash)

    def search(self, query: str, *, by_author: bool = False) -> list[Commit]:
        """Return indexed keyword, phrase, or author matches."""

        self.require_initialized()
        if not query.strip():
            raise RepositoryError("invalid_args")
        hashes = (
            self.index.search_author(query)
            if by_author
            else self.index.search_keyword(query, self.graph.commits)
        )
        return [self.graph.commits[commit_hash] for commit_hash in hashes]
