# Advent of Code 2021, Day 1
# (c) blu3r4y

from aocd.models import Puzzle
from funcy import print_calls

import numpy as np


@print_calls
def part1(data):
    return np.sum(np.diff(data) > 0)


@print_calls
def part2(data):
    window = np.convolve(data, np.ones(3, dtype=int), "valid")
    return np.sum(np.diff(window) > 0)


def load(data):
    return np.fromstring(data, dtype=int, sep="\n")


if __name__ == "__main__":
    puzzle = Puzzle(year=2021, day=1)

    ans1 = part1(load(puzzle.input_data))
    # puzzle.answer_a = ans1
    ans2 = part2(load(puzzle.input_data))
    # puzzle.answer_b = ans2
