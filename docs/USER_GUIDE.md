# 사용자 가이드

Git의 커밋 그래프·브랜치·탐색·검색 알고리즘을 메모리에서 실행하는 터미널 도구의 설치 및 사용 방법

## 요구사항

- Python 3.10 이상
- Git

## 설치

### 1. 저장소 복제 및 이동

```bash
git clone https://github.com/myy-dev/B5-2.git
cd B5-2
```

### 2. 의존성 설치

Python 표준 라이브러리만 사용하므로 별도 설치 불필요

## 실행

macOS 또는 Linux 환경

```bash
python3 main.py
```

Windows PowerShell 환경

```powershell
py -3 main.py
```

## 기본 사용법

### 저장소 초기화 및 커밋 생성

```text
mini-git> init "Alice"
mini-git> commit "Initial commit"
```

### 브랜치 생성 및 전환

```text
mini-git> branch feature
mini-git> switch feature
mini-git> commit "Add login feature"
```

### 브랜치 병합

```text
mini-git> switch main
mini-git> merge feature
```

## CLI 명령어

| 명령어 | 설명 |
| --- | --- |
| `INIT <user_name>` | 저장소 초기화 및 `main`·HEAD·작성자 설정 |
| `BRANCH <branch_name>` | 현재 HEAD 위치에 브랜치 생성 |
| `SWITCH <branch_name>` | 현재 브랜치 전환 |
| `COMMIT <message>` | 현재 HEAD를 부모로 갖는 커밋 생성 |
| `LOG` | 전체 커밋의 부모 우선 위상 순서 출력 |
| `LOG --sort-by=date` | 커밋 시각 기준 정렬 출력 |
| `LOG --sort-by=author` | 작성자 기준 정렬 출력 |
| `PATH <commit1> <commit2>` | 두 커밋 사이의 최단 경로 출력 |
| `ANCESTORS <commit_hash>` | 조상 커밋의 중복 없는 출력 |
| `SEARCH <keyword>` | 메시지 키워드·구문 검색 |
| `SEARCH --author=<name>` | 작성자 검색 |
| `DIFF <file1> <file2>` | 두 UTF-8 텍스트 파일의 줄 단위 비교 |
| `MERGE <branch_name>` | 부모가 2개인 병합 커밋 생성 |
| `BENCHMARK <size>` | 병합·버블 정렬 성능 비교(1~10000) |
| `exit`, `quit` | 프로그램 종료 |

## 입력 규칙

- 명령어·옵션의 대소문자 구분 없음
- 공백 포함 사용자명·커밋 메시지·검색 구문의 따옴표 처리
- `PATH`, `ANCESTORS`의 커밋 메시지 대신 커밋 hash 사용
- `DIFF`의 공백 포함 파일 경로 따옴표 처리

## 출력 및 동작 규칙

### 커밋

- 세션 내 고유 hash 생성
- 현재 브랜치의 마지막 커밋을 부모로 연결
- 커밋 생성 후 현재 브랜치 HEAD 갱신

### 병합

- 현재 브랜치 HEAD와 대상 브랜치 HEAD를 부모로 연결
- 부모가 2개인 병합 커밋 생성
- 파일 내용 병합 및 충돌 해결 제외

### 데이터 유지

- 메모리 기반 저장소
- `INIT` 재실행 시 커밋·브랜치·검색 색인 초기화
- 프로그램 종료 시 저장소 데이터 소멸

## 오류와 해결

| 메시지 또는 상황 | 해결 방법 |
| --- | --- |
| `Repository not initialized.` | `INIT <user_name>` 실행 |
| `Invalid args` | 명령어의 인자 개수·옵션·따옴표 확인 |
| `Unknown branch: <name>` | `BRANCH`로 생성한 브랜치명 확인 |
| `Unknown commit: <hash>` | `LOG` 또는 `SEARCH` 결과의 커밋 hash 사용 |
| `No path` | 두 커밋이 같은 연결 그래프에 속하는지 확인 |
| `File error: ...` | 파일 경로·읽기 권한·UTF-8 인코딩 확인 |
| `Benchmark verification failed.` | 동일 입력의 두 정렬 결과 불일치 여부 확인 |
