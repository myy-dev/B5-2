"""재현 가능한 입력 기반 두 정렬의 성능 측정"""

from __future__ import annotations

import time
from dataclasses import dataclass

from .sorting import bubble_sort, compare_number, merge_sort


@dataclass(frozen=True)
class BenchmarkResult:
    """정렬별 실행 시간 및 결과 일치 여부"""

    size: int
    merge_seconds: float
    bubble_seconds: float
    verified: bool


def run_benchmark(size: int) -> BenchmarkResult:
    """동일한 입력 1~10000개에 대한 두 정렬의 실행 시간 측정"""

    if size < 1 or size > 10000:
        raise ValueError("size must be between 1 and 10000")
    values: list[int] = []
    state = 20240318
    for _ in range(size):
        state = (1103515245 * state + 12345) % (2**31)
        values.append(state)

    merge_start = time.perf_counter()
    merge_result = merge_sort(values, compare_number)
    merge_seconds = time.perf_counter() - merge_start

    bubble_start = time.perf_counter()
    bubble_result = bubble_sort(values, compare_number)
    bubble_seconds = time.perf_counter() - bubble_start
    return BenchmarkResult(
        size, merge_seconds, bubble_seconds, merge_result == bubble_result
    )
