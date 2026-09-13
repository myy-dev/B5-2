"""CLI와 분리된 저장소 상태 및 기능 관리"""

from __future__ import annotations

import hashlib
from datetime import datetime

from .graph import CommitGraph
from .index import InvertedIndex
from .models import Commit
from .sorting import compare_author, compare_date, merge_sort


class RepositoryError(ValueError):
    """CLI 오류 메시지 변환용 저장소 예외"""

    def __init__(self, code: str, detail: str = "") -> None:
        super().__init__(code, detail)
        self.code = code
        self.detail = detail


class Repository:
    """브랜치 관리 및 커밋·색인·HEAD 동기화"""

    def __init__(self) -> None:
        self.graph = CommitGraph()
        self.index = InvertedIndex()
        self.branches: dict[str, str | None] = {}
        self.current_branch: str | None = None
        self.author: str | None = None
        self._commit_counter = 0

    @property
    def initialized(self) -> bool:
        """작성자 및 현재 브랜치 설정 여부"""

        return self.author is not None and self.current_branch is not None

    @property
    def head(self) -> str | None:
        """현재 브랜치의 마지막 커밋 해시 조회"""

        return (
            None if self.current_branch is None else self.branches[self.current_branch]
        )

    def require_initialized(self) -> None:
        """저장소 초기화 여부 검사"""

        if not self.initialized:
            raise RepositoryError("not_initialized")

    def _require_commit(self, commit_hash: str) -> None:
        if commit_hash not in self.graph.commits:
            raise RepositoryError("unknown_commit", commit_hash)

    def initialize(self, author: str) -> None:
        """세션 해시 카운터 유지 및 저장소 초기화"""

        if not author.strip():
            raise RepositoryError("invalid_args")
        self.graph.clear()
        self.index.clear()
        self.branches = {"main": None}
        self.current_branch = "main"
        self.author = author

    def create_branch(self, name: str) -> None:
        """빈 이름·중복 이름 검사 후 HEAD 위치에 브랜치 생성"""

        self.require_initialized()
        if not name.strip() or name in self.branches:
            raise RepositoryError("invalid_args")
        self.branches[name] = self.head

    def switch(self, name: str) -> None:
        """기존 브랜치로 전환"""

        self.require_initialized()
        if name not in self.branches:
            raise RepositoryError("unknown_branch", name)
        self.current_branch = name

    def _new_hash(self, message: str, parents: tuple[str, ...]) -> str:
        """증가하는 접두사를 이용한 세션 내 고유 해시 생성"""

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
        """HEAD 기준 커밋 생성 및 저장소 참조 갱신"""

        self.require_initialized()
        if not message.strip():
            raise RepositoryError("invalid_args")
        parents = () if self.head is None else (self.head,)
        return self._create_commit(message, parents)

    def merge(self, target_branch: str) -> Commit:
        """서로 다른 두 브랜치의 마지막 커밋을 부모로 병합 커밋 생성"""

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
        """부모 우선 또는 지정 기준의 커밋 목록 정렬"""

        self.require_initialized()
        if sort_by is None:
            return self.graph.topological_order()
        comparators = {"date": compare_date, "author": compare_author}
        if sort_by not in comparators:
            raise RepositoryError("invalid_args")
        return merge_sort(self.graph.commits.values(), comparators[sort_by])

    def path(self, start: str, end: str) -> list[str] | None:
        """커밋 간 무방향 최단 경로 탐색"""

        self.require_initialized()
        self._require_commit(start)
        self._require_commit(end)
        return self.graph.shortest_path(start, end)

    def ancestors(self, commit_hash: str) -> list[Commit]:
        """중복 없는 조상 커밋의 부모 우선 조회"""

        self.require_initialized()
        self._require_commit(commit_hash)
        return self.graph.ancestors(commit_hash)

    def search(self, query: str, *, by_author: bool = False) -> list[Commit]:
        """색인 기반 키워드·구문·작성자 검색"""

        self.require_initialized()
        if not query.strip():
            raise RepositoryError("invalid_args")
        hashes = (
            self.index.search_author(query)
            if by_author
            else self.index.search_keyword(query, self.graph.commits)
        )
        return [self.graph.commits[commit_hash] for commit_hash in hashes]
