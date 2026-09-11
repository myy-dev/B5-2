from __future__ import annotations

from .models import Commit


class InvertedIndex:
    """정규화한 메시지 토큰·작성자와 커밋 해시 목록 연결"""

    def __init__(self) -> None:
        self.keyword_to_hashes: dict[str, list[str]] = {}
        self.author_to_hashes: dict[str, list[str]] = {}

    @staticmethod
    def _tokens(text: str) -> list[str]:
        return [token.lower() for token in text.split() if token]

    def clear(self) -> None:
        """저장소 재초기화 시 전체 색인 삭제"""

        self.keyword_to_hashes.clear()
        self.author_to_hashes.clear()

    def add(self, commit: Commit) -> None:
        """메시지 토큰별 해시 중복 방지를 통한 커밋 색인 등록"""

        seen_tokens: set[str] = set()
        for token in self._tokens(commit.message):
            if token in seen_tokens:
                continue
            seen_tokens.add(token)
            self.keyword_to_hashes.setdefault(token, []).append(commit.hash)

        author_key = commit.author.lower()
        self.author_to_hashes.setdefault(author_key, []).append(commit.hash)

    def search_keyword(self, query: str, commits: dict[str, Commit]) -> list[str]:
        """색인 목록 기반 토큰·구문 검색"""

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
        """정규화한 작성자명의 커밋 해시 목록 복사본 반환"""

        return list(self.author_to_hashes.get(author.lower(), []))
