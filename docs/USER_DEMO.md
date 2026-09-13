# 사용자 시연 예시

## 실행

```bash
python3 main.py
```

## 저장소 초기화

```text
init "Alice"
```

## 커밋 생성

```text
commit "Initial commit"
```

## 브랜치 생성 및 전환

```text
branch feature
switch feature
commit "Add login feature"
switch main
commit "Add payment feature"
```

## 브랜치 병합

현재 브랜치 `main`에 `feature` 병합

```text
merge feature
```

## 커밋 로그 조회

```text
log
log --sort-by=date
log --sort-by=author
```

## 최단 경로 조회

```text
path 000000029c77872b 00000003fd47c15f
```

## 조상 커밋 조회

```text
ancestors 00000004798be2a2
```

## 커밋 검색

```text
search login
search "login feature"
search --author=Alice
```

## 텍스트 파일 비교

UTF-8 형식의 `before.txt`, `after.txt` 준비 후 실행

```text
diff "before.txt" "after.txt"
```

## 정렬 성능 비교

```text
benchmark 100
benchmark 1000
```

## 저장소 재초기화

```text
init "Bob"
log
```

## 종료

```text
quit
```
