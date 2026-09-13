from __future__ import annotations


def line_diff(old_lines: list[str], new_lines: list[str]) -> list[str]:
    """최장 공통 부분 수열 동적 계획법 기반 줄 단위 차이 계산"""

    old_count = len(old_lines)
    new_count = len(new_lines)
    lengths = [[0] * (new_count + 1) for _ in range(old_count + 1)]

    for old_index in range(old_count - 1, -1, -1):
        for new_index in range(new_count - 1, -1, -1):
            if old_lines[old_index] == new_lines[new_index]:
                lengths[old_index][new_index] = (
                    lengths[old_index + 1][new_index + 1] + 1
                )
            else:
                skip_old = lengths[old_index + 1][new_index]
                skip_new = lengths[old_index][new_index + 1]
                lengths[old_index][new_index] = max(skip_old, skip_new)

    result: list[str] = []
    old_index = 0
    new_index = 0
    while old_index < old_count and new_index < new_count:
        if old_lines[old_index] == new_lines[new_index]:
            result.append(f"  {old_lines[old_index]}")
            old_index += 1
            new_index += 1
        elif lengths[old_index + 1][new_index] >= lengths[old_index][new_index + 1]:
            result.append(f"- {old_lines[old_index]}")
            old_index += 1
        else:
            result.append(f"+ {new_lines[new_index]}")
            new_index += 1

    while old_index < old_count:
        result.append(f"- {old_lines[old_index]}")
        old_index += 1
    while new_index < new_count:
        result.append(f"+ {new_lines[new_index]}")
        new_index += 1
    return result
