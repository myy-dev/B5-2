# Mini Git 사용법

## 실행 방법

실행 환경: Python 3.10 이상, 외부 패키지 불필요

프로젝트 루트에서 실행:

```bash
python3 main.py
```

`mini-git>` 프롬프트에서 명령 입력, `exit` 또는 `quit`으로 종료

## CLI 문법

- 명령어·옵션의 대소문자 구분 없음
- 공백 포함 사용자명·커밋 메시지·검색어의 따옴표 처리 필수
  예: `INIT "Alice Kim"`, `COMMIT "Add login feature"`, `SEARCH "login feature"`
- 옵션 형식: `SEARCH --author=<name>`, `LOG --sort-by=date`, `LOG --sort-by=author`
- 잘못된 인자: `Invalid args` 출력
- 없는 브랜치·커밋: `Unknown branch: <name>`, `Unknown commit: <hash>` 출력
- 초기화 전 저장소 명령: `Repository not initialized.` 출력

| 명령 | 동작 |
| --- | --- |
| `INIT <user_name>` | 메모리 저장소 초기화, `main`·HEAD·author 설정 |
| `BRANCH <branch_name>` | 현재 HEAD를 가리키는 브랜치 생성 |
| `SWITCH <branch_name>` | HEAD의 대상 브랜치 전환 |
| `COMMIT <message>` | 현재 HEAD를 부모로 갖는 커밋 생성 |
| `LOG` | 전체 커밋의 부모 우선 위상 순서 출력 |
| `LOG --sort-by=date\|author` | 날짜·작성자 기준 직접 정렬 및 출력 |
| `PATH <commit1> <commit2>` | 부모 연결을 무방향 간선으로 취급한 최단 경로 출력 |
| `ANCESTORS <commit_hash>` | 도달 가능한 모든 조상의 중복 없는 출력 |
| `SEARCH <keyword>` | 메시지 역색인 기반 토큰·구문 검색 |
| `SEARCH --author=<name>` | 작성자 역색인 검색 |
| `DIFF <file1> <file2>` | 두 UTF-8 텍스트 파일의 줄 단위 비교 |
| `MERGE <branch_name>` | 현재·대상 HEAD를 부모로 갖는 병합 커밋 생성 |
| `BENCHMARK <size>` | 병합·삽입 정렬 실행 시간 비교(1~5000) |
| `exit`, `quit` | REPL 종료 |
