"""명령어 분석·결과 출력·파일 입력·대화형 실행"""

from __future__ import annotations

import shlex
from pathlib import Path
from typing import Iterable

from .benchmark import run_benchmark
from .diff import line_diff
from .models import Commit
from .repository import Repository, RepositoryError


class MiniGit:
    """텍스트 명령어의 저장소 기능 연결 및 결과 형식화"""

    def __init__(self, repository: Repository | None = None) -> None:
        self.repository = repository if repository is not None else Repository()

    def _branch_labels(self, commit_hash: str) -> str:
        names = [
            name
            for name, target in self.repository.branches.items()
            if target == commit_hash
        ]
        return f" [{' '.join(names)}]" if names else ""

    def _format_commits(
        self, commits: Iterable[Commit], show_branches: bool = False
    ) -> str:
        blocks: list[str] = []
        for commit in commits:
            timestamp = commit.timestamp.strftime("%Y-%m-%d %H:%M:%S.%f")
            labels = self._branch_labels(commit.hash) if show_branches else ""
            blocks.append(
                f"커밋 {commit.hash} ({commit.author}, {timestamp}){labels}\n{commit.message}"
            )
        return "\n\n".join(blocks) if blocks else "커밋이 없습니다."

    def _format_created_commit(self, commit: Commit) -> str:
        return f"[{self.repository.current_branch} {commit.hash}] {commit.message}"

    @staticmethod
    def _require_count(args: list[str], count: int) -> None:
        if len(args) != count:
            raise RepositoryError("invalid_args")

    @staticmethod
    def _format_error(error: RepositoryError) -> str:
        messages = {
            "invalid_args": "잘못된 인자입니다.",
            "not_initialized": "저장소가 초기화되지 않았습니다.",
            "unknown_branch": f"존재하지 않는 브랜치: {error.detail}",
            "unknown_commit": f"존재하지 않는 커밋: {error.detail}",
        }
        return messages[error.code]

    def execute(self, line: str) -> str:
        """명령어 분석 및 저장소 예외의 CLI 메시지 변환"""

        try:
            parts = shlex.split(line)
        except ValueError:
            return "잘못된 인자입니다."
        if not parts:
            return "잘못된 인자입니다."

        command, args = parts[0].lower(), parts[1:]
        if command in {"exit", "quit"}:
            return "__EXIT__" if not args else "잘못된 인자입니다."
        handlers = {
            "init": self._init,
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
            return "잘못된 인자입니다."
        try:
            if command != "init":
                self.repository.require_initialized()
            return handler(args)
        except RepositoryError as error:
            return self._format_error(error)

    def _init(self, args: list[str]) -> str:
        self._require_count(args, 1)
        self.repository.initialize(args[0])
        return (
            "저장소를 초기화했습니다.\n"
            "현재 브랜치: main\n"
            f"현재 사용자: {self.repository.author}"
        )

    def _branch(self, args: list[str]) -> str:
        self._require_count(args, 1)
        self.repository.create_branch(args[0])
        return f"브랜치를 생성했습니다: {args[0]}"

    def _switch(self, args: list[str]) -> str:
        self._require_count(args, 1)
        self.repository.switch(args[0])
        return f"브랜치를 전환했습니다: {args[0]}"

    def _commit(self, args: list[str]) -> str:
        self._require_count(args, 1)
        return self._format_created_commit(self.repository.commit(args[0]))

    def _log(self, args: list[str]) -> str:
        if not args:
            return self._format_commits(self.repository.log(), show_branches=True)
        self._require_count(args, 1)
        option = args[0].lower()
        if option not in {"--sort-by=date", "--sort-by=author"}:
            return "잘못된 인자입니다."
        return self._format_commits(self.repository.log(option.split("=", 1)[1]))

    def _path(self, args: list[str]) -> str:
        self._require_count(args, 2)
        path = self.repository.path(args[0], args[1])
        return "경로가 없습니다." if path is None else f"경로: {' -> '.join(path)}"

    def _ancestors(self, args: list[str]) -> str:
        self._require_count(args, 1)
        return self._format_commits(self.repository.ancestors(args[0]))

    def _search(self, args: list[str]) -> str:
        self._require_count(args, 1)
        argument = args[0]
        if argument.lower().startswith("--author="):
            commits = self.repository.search(
                argument[len("--author=") :], by_author=True
            )
        elif argument.startswith("--"):
            return "잘못된 인자입니다."
        else:
            commits = self.repository.search(argument)
        lines = [f"검색 결과: {len(commits)}개"]
        for commit in commits:
            lines.append(f"- {commit.hash} ({commit.author}): {commit.message}")
        return "\n".join(lines)

    def _diff(self, args: list[str]) -> str:
        self._require_count(args, 2)
        try:
            old_lines = Path(args[0]).read_text(encoding="utf-8").splitlines()
            new_lines = Path(args[1]).read_text(encoding="utf-8").splitlines()
        except UnicodeError:
            return "파일 오류: UTF-8 텍스트 파일이 아닙니다."
        except OSError:
            return "파일 오류: 파일을 읽을 수 없습니다."
        result = line_diff(old_lines, new_lines)
        return "\n".join(result) if result else "차이가 없습니다."

    def _merge(self, args: list[str]) -> str:
        self._require_count(args, 1)
        return self._format_created_commit(self.repository.merge(args[0]))

    def _benchmark(self, args: list[str]) -> str:
        self._require_count(args, 1)
        try:
            result = run_benchmark(int(args[0]))
        except ValueError:
            return "잘못된 인자입니다."
        if not result.verified:
            return "벤치마크 검증에 실패했습니다."
        return (
            f"입력 크기: {result.size}\n"
            f"병합 정렬: {result.merge_seconds:.6f}초\n"
            f"버블 정렬: {result.bubble_seconds:.6f}초"
        )


def repl() -> None:
    """미니 깃 대화형 입력·실행·출력 반복"""

    app = MiniGit()
    while True:
        try:
            line = input("mini-git> ")
        except EOFError:
            print()
            break
        except KeyboardInterrupt:
            print("\n종료하려면 exit 또는 quit을 입력하세요.")
            continue

        result = app.execute(line)
        if result == "__EXIT__":
            break
        print(result)
