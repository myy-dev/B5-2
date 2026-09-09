# Mini Git 시연 시나리오

## 시연 개요

- 예상 시간: 8~10분
- 흐름: 초기화 → 분기·커밋 → 병합·로그 → 탐색·검색 → 오류 처리 → 보너스 기능 → 재초기화·종료
- 시연 대상: 메모리 기반 커밋 그래프, 브랜치 포인터, 직접 구현한 알고리즘
- 진행 기준: 새 프로세스에서 아래 순서대로 실행, 명령어 블록만 입력
- hash 기준: 동일 작성자·메시지·커밋 생성 순서에서 아래 값 재현 가능
- 재시작 기준: 순서 변경 또는 추가 커밋 생성 시 `quit` 후 `python3 main.py`부터 재실행
- 가변 출력: timestamp 및 벤치마크 측정 시간

## 0. 사전 준비 — 시연 전

프로젝트 루트의 터미널에서 Diff용 임시 파일 생성:

```bash
python3 - <<'PY'
from pathlib import Path
from tempfile import mkdtemp

folder = Path(mkdtemp(prefix="mini-git-demo-"))
(folder / "before.txt").write_text("title\nold login\nfooter\n", encoding="utf-8")
(folder / "after.txt").write_text("title\nnew login\nfooter\n", encoding="utf-8")
print(f'DIFF "{folder / "before.txt"}" "{folder / "after.txt"}"')
PY
```

준비 결과: 임시 폴더와 두 UTF-8 파일 생성, 화면에 출력된 `DIFF` 명령 복사 후 7단계에서 사용

## 1. 실행 및 초기화 — 30초

터미널에서 실행:

```bash
python3 main.py
```

이후 모든 명령은 `mini-git>` 프롬프트에 입력:

```text
log
InIt "Alice"
branch island
```

| 입력 | 예상 결과 | 설명 포인트 |
| --- | --- | --- |
| `log` | `Repository not initialized.` | 초기화 전 명령 차단 |
| `InIt "Alice"` | 초기화 완료, 현재 브랜치 `main`, 사용자 `Alice` | 명령어 대소문자 구분 없음 |
| `branch island` | `Created branch: island` | 빈 HEAD의 브랜치 생성, 이후 미연결 경로 시연에 활용 |

## 2. 커밋 생성 및 브랜치 분기 — 1분

```text
commit "Initial commit"
branch feature
switch feature
commit "Add login feature"
switch main
commit "Add payment feature"
```

| 기호 | 커밋 hash | 메시지 | 부모 |
| --- | --- | --- | --- |
| A | `000000017d21a0b3` | Initial commit | 없음 |
| B | `000000029c77872b` | Add login feature | A |
| C | `00000003fd47c15f` | Add payment feature | A |

확인 기준: `feature`는 B, `main`은 C를 가리키는 상태

설명 포인트: 브랜치별 커밋 복제 없이 포인터 관리, 현재 브랜치에서만 HEAD 갱신

## 3. 병합 및 로그 — 1분 30초

```text
merge feature
log
log --sort-by=date
log --sort-by=author
```

병합 직후 예상 출력:

```text
[main 00000004798be2a2] Merge branch 'feature'
```

병합 후 구조 — 화살표는 설명용 부모 → 자식 방향:

```text
    B [feature]
   / \
  A   D [main]
   \ /
    C
```

- D의 부모: C, B / D의 hash: `00000004798be2a2`
- 기본 `log`: A → B → C → D 순서, B에 `[feature]`, D에 `[main]` 표시
- 날짜 정렬: timestamp 오름차순, 직접 구현한 병합 정렬 사용
- 작성자 정렬: 소문자 작성자 → timestamp → hash 순서
- 이번 시연의 작성자: 전부 Alice, 두 정렬 옵션의 커밋 순서 동일
- 병합 범위: 부모 2개의 커밋 생성 및 역색인 갱신, 파일 내용 병합 미지원
- 부모 관계 시연: 아래 경로·조상 탐색 활용, `log` 자체에는 부모 필드 미출력

## 4. 최단 경로 및 조상 탐색 — 1분

```text
path 000000029c77872b 00000003fd47c15f
ancestors 00000004798be2a2
```

PATH 예상 출력:

```text
Path: 000000029c77872b -> 000000017d21a0b3 -> 00000003fd47c15f
```

- 후보 경로: B → A → C, B → D → C / 두 경로 모두 간선 2개
- 선택 결과: 전체 hash 경로의 사전순 비교로 B → A → C 선택
- 설명 포인트: 부모·자식 연결의 무방향 탐색, 최단 거리 동률 처리

ANCESTORS 확인 기준: A, B, C 각각 1회 출력, D 제외

설명 포인트: 두 부모 경로에 공통으로 존재하는 A의 중복 제거, 부모 우선 결과 정렬

## 5. 역색인 검색 — 1분

```text
search login
search "login feature"
search --author=Alice
search missing
```

| 입력 | 예상 결과 | 설명 포인트 |
| --- | --- | --- |
| `search login` | B 1개 | 메시지 토큰 역색인 조회 |
| `search "login feature"` | B 1개 | 토큰 교집합 후보에서 구문 확인 |
| `search --author=Alice` | A, B, C, D 총 4개 | 작성자 역색인 및 병합 커밋 등록 |
| `search missing` | `Found 0 commit(s):` | 검색 결과 없음 처리 |

## 6. 미연결 경로 및 잘못된 입력 — 1분

```text
switch island
commit "Island root"
path 000000017d21a0b3 00000005c01b6e5f
switch main
switch missing
path missing missing
commit
merge main
```

| 입력 | 예상 결과 |
| --- | --- |
| `commit "Island root"` | `[island 00000005c01b6e5f] Island root` |
| A와 island 커밋의 `path` | `No path` |
| `switch missing` | `Unknown branch: missing` |
| `path missing missing` | `Unknown commit: missing` |
| 인자 없는 `commit` | `Invalid args` |
| 현재 브랜치 대상 `merge main` | `Invalid args` |

설명 포인트: 초기 빈 HEAD에서 분리된 루트 생성, 미연결 그래프 처리, 오류 발생 후 명령 입력 지속

## 7. Diff 및 정렬 성능 비교 — 1분

0단계에서 복사한 `DIFF` 명령을 Mini Git 프롬프트에 입력

예상 출력 — 공통 줄 앞 공백 2개:

```text
  title
- old login
+ new login
  footer
```

설명 포인트: LCS 기반 줄 비교, 공통·삭제·추가 구분, 파일별 줄 수 n·m 기준 시간·공간 O(nm)

이어서 입력:

```text
benchmark 100
benchmark 1000
```

확인 기준: 각 입력 크기의 `Input size`, `Merge sort`, `Insertion sort` 출력

- 비교 조건: 두 알고리즘에 동일 입력 제공, 정렬 결과 일치 확인
- 설명 포인트: 병합 정렬 O(n log n), 삽입 정렬 평균·최악 O(n²)
- 측정 해석: 실행 환경별 시간 변동, 두 입력 크기의 관측값으로 복잡도 증명 불가

## 8. 재초기화 및 종료 — 30초

```text
init Alice
log
search login
commit "Initial commit"
quit
```

| 입력 | 예상 결과 |
| --- | --- |
| `init Alice` | 저장소 재초기화, `main`·Alice 설정 |
| `log` | `No commits.` |
| `search login` | `Found 0 commit(s):` |
| `commit "Initial commit"` | `[main 00000006265f0eff] Initial commit` |
| `quit` | Mini Git 종료 및 터미널 복귀 |

설명 포인트: 재초기화 시 커밋·브랜치·역색인 초기화, 세션 카운터 유지로 첫 커밋 A와 다른 hash 생성

## 마무리 확인

- [ ] 브랜치 분기 및 두 부모 병합 설명
- [ ] 부모 우선 로그와 정렬 옵션 확인
- [ ] 최단 경로 동률 처리 및 조상 중복 제거 확인
- [ ] 키워드·구문·작성자 검색 확인
- [ ] 미연결 경로 및 잘못된 입력 처리 확인
- [ ] Diff·정렬 성능 비교 확인
- [ ] 재초기화 후 hash 고유성 및 종료 확인
