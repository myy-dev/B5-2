from __future__ import annotations

from typing import Callable, Iterable, TypeVar

from .models import Commit

T = TypeVar("T")
Comparator = Callable[[T, T], int]


def merge_sort(items: Iterable[T], compare: Comparator[T]) -> list[T]:
    """내장 정렬 함수 없이 직접 구현한 안정 병합 정렬"""

    values = list(items)
    if len(values) < 2:
        return values

    middle = len(values) // 2
    left = merge_sort(values[:middle], compare)
    right = merge_sort(values[middle:], compare)
    merged: list[T] = []
    left_index = 0
    right_index = 0

    while left_index < len(left) and right_index < len(right):
        if compare(left[left_index], right[right_index]) <= 0:
            merged.append(left[left_index])
            left_index += 1
        else:
            merged.append(right[right_index])
            right_index += 1

    merged.extend(left[left_index:])
    merged.extend(right[right_index:])
    return merged


def insertion_sort(items: Iterable[T], compare: Comparator[T]) -> list[T]:
    """성능 비교용 안정 삽입 정렬"""

    values = list(items)
    for index in range(1, len(values)):
        current = values[index]
        position = index - 1
        while position >= 0 and compare(values[position], current) > 0:
            values[position + 1] = values[position]
            position -= 1
        values[position + 1] = current
    return values


def compare_date(left: Commit, right: Commit) -> int:
    """커밋 시각·해시 순 비교"""

    left_key = (left.timestamp, left.hash)
    right_key = (right.timestamp, right.hash)
    return (left_key > right_key) - (left_key < right_key)


def compare_author(left: Commit, right: Commit) -> int:
    """소문자 작성자명·커밋 시각·해시 순 비교"""

    left_key = (left.author.lower(), left.timestamp, left.hash)
    right_key = (right.author.lower(), right.timestamp, right.hash)
    return (left_key > right_key) - (left_key < right_key)


def compare_number(left: int, right: int) -> int:
    """성능 측정용 숫자 비교"""

    return (left > right) - (left < right)
