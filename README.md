# Git 핵심 구조 기반 Mini Git 구현

## 프로젝트 개요

Git의 커밋 그래프·해시·브랜치·탐색 알고리즘 직접 구현을 위한 메모리 기반 CLI 프로젝트

## 프로젝트 구조

```text
B5-2/
├── main.py              # CLI 엔트리 포인트
├── mini_git/
│   ├── __init__.py
│   ├── models.py        # Commit 데이터 모델
│   ├── graph.py         # 커밋 그래프·경로·조상 탐색
│   ├── index.py         # 메시지·작성자 역색인
│   ├── sorting.py       # 병합·버블 정렬 및 비교 함수
│   ├── diff.py          # LCS 기반 줄 비교
│   ├── repository.py    # 저장소 상태·브랜치·커밋·검색 관리
│   ├── cli.py           # 명령 해석·출력·파일 읽기·REPL
│   └── benchmark.py     # 정렬 성능 측정 및 결과 비교
├── tests/
│   ├── __init__.py
│   ├── test_algorithms.py  # 그래프·정렬 검증
│   ├── test_repository.py  # 저장소 연산·오류·상태 일관성 검증
│   └── test_cli.py         # 명령·입출력·전체 구현 문법 검증
├── docs/
│   ├── USER_GUIDE.md    # 설치·실행·CLI 사용 방법
│   └── USER_DEMO.md     # 기능별 사용자 시연 명령
└── README.md
```

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
- [x] 잘못된 입력 시 `잘못된 인자입니다.` 출력

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
- [x] 존재하지 않는 브랜치 접근 시 `존재하지 않는 브랜치: <name>` 출력

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
- [x] 경로가 없을 때 `경로가 없습니다.` 출력
- [x] 존재하지 않는 커밋 접근 시 `존재하지 않는 커밋: <hash>` 출력
- [x] 최단 경로 여러 개 존재 시 사전순 최소 경로 선택

### 조상 탐색

- [x] `ANCESTORS <commit_hash>` 명령 구현
- [x] 특정 커밋의 모든 조상 탐색
- [x] 중복 조상 제거
- [x] 조상 커밋 목록 출력
- [x] 존재하지 않는 커밋 접근 시 `존재하지 않는 커밋: <hash>` 출력

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

## 결과물

### 사용자 가이드

- [사용자 가이드](docs/USER_GUIDE.md)
- [사용자 시연 예시](docs/USER_DEMO.md)
