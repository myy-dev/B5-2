from __future__ import annotations

import heapq

from .models import Commit


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
