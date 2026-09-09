"""Deterministic benchmark input and timing for the two manual sorts."""

from __future__ import annotations

import time
from dataclasses import dataclass

from .sorting import compare_number, insertion_sort, merge_sort


@dataclass(frozen=True)
class BenchmarkResult:
    """Measured durations and agreement between sorting algorithms."""

    size: int
    merge_seconds: float
    insertion_seconds: float
    verified: bool


def run_benchmark(size: int) -> BenchmarkResult:
    """Measure both sorts on identical input of 1 to 5000 elements."""

    if size < 1 or size > 5000:
        raise ValueError("size must be between 1 and 5000")
    values: list[int] = []
    state = 20240318
    for _ in range(size):
        state = (1103515245 * state + 12345) % (2**31)
        values.append(state)

    merge_start = time.perf_counter()
    merge_result = merge_sort(values, compare_number)
    merge_seconds = time.perf_counter() - merge_start

    insertion_start = time.perf_counter()
    insertion_result = insertion_sort(values, compare_number)
    insertion_seconds = time.perf_counter() - insertion_start
    return BenchmarkResult(size, merge_seconds, insertion_seconds, merge_result == insertion_result)
