from __future__ import annotations

from typing import Callable, Iterable, TypeVar

from .models import Commit

T = TypeVar("T")
Comparator = Callable[[T, T], int]


def merge_sort(items: Iterable[T], compare: Comparator[T]) -> list[T]:
    """Return a stable merge-sorted list without using a standard sorting API."""

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
    """Return a stable insertion-sorted list for benchmark comparison."""

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
    """Compare commits by timestamp, then hash."""

    left_key = (left.timestamp, left.hash)
    right_key = (right.timestamp, right.hash)
    return (left_key > right_key) - (left_key < right_key)


def compare_author(left: Commit, right: Commit) -> int:
    """Compare normalized authors, then timestamp and hash."""

    left_key = (left.author.lower(), left.timestamp, left.hash)
    right_key = (right.author.lower(), right.timestamp, right.hash)
    return (left_key > right_key) - (left_key < right_key)


def compare_number(left: int, right: int) -> int:
    """Compare numeric values for benchmark sorting."""

    return (left > right) - (left < right)
