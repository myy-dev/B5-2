from __future__ import annotations

from .models import Commit


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
