"""A small, in-memory Git-like CLI for studying graphs and algorithms."""

from __future__ import annotations

import hashlib
import heapq
import shlex
import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Callable, Iterable, TypeVar


T = TypeVar("T")
Comparator = Callable[[T, T], int]


@dataclass(frozen=True)
class Commit:
    """A commit node whose parent edges always point to older commits."""

    hash: str
    message: str
    author: str
    timestamp: datetime
    parents: tuple[str, ...]


def merge_sort(items: Iterable[T], compare: Comparator[T]) -> list[T]:
    """Return a stable merge-sorted list without using a standard sorting API."""

    values = list(items)
    if len(values) < 2:
        return values

    middle = len(values) // 2
    left = merge_sort(values[:middle], compare)
    right = merge_sort(values[middle:], compare)
    merged: list[T] = []
    left_index = 0
    right_index = 0

    while left_index < len(left) and right_index < len(right):
        if compare(left[left_index], right[right_index]) <= 0:
            merged.append(left[left_index])
            left_index += 1
        else:
            merged.append(right[right_index])
            right_index += 1

    merged.extend(left[left_index:])
    merged.extend(right[right_index:])
    return merged


def insertion_sort(items: Iterable[T], compare: Comparator[T]) -> list[T]:
    """Return a stable insertion-sorted list for benchmark comparison."""

    values = list(items)
    for index in range(1, len(values)):
        current = values[index]
        position = index - 1
        while position >= 0 and compare(values[position], current) > 0:
            values[position + 1] = values[position]
            position -= 1
        values[position + 1] = current
    return values


class InvertedIndex:
    """Map normalized message tokens and authors to commit hash postings."""

    def __init__(self) -> None:
        self.keyword_to_hashes: dict[str, list[str]] = {}
        self.author_to_hashes: dict[str, list[str]] = {}

    @staticmethod
    def _tokens(text: str) -> list[str]:
        return [token.lower() for token in text.split() if token]

    def clear(self) -> None:
        """Remove every posting when a repository is reinitialized."""

        self.keyword_to_hashes.clear()
        self.author_to_hashes.clear()

    def add(self, commit: Commit) -> None:
        """Index one commit, adding a hash only once for each message token."""

        seen_tokens: set[str] = set()
        for token in self._tokens(commit.message):
            if token in seen_tokens:
                continue
            seen_tokens.add(token)
            self.keyword_to_hashes.setdefault(token, []).append(commit.hash)

        author_key = commit.author.lower()
        self.author_to_hashes.setdefault(author_key, []).append(commit.hash)

    def search_keyword(self, query: str, commits: dict[str, Commit]) -> list[str]:
        """Find token or phrase matches from postings, never scanning all commits."""

        tokens = self._tokens(query)
        if not tokens:
            return []

        first_postings = self.keyword_to_hashes.get(tokens[0], [])
        if len(tokens) == 1:
            return list(first_postings)

        remaining_postings = []
        for token in tokens[1:]:
            postings = self.keyword_to_hashes.get(token)
            if postings is None:
                return []
            remaining_postings.append(set(postings))

        normalized_query = query.lower()
        matches: list[str] = []
        for commit_hash in first_postings:
            if all(commit_hash in postings for postings in remaining_postings):
                if normalized_query in commits[commit_hash].message.lower():
                    matches.append(commit_hash)
        return matches

    def search_author(self, author: str) -> list[str]:
        """Return a copy of the posting list for a normalized author name."""

        return list(self.author_to_hashes.get(author.lower(), []))


class CommitGraph:
    """Store commits by hash and provide graph traversal algorithms."""

    def __init__(self) -> None:
        self.commits: dict[str, Commit] = {}
        self.children: dict[str, list[str]] = {}

    def clear(self) -> None:
        """Remove all nodes and adjacency information."""

        self.commits.clear()
        self.children.clear()

    def add(self, commit: Commit) -> None:
        """Add a new node after validating its hash and parent references."""

        if commit.hash in self.commits:
            raise ValueError("duplicate commit hash")
        for parent in commit.parents:
            if parent not in self.commits:
                raise ValueError("unknown parent commit")

        self.commits[commit.hash] = commit
        self.children[commit.hash] = []
        for parent in commit.parents:
            self.children[parent].append(commit.hash)

    def topological_order(self) -> list[Commit]:
        """Use Kahn's algorithm so every parent appears before its children."""

        indegree = {commit_hash: 0 for commit_hash in self.commits}
        for commit in self.commits.values():
            indegree[commit.hash] = len(commit.parents)

        available = [commit_hash for commit_hash, degree in indegree.items() if degree == 0]
        heapq.heapify(available)
        result: list[Commit] = []

        while available:
            commit_hash = heapq.heappop(available)
            result.append(self.commits[commit_hash])
            for child in self.children[commit_hash]:
                indegree[child] -= 1
                if indegree[child] == 0:
                    heapq.heappush(available, child)

        if len(result) != len(self.commits):
            raise RuntimeError("commit graph contains a cycle")
        return result

    def shortest_path(self, start: str, end: str) -> list[str] | None:
        """Find the shortest undirected path, breaking ties lexicographically."""

        if start == end:
            return [start]

        queue: list[tuple[int, tuple[str, ...], str]] = [(0, (start,), start)]
        best: dict[str, tuple[int, tuple[str, ...]]] = {start: (0, (start,))}

        while queue:
            distance, path, current = heapq.heappop(queue)
            if best.get(current) != (distance, path):
                continue
            if current == end:
                return list(path)

            neighbors = set(self.commits[current].parents)
            neighbors.update(self.children[current])
            for neighbor in neighbors:
                candidate = (distance + 1, path + (neighbor,))
                previous = best.get(neighbor)
                if previous is None or candidate < previous:
                    best[neighbor] = candidate
                    heapq.heappush(queue, (candidate[0], candidate[1], neighbor))

        return None

    def ancestors(self, commit_hash: str) -> list[Commit]:
        """Return every reachable ancestor once, in parent-before-child order."""

        discovered: set[str] = set()
        stack = list(self.commits[commit_hash].parents)
        while stack:
            current = stack.pop()
            if current in discovered:
                continue
            discovered.add(current)
            stack.extend(self.commits[current].parents)

        return [commit for commit in self.topological_order() if commit.hash in discovered]


def line_diff(old_lines: list[str], new_lines: list[str]) -> list[str]:
    """Build a line diff using a longest-common-subsequence dynamic program."""

    old_count = len(old_lines)
    new_count = len(new_lines)
    lengths = [[0] * (new_count + 1) for _ in range(old_count + 1)]

    for old_index in range(old_count - 1, -1, -1):
        for new_index in range(new_count - 1, -1, -1):
            if old_lines[old_index] == new_lines[new_index]:
                lengths[old_index][new_index] = lengths[old_index + 1][new_index + 1] + 1
            else:
                skip_old = lengths[old_index + 1][new_index]
                skip_new = lengths[old_index][new_index + 1]
                lengths[old_index][new_index] = max(skip_old, skip_new)

    result: list[str] = []
    old_index = 0
    new_index = 0
    while old_index < old_count and new_index < new_count:
        if old_lines[old_index] == new_lines[new_index]:
            result.append(f"  {old_lines[old_index]}")
            old_index += 1
            new_index += 1
        elif lengths[old_index + 1][new_index] >= lengths[old_index][new_index + 1]:
            result.append(f"- {old_lines[old_index]}")
            old_index += 1
        else:
            result.append(f"+ {new_lines[new_index]}")
            new_index += 1

    while old_index < old_count:
        result.append(f"- {old_lines[old_index]}")
        old_index += 1
    while new_index < new_count:
        result.append(f"+ {new_lines[new_index]}")
        new_index += 1
    return result


class MiniGit:
    """Manage repository state and dispatch parsed CLI commands."""

    def __init__(self) -> None:
        self.graph = CommitGraph()
        self.index = InvertedIndex()
        self.branches: dict[str, str | None] = {}
        self.current_branch: str | None = None
        self.author: str | None = None
        self._commit_counter = 0

    @property
    def initialized(self) -> bool:
        """Whether INIT has configured this in-memory repository."""

        return self.author is not None and self.current_branch is not None

    def _head(self) -> str | None:
        if self.current_branch is None:
            return None
        return self.branches[self.current_branch]

    def _new_hash(self, message: str, parents: tuple[str, ...]) -> str:
        """Create a session-unique readable hash with a monotonic prefix."""

        self._commit_counter += 1
        unique_prefix = f"{self._commit_counter:08x}"
        payload = f"{unique_prefix}\0{self.author}\0{message}\0{'|'.join(parents)}"
        digest = hashlib.sha256(payload.encode("utf-8")).hexdigest()[:8]
        return f"{unique_prefix}{digest}"

    def _create_commit(self, message: str, parents: tuple[str, ...]) -> Commit:
        timestamp = datetime.now()
        commit = Commit(
            hash=self._new_hash(message, parents),
            message=message,
            author=self.author or "",
            timestamp=timestamp,
            parents=parents,
        )
        self.graph.add(commit)
        self.index.add(commit)
        if self.current_branch is not None:
            self.branches[self.current_branch] = commit.hash
        return commit

    @staticmethod
    def _compare_date(left: Commit, right: Commit) -> int:
        left_key = (left.timestamp, left.hash)
        right_key = (right.timestamp, right.hash)
        return (left_key > right_key) - (left_key < right_key)

    @staticmethod
    def _compare_author(left: Commit, right: Commit) -> int:
        left_key = (left.author.lower(), left.timestamp, left.hash)
        right_key = (right.author.lower(), right.timestamp, right.hash)
        return (left_key > right_key) - (left_key < right_key)

    def _branch_labels(self, commit_hash: str) -> str:
        names = [name for name, target in self.branches.items() if target == commit_hash]
        if not names:
            return ""
        return f" [{' '.join(names)}]"

    def _format_commits(self, commits: Iterable[Commit], show_branches: bool = False) -> str:
        blocks: list[str] = []
        for commit in commits:
            timestamp = commit.timestamp.strftime("%Y-%m-%d %H:%M:%S.%f")
            labels = self._branch_labels(commit.hash) if show_branches else ""
            blocks.append(
                f"commit {commit.hash} ({commit.author}, {timestamp}){labels}\n{commit.message}"
            )
        return "\n\n".join(blocks) if blocks else "No commits."

    def _require_initialized(self) -> str | None:
        return None if self.initialized else "Repository not initialized."

    def execute(self, line: str) -> str:
        """Parse and execute one command, returning text for the REPL."""

        try:
            parts = shlex.split(line)
        except ValueError:
            return "Invalid args"
        if not parts:
            return "Invalid args"

        command = parts[0].lower()
        args = parts[1:]

        if command == "init":
            return self._init(args)
        if command in {"exit", "quit"}:
            return "__EXIT__" if not args else "Invalid args"

        handlers = {
            "branch": self._branch,
            "switch": self._switch,
            "commit": self._commit,
            "log": self._log,
            "path": self._path,
            "ancestors": self._ancestors,
            "search": self._search,
            "diff": self._diff,
            "merge": self._merge,
            "benchmark": self._benchmark,
        }
        handler = handlers.get(command)
        if handler is None:
            return "Invalid args"

        error = self._require_initialized()
        if error is not None:
            return error
        return handler(args)

    def _init(self, args: list[str]) -> str:
        if len(args) != 1 or not args[0].strip():
            return "Invalid args"
        self.graph.clear()
        self.index.clear()
        self.branches = {"main": None}
        self.current_branch = "main"
        self.author = args[0]
        return (
            "Initialized repository.\n"
            "Current branch: main\n"
            f"Current user: {self.author}"
        )

    def _branch(self, args: list[str]) -> str:
        if len(args) != 1 or not args[0].strip() or args[0] in self.branches:
            return "Invalid args"
        branch_name = args[0]
        self.branches[branch_name] = self._head()
        return f"Created branch: {branch_name}"

    def _switch(self, args: list[str]) -> str:
        if len(args) != 1:
            return "Invalid args"
        branch_name = args[0]
        if branch_name not in self.branches:
            return f"Unknown branch: {branch_name}"
        self.current_branch = branch_name
        return f"Switched to branch: {branch_name}"

    def _commit(self, args: list[str]) -> str:
        if len(args) != 1 or not args[0].strip():
            return "Invalid args"
        head = self._head()
        parents = () if head is None else (head,)
        commit = self._create_commit(args[0], parents)
        return f"[{self.current_branch} {commit.hash}] {commit.message}"

    def _log(self, args: list[str]) -> str:
        if not args:
            return self._format_commits(self.graph.topological_order(), show_branches=True)
        if len(args) != 1:
            return "Invalid args"

        option = args[0].lower()
        commits = list(self.graph.commits.values())
        if option == "--sort-by=date":
            commits = merge_sort(commits, self._compare_date)
        elif option == "--sort-by=author":
            commits = merge_sort(commits, self._compare_author)
        else:
            return "Invalid args"
        return self._format_commits(commits)

    def _unknown_commit(self, commit_hash: str) -> str | None:
        if commit_hash not in self.graph.commits:
            return f"Unknown commit: {commit_hash}"
        return None

    def _path(self, args: list[str]) -> str:
        if len(args) != 2:
            return "Invalid args"
        for commit_hash in args:
            error = self._unknown_commit(commit_hash)
            if error is not None:
                return error
        path = self.graph.shortest_path(args[0], args[1])
        return "No path" if path is None else f"Path: {' -> '.join(path)}"

    def _ancestors(self, args: list[str]) -> str:
        if len(args) != 1:
            return "Invalid args"
        error = self._unknown_commit(args[0])
        if error is not None:
            return error
        ancestors = self.graph.ancestors(args[0])
        return self._format_commits(ancestors)

    def _search(self, args: list[str]) -> str:
        if len(args) != 1 or not args[0].strip():
            return "Invalid args"
        argument = args[0]
        if argument.lower().startswith("--author="):
            author = argument[len("--author=") :]
            if not author.strip():
                return "Invalid args"
            hashes = self.index.search_author(author)
        elif argument.startswith("--"):
            return "Invalid args"
        else:
            hashes = self.index.search_keyword(argument, self.graph.commits)

        lines = [f"Found {len(hashes)} commit(s):"]
        for commit_hash in hashes:
            commit = self.graph.commits[commit_hash]
            lines.append(f"- {commit.hash} ({commit.author}): {commit.message}")
        return "\n".join(lines)

    def _diff(self, args: list[str]) -> str:
        if len(args) != 2:
            return "Invalid args"
        try:
            old_lines = Path(args[0]).read_text(encoding="utf-8").splitlines()
            new_lines = Path(args[1]).read_text(encoding="utf-8").splitlines()
        except (OSError, UnicodeError) as error:
            return f"File error: {error}"
        result = line_diff(old_lines, new_lines)
        return "\n".join(result) if result else "No differences."

    def _merge(self, args: list[str]) -> str:
        if len(args) != 1:
            return "Invalid args"
        target_branch = args[0]
        if target_branch not in self.branches:
            return f"Unknown branch: {target_branch}"
        current_head = self._head()
        target_head = self.branches[target_branch]
        if (
            target_branch == self.current_branch
            or current_head is None
            or target_head is None
            or current_head == target_head
        ):
            return "Invalid args"

        message = f"Merge branch '{target_branch}'"
        commit = self._create_commit(message, (current_head, target_head))
        return f"[{self.current_branch} {commit.hash}] {message}"

    @staticmethod
    def _compare_number(left: int, right: int) -> int:
        return (left > right) - (left < right)

    def _benchmark(self, args: list[str]) -> str:
        if len(args) != 1:
            return "Invalid args"
        try:
            size = int(args[0])
        except ValueError:
            return "Invalid args"
        if size < 1 or size > 5000:
            return "Invalid args"

        values: list[int] = []
        state = 20240318
        for _ in range(size):
            state = (1103515245 * state + 12345) % (2**31)
            values.append(state)

        merge_start = time.perf_counter()
        merge_result = merge_sort(values, self._compare_number)
        merge_seconds = time.perf_counter() - merge_start

        insertion_start = time.perf_counter()
        insertion_result = insertion_sort(values, self._compare_number)
        insertion_seconds = time.perf_counter() - insertion_start

        if merge_result != insertion_result:
            return "Benchmark verification failed."
        return (
            f"Input size: {size}\n"
            f"Merge sort: {merge_seconds:.6f}s\n"
            f"Insertion sort: {insertion_seconds:.6f}s"
        )


def repl() -> None:
    """Run the interactive Mini Git read-evaluate-print loop."""

    app = MiniGit()
    while True:
        try:
            line = input("mini-git> ")
        except EOFError:
            print()
            break
        except KeyboardInterrupt:
            print("\nUse exit or quit to close Mini Git.")
            continue

        result = app.execute(line)
        if result == "__EXIT__":
            break
        print(result)


if __name__ == "__main__":
    repl()
