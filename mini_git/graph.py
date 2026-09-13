from __future__ import annotations

import heapq

from .models import Commit


class CommitGraph:
    """해시 기반 커밋 저장 및 그래프 탐색"""

    def __init__(self) -> None:
        self.commits: dict[str, Commit] = {}
        self.children: dict[str, list[str]] = {}

    def clear(self) -> None:
        """전체 노드 및 인접 정보 삭제"""

        self.commits.clear()
        self.children.clear()

    def add(self, commit: Commit) -> None:
        """해시 및 부모 참조 검증 후 노드 추가"""

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
        """칸 알고리즘 기반 부모 우선 위상 정렬"""

        indegree = {commit_hash: 0 for commit_hash in self.commits}
        for commit in self.commits.values():
            indegree[commit.hash] = len(commit.parents)

        available = [
            commit_hash for commit_hash, degree in indegree.items() if degree == 0
        ]
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
        """무방향 최단 경로 탐색 및 동률 시 사전순 선택"""

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
        """도달 가능한 조상의 중복 제거 및 부모 우선 조회"""

        discovered: set[str] = set()
        stack = list(self.commits[commit_hash].parents)
        while stack:
            current = stack.pop()
            if current in discovered:
                continue
            discovered.add(current)
            stack.extend(self.commits[current].parents)

        return [
            commit for commit in self.topological_order() if commit.hash in discovered
        ]
