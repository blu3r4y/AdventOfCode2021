# Advent of Code 2021, Day 11
# (c) blu3r4y

from itertools import count

import numpy as np
from aocd.models import Puzzle
from funcy import print_calls, remove


@print_calls
def part1(arr):
    return solve(arr, limit=100)


@print_calls
def part2(arr):
    return solve(arr, limit=None)


def solve(arr, limit):
    total_flashes = 0

    steps = range(limit) if limit else count()
    for step in steps:
        arr += 1

        # positions to be flashed, i.e. overflowing positions
        overflow = np.argwhere(arr > 9)
        overflow = set(map(tuple, overflow))
        flashed = set()

        while overflow:
            flash = overflow.pop()
            if flash not in flashed:
                flashed.add(flash)

                # increase adjacent and check overflows
                for adj in adjacent(*flash, arr.shape):
                    if adj not in flashed:
                        arr[adj] += 1
                        if arr[adj] > 9:
                            overflow.add(adj)

        # reset all flashed positions
        total_flashes += len(flashed)
        for xy in flashed:
            arr[xy] = 0

        # with no limit, return step at which flashes synchronize
        if limit is None and len(flashed) == arr.size:
            return step + 1

    # with a limit, return number of total flashes
    return total_flashes


def adjacent(x, y, shape):
    # get adjacent with diagonals and out-of-bounds check
    adj = (
        (x, y),
        (x, y + 1),
        (x, y - 1),
        (x + 1, y),
        (x - 1, y),
        (x + 1, y + 1),
        (x - 1, y - 1),
        (x + 1, y - 1),
        (x - 1, y + 1),
    )
    return ((x, y) for x, y in adj if 0 <= x < shape[0] and 0 <= y < shape[1])


def load(data):
    # parse into a 2d matrix of integers
    return np.fromiter(remove("\n", data), dtype=int).reshape(-1, data.index("\n"))


if __name__ == "__main__":
    puzzle = Puzzle(year=2021, day=11)

    ans1 = part1(load(puzzle.input_data))
    # puzzle.answer_a = ans1
    ans2 = part2(load(puzzle.input_data))
    # puzzle.answer_b = ans2
