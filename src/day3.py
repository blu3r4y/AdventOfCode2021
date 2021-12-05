# Advent of Code 2021, Day 3
# (c) blu3r4y

from functools import partial

import numpy as np
from aocd.models import Puzzle
from funcy import print_calls, remove


@print_calls
def part1(data):
    gamma, epsilon = "", ""

    n = data.shape[0]
    for pos in range(n):
        bit = most_common(*count_bits(data, pos))
        gamma += str(bit)

    # this is just the binary inverse then
    epsilon = gamma.translate(gamma.maketrans("01", "10"))

    gamma = int(gamma, 2)
    epsilon = int(epsilon, 2)

    return epsilon * gamma


@print_calls
def part2(data):
    oxy = filter_values(data, criteria=partial(most_common, tie=1))
    co2 = filter_values(data, criteria=partial(least_common, tie=0))

    return oxy * co2


def filter_values(arr, criteria):
    tmp = arr.copy()
    pos = 0

    # iterate until there is only one element left
    while tmp.shape[1] > 1:
        assert pos < tmp.shape[0]

        n, p = count_bits(tmp, pos)
        bit = criteria(n, p)

        # filter rows by bit set in column
        mask = tmp[pos, :] == bit
        tmp = tmp[:, mask]

        pos += 1

    # map binary array back to integer
    result = tmp[:, 0]
    result = int("".join(map(str, result)), 2)

    return result


def count_bits(arr, pos):
    n = np.sum(arr[pos, :] == 0)
    p = np.sum(arr[pos, :] == 1)
    return n, p


def most_common(x, y, tie=None):
    if x == y:
        return tie
    return 0 if x > y else 1


def least_common(x, y, tie=None):
    if x == y:
        return tie
    return 1 if x > y else 0


def load(data):
    # parse into a 2d matrix of integers
    return np.fromiter(remove("\n", data), dtype=int).reshape(-1, data.index("\n")).T


if __name__ == "__main__":
    puzzle = Puzzle(year=2021, day=3)

    ans1 = part1(load(puzzle.input_data))
    # puzzle.answer_a = ans1
    ans2 = part2(load(puzzle.input_data))
    # puzzle.answer_b = ans2
