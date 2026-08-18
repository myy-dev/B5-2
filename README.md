# Git 핵심 구조 기반 Mini Git 구현

## 프로젝트 개요

Git의 커밋 그래프, 해시, 브랜치, 탐색 알고리즘을 직접 구현하는 CLI 기반 Mini Git 프로젝트이다.

커밋 노드와 브랜치 포인터를 직접 관리하고, 커밋 로그 출력, 최단 경로 탐색, 조상 탐색, 역색인 기반 검색, 직접 구현한 정렬 기능을 완성한다.

## 프로젝트 구조

```text
B3-2/
├── main.py       # 프로그램 엔트리 포인트와 알고리즘 구현
├── test_main.py  # 요구사항 자동 검증(16개 테스트)
└── README.md     # 사용법, 설계 및 검증 기록
```

> `main.py`는 CLI 엔트리 포인트로 사용한다. 커밋 그래프, 브랜치 관리, 탐색, 정렬, 인덱싱 로직은 함수 또는 클래스로 분리한다.

## 실행 및 테스트

Python 3.10 이상에서 외부 패키지 설치 없이 실행할 수 있다.

```bash
python3 main.py
```

자동 테스트 실행:

```bash
python3 -m unittest -v
```

## CLI 문법

- 명령어와 옵션은 대소문자를 구분하지 않는다.
- 사용자명, 커밋 메시지, 검색어에 공백이 있으면 따옴표로 감싼다.
  예: `INIT "Alice Kim"`, `COMMIT "Add login feature"`, `SEARCH "login feature"`
- 옵션은 `SEARCH --author=<name>`, `LOG --sort-by=date`,
  `LOG --sort-by=author` 형식으로 입력한다.
- 잘못된 인자에는 `Invalid args`, 없는 브랜치와 커밋에는 각각
  `Unknown branch: <name>`, `Unknown commit: <hash>`를 출력한다.
- 초기화 전에 저장소 명령을 실행하면 `Repository not initialized.`를 출력한다.

| 명령 | 동작 |
| --- | --- |
| `INIT <user_name>` | 메모리 저장소를 초기화하고 `main`, HEAD, author를 설정한다. |
| `BRANCH <branch_name>` | 현재 HEAD를 가리키는 브랜치를 만든다. |
| `SWITCH <branch_name>` | HEAD가 가리키는 브랜치를 바꾼다. |
| `COMMIT <message>` | 현재 HEAD를 부모로 하는 커밋을 만든다. |
| `LOG` | 모든 커밋을 부모 우선 위상 순서로 출력한다. |
| `LOG --sort-by=date\|author` | 날짜 또는 작성자 기준으로 직접 정렬하여 출력한다. |
| `PATH <commit1> <commit2>` | 부모 연결을 무방향 간선으로 본 최단 경로를 출력한다. |
| `ANCESTORS <commit_hash>` | 도달 가능한 모든 조상을 중복 없이 출력한다. |
| `SEARCH <keyword>` | 메시지 역색인으로 토큰 또는 구문을 검색한다. |
| `SEARCH --author=<name>` | 작성자 역색인으로 검색한다. |
| `DIFF <file1> <file2>` | 두 UTF-8 텍스트 파일을 줄 단위로 비교한다. |
| `MERGE <branch_name>` | 현재 HEAD와 대상 HEAD를 부모로 갖는 병합 커밋을 만든다. |
| `BENCHMARK <size>` | 병합 정렬과 삽입 정렬의 실행 시간을 비교한다(1~5000). |
| `exit`, `quit` | REPL을 종료한다. |

## 수행 항목 체크리스트

### CLI 기본 구성

- [x] `python3 main.py` 실행 가능
- [x] `mini-git>` 프롬프트 출력
- [x] 명령어 반복 입력 처리
- [x] `exit` 명령 종료
- [x] `quit` 명령 종료
- [x] 명령어 대소문자 구분 없이 처리
- [x] 공백 포함 문자열 인자 처리
- [x] 따옴표 문자열 인자 처리
- [x] 잘못된 입력 시 `Invalid args` 출력

### 저장소 초기화

- [x] `INIT <user_name>` 명령 구현
- [x] 저장소 초기화 처리
- [x] `main` 브랜치 생성
- [x] HEAD를 `main` 브랜치로 설정
- [x] 현재 사용자(author) 설정
- [x] 초기화 결과 출력

### 브랜치 관리

- [x] `BRANCH <branch_name>` 명령 구현
- [x] 현재 커밋을 가리키는 브랜치 생성
- [x] 브랜치 생성 결과 출력
- [x] `SWITCH <branch_name>` 명령 구현
- [x] HEAD 브랜치 전환 처리
- [x] 브랜치 전환 결과 출력
- [x] 존재하지 않는 브랜치 접근 시 `Unknown branch: <name>` 출력

### 커밋 그래프

- [x] Commit 노드 모델 구현
- [x] `hash` 필드 저장
- [x] `message` 필드 저장
- [x] `author` 필드 저장
- [x] `timestamp` 필드 저장
- [x] `parents` 필드 저장
- [x] 각 커밋의 0개 이상 부모 지원
- [x] DAG 구조 유지
- [x] 커밋 hash 기반 저장소 구현
- [x] 세션 내 커밋 hash 중복 방지

### 커밋 생성

- [x] `COMMIT <message>` 명령 구현
- [x] 현재 HEAD를 부모로 설정
- [x] 새 커밋 hash 생성
- [x] 현재 author 저장
- [x] 현재 timestamp 저장
- [x] 현재 브랜치 포인터 갱신
- [x] 커밋 생성 결과 출력
- [x] 커밋 생성 시 keyword 인덱스 갱신
- [x] 커밋 생성 시 author 인덱스 갱신

### 로그 출력

- [x] `LOG` 명령 구현
- [x] 부모 커밋 우선 출력
- [x] 커밋 hash 출력
- [x] author 출력
- [x] timestamp 출력
- [x] message 출력
- [x] 최신순 단순 나열 대신 부모-자식 관계 반영

### 정렬

- [x] Python `sorted()` 미사용
- [x] Python `list.sort()` 미사용
- [x] 직접 구현한 정렬 알고리즘 사용
- [x] 비교 기준 분리
- [x] `LOG --sort-by=date` 명령 구현
- [x] timestamp 기준 정렬 출력
- [x] `LOG --sort-by=author` 명령 구현
- [x] author 기준 정렬 출력
- [x] 평균 시간복잡도 설명 가능
- [x] 최악 시간복잡도 설명 가능
- [x] 안정 정렬 여부 설명 가능

### 경로 탐색

- [x] `PATH <commit1> <commit2>` 명령 구현
- [x] 커밋-부모 연결을 무방향 간선으로 처리
- [x] 간선 수 최소 경로 탐색
- [x] 경로 출력 형식 구현
- [x] 경로가 없을 때 `No path` 출력
- [x] 존재하지 않는 커밋 접근 시 `Unknown commit: <hash>` 출력
- [x] 최단 경로 여러 개 존재 시 사전순 최소 경로 선택

### 조상 탐색

- [x] `ANCESTORS <commit_hash>` 명령 구현
- [x] 특정 커밋의 모든 조상 탐색
- [x] 중복 조상 제거
- [x] 조상 커밋 목록 출력
- [x] 존재하지 않는 커밋 접근 시 `Unknown commit: <hash>` 출력

### 역색인 검색

- [x] keyword 인덱스 구현
- [x] author 인덱스 구현
- [x] 커밋 메시지 공백 기준 토큰화
- [x] 토큰 소문자 정규화
- [x] `keyword -> commit_hash 목록` 저장
- [x] `author -> commit_hash 목록` 저장
- [x] `SEARCH <keyword>` 명령 구현
- [x] 메시지 키워드 기반 검색 결과 출력
- [x] `SEARCH --author=<name>` 명령 구현
- [x] 작성자 기반 검색 결과 출력
- [x] 전체 커밋 순회 없는 후보 조회

### CLI 문법 표준

- [x] `INIT <user_name>` 지원
- [x] `BRANCH <branch_name>` 지원
- [x] `SWITCH <branch_name>` 지원
- [x] `COMMIT <message>` 지원
- [x] `LOG` 지원
- [x] `LOG --sort-by=date` 지원
- [x] `LOG --sort-by=author` 지원
- [x] `PATH <commit1> <commit2>` 지원
- [x] `ANCESTORS <commit_hash>` 지원
- [x] `SEARCH <keyword>` 지원
- [x] `SEARCH --author=<name>` 지원

### 코드 품질

- [x] 탐색 로직 분리
- [x] 정렬 로직 분리
- [x] 인덱싱 로직 분리
- [x] 명령어 파싱 로직 분리
- [x] 주요 함수 docstring 작성
- [x] 주요 클래스 docstring 작성
- [x] 커밋 메타데이터 중심 구현
- [x] 파일 내용 추적 미구현
- [x] 네트워크 통신 미구현
- [x] 메모리 기반 동작

### 보너스 과제

#### Diff 구현

- [x] `DIFF <file1> <file2>` 명령 구현
- [x] 두 텍스트 파일 줄 단위 비교
- [x] 추가 줄 출력
- [x] 삭제 줄 출력
- [x] 공통 줄 출력

#### Merge 구현

- [x] `MERGE <branch_name>` 명령 구현
- [x] 현재 브랜치 HEAD 부모 연결
- [x] 대상 브랜치 HEAD 부모 연결
- [x] 부모 2개인 merge commit 생성
- [x] merge commit 생성 결과 출력

#### 정렬 성능 비교

- [x] 서로 다른 정렬 알고리즘 2개 이상 구현
- [x] 입력 크기별 실행 시간 측정
- [x] 알고리즘별 실행 시간 비교
- [x] 시간복잡도 분석 기록

## 제약 사항

- Python 3.10 이상 사용
- 실행 커맨드 `python3 main.py` 준수(`python`이 Python 3을 가리키면 동일)
- 그래프 전용 라이브러리 사용 금지
- Python 표준 정렬 API 사용 금지
- `sorted()` 사용 금지
- `list.sort()` 사용 금지
- 기본 자료형 사용 가능
- 문자열 처리 사용 가능
- 파일 입출력 사용 가능
- 시간 처리 사용 가능
- 커밋 hash 세션 내 유일성 보장
- 커밋 저장소 hash map 기반 조회
- 검색 기능 역색인 기반 구현
- 데이터 영속성 구현 선택 사항
- 파일 내용 추적 구현 제외
- 네트워크 통신 구현 제외
- 알고리즘 로직 독립 함수 또는 클래스 분리
- 주요 함수 또는 클래스 주석/docstring 작성

## 자료구조와 알고리즘

### 커밋 그래프와 DAG

`Commit`은 `hash`, `message`, `author`, `timestamp`, `parents`를 저장한다.
`CommitGraph.commits`는 `dict[hash, Commit]`이므로 hash를 이용한 평균 조회
시간은 O(1)이다. 자식 인접 목록도 별도로 관리해 무방향 경로 탐색 시 매번
전체 커밋을 훑지 않는다.

새 커밋은 이미 그래프에 존재하는 커밋만 부모로 선택할 수 있다. `parents`
참조를 따라가면 간선은 새 노드에서 과거 노드로 향하므로, 과거 노드에서 새
노드로 돌아오는 사이클을 만들 수 없다. 이 불변식 때문에 커밋 그래프는
방향성 비순환 그래프(DAG)다. 일반 커밋은 부모가 0개 또는 1개이고 `MERGE`
커밋은 부모가 2개다.

커밋 hash는 증가하는 프로세스 세션 카운터와 SHA-256 결과 8자리를 결합한다.
`INIT`으로 저장소를 재초기화해도 카운터는 되돌리지 않는다. 증가 카운터
전체가 hash에 포함되므로 같은 REPL 세션에서는 동일한 작성자와 메시지로
재초기화 후 다시 커밋해도 hash가 중복되지 않는다.

### 부모 우선 LOG

`LOG`는 저장된 `자식 -> 부모` 참조를 뒤집어 `부모 -> 자식` 방향으로 보고
Kahn 위상 정렬을 수행한다. 이 방향에서 각 커밋의 부모 수가 진입 차수다.
진입 차수가 0인 커밋부터 꺼낸 뒤 그 자식의 진입 차수를 감소시키므로 부모는
항상 자식보다 먼저 출력된다. 현재 진입 차수가 0인 모든 후보는 hash 최소
힙으로 관리해 결과를 결정적으로 만든다. 일반적인 Kahn 알고리즘은 O(V+E)이고,
이 구현은 최소 힙 연산을 포함해 O((V+E) log V)이다.

`LOG --sort-by=...`는 그래프 순서와 별개의 명시적인 정렬 명령이다. Python의
표준 정렬 API 대신 다음 두 알고리즘을 직접 구현했다.

| 알고리즘 | 평균 | 최악 | 추가 공간 | 안정 정렬 |
| --- | --- | --- | --- | --- |
| 병합 정렬 | O(n log n) | O(n log n) | O(n) | 예 |
| 삽입 정렬 | O(n²) | O(n²) | O(n)¹ | 예 |

¹ 정렬 루프 자체는 제자리 O(1)이지만, 공개 함수가 입력을 보존하고 새 결과
리스트를 반환하기 위해 O(n) 복사본을 만든다.

실제 `LOG`에는 병합 정렬을 사용한다. 병합 시 값이 같으면 왼쪽 원소를 먼저
선택해 안정성을 보장한다. 비교 함수를 분리하여 timestamp 또는 소문자 author를
기준으로 바꿀 수 있다. 삽입 정렬은 `BENCHMARK` 비교 대상으로 사용한다.

### PATH와 ANCESTORS

`PATH`는 부모와 자식 인접 목록을 합쳐 간선을 무방향으로 취급한다. 우선순위
큐에 `(간선 수, 경로 hash 튜플, 현재 hash)`를 넣어 탐색하므로 간선 수가 가장
적은 경로가 먼저 선택된다. 거리가 같으면 전체 hash 경로 튜플을 비교하므로
`hash1->hash2->...` 문자열 기준 사전순 최소 경로가 선택된다. 연결되지 않은
두 루트 사이에는 `No path`를 출력한다.

`ANCESTORS`는 대상 커밋의 부모에서 시작하는 DFS로 도달 가능한 hash를 `set`에
모은다. 따라서 병합 그래프에서 같은 조상을 여러 경로로 만나도 한 번만
포함한다. 조상 수집 자체는 O(V+E)이고 방문 집합은 O(V) 공간을 쓴다. 이후
결과를 부모 우선으로 만들기 위해 전체 그래프에 힙 기반 위상 정렬을 적용하므로
명령 전체 시간복잡도는 O((V+E) log V), 추가 공간복잡도는 O(V+E)이다.

### 역색인

커밋 생성 시 메시지를 `split()`하고 각 토큰을 `lower()`한 뒤
`keyword -> commit hash 목록`에 저장한다. 작성자도 소문자로 정규화해
`author -> commit hash 목록`에 저장한다. 같은 메시지에서 같은 토큰이 반복돼도
posting list에는 해당 hash를 한 번만 넣는다.

단일 토큰이나 작성자 검색은 dict 조회 후 결과 K개만 읽으므로 평균 O(1+K)다.
여러 단어 검색은 각 토큰의 posting list를 교집합 후보로 좁힌 후 구문 포함
여부를 검사한다. 모든 커밋 N개를 매번 순회하는 O(N) 검색보다 후보가 적을수록
빠르다.

### DIFF

두 파일의 줄 배열에 대해 최장 공통 부분 수열(LCS)을 동적 계획법으로 구한다.
공통 줄은 공백 두 개, 삭제 줄은 `- `, 추가 줄은 `+ ` 접두사로 출력한다.
두 파일의 줄 수가 각각 n, m이면 시간·공간복잡도는 O(nm)이다.

## 명령어 예시

```text
mini-git> init "Alice"
Initialized repository.
Current branch: main
Current user: Alice

mini-git> commit "Initial commit"
[main 000000017d21a0b3] Initial commit

mini-git> branch feature
Created branch: feature

mini-git> switch feature
Switched to branch: feature

mini-git> commit "Add login feature"
[feature 000000029c77872b] Add login feature

mini-git> switch main
Switched to branch: main

mini-git> commit "Add payment feature"
[main 00000003fd47c15f] Add payment feature

mini-git> log
commit 000000017d21a0b3 (Alice, <timestamp>)
Initial commit

commit 000000029c77872b (Alice, <timestamp>) [feature]
Add login feature

commit 00000003fd47c15f (Alice, <timestamp>) [main]
Add payment feature

mini-git> path 000000017d21a0b3 00000003fd47c15f
Path: 000000017d21a0b3 -> 00000003fd47c15f

mini-git> ancestors 000000029c77872b
commit 000000017d21a0b3 (Alice, <timestamp>)
Initial commit

mini-git> search "login"
Found 1 commit(s):
- 000000029c77872b (Alice): Add login feature

mini-git> search --author=Alice
Found 3 commit(s):
- 000000017d21a0b3 (Alice): Initial commit
- 000000029c77872b (Alice): Add login feature
- 00000003fd47c15f (Alice): Add payment feature
```

timestamp는 실행 시점에 따라 달라진다. 예시 hash는 위 명령을 새 세션에서
순서대로 실행했을 때의 값이다.

## 기능 검증 기록

- 실행 명령: `python3 main.py` (`python`이 Python 3을 가리키는 환경에서는
  `python main.py`도 동일)
- 검증 일자: 2026-08-18
- 프롬프트 및 `exit`/`quit`: 통과
- INIT 초기화·재초기화·공백 author: 통과
- BRANCH 생성 및 SWITCH 전환·오류: 통과
- COMMIT 부모·hash 고유성·브랜치 포인터: 통과
- LOG 부모 우선 및 date/author 정렬: 통과
- PATH 무방향 최단 경로·사전순 동률·No path: 통과
- ANCESTORS 전체 조상·중복 제거: 통과
- SEARCH keyword·구문·author 역색인: 통과
- DIFF 공통·삭제·추가 줄: 통과
- MERGE 부모 2개·인덱스 갱신: 통과
- BENCHMARK 두 정렬 결과 일치 및 시간 출력: 통과
- 자동 테스트: 16개 전체 통과 (`python3 -m unittest -v`)
- 재INIT 후 hash 재사용 회귀 테스트: 통과
- 공백-only·따옴표 오류·알 수 없는 명령 검증: 통과
- 중복 hash·없는 부모에 대한 그래프 방어 검증: 통과
- Python 3.10 문법 AST 검사: 통과
- 문법 검사: 통과 (`python3 -m py_compile main.py`)
- 금지 정렬 API 호출 검사: 0건

## 알고리즘 분석 기록

- 커밋 저장소 조회 방식: hash를 key로 갖는 dict, 평균 O(1)
- LOG 부모 우선 출력 방식: 진입 차수와 최소 힙을 사용하는 Kahn 위상 정렬
- PATH 최단 경로 탐색 방식: 무방향 인접 목록과 `(거리, 전체 경로)` 우선순위 큐
- ANCESTORS 조상 탐색 방식: 부모 방향 DFS와 방문 set
- 실제 LOG 정렬 알고리즘: 안정 병합 정렬
- 정렬 평균 시간복잡도: 병합 O(n log n), 삽입 O(n²)
- 정렬 최악 시간복잡도: 병합 O(n log n), 삽입 O(n²)
- 안정 정렬 여부: 두 구현 모두 안정 정렬
- 역색인 검색 시간복잡도: 단일 key 평균 O(1+K), K는 결과 수

## 보너스 구현 기록

- Diff 구현 여부: 완료(LCS 기반 줄 단위 비교)
- Merge 구현 여부: 완료(서로 다른 두 HEAD를 부모로 저장)
- 정렬 성능 비교 여부: 완료(병합 정렬과 삽입 정렬)
- 사용한 추가 명령어: `DIFF`, `MERGE`, `BENCHMARK`
- 검증 결과: 자동 테스트 전체 통과
