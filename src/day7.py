# Advent of Code 2021, Day 7
# (c) blu3r4y

import numpy as np
from aocd.models import Puzzle
from funcy import lmap, print_calls


@print_calls
def part1(data):
    return solve(data, gauss=False)


@print_calls
def part2(data):
    return solve(data, gauss=True)


def solve(data, gauss=False):
    lo, hi = data.min(), data.max()
    cheapest = np.inf

    for i in range(lo, hi + 1):
        fuels = np.abs(data - i)
        if gauss:
            # do not count l1 distance, but gauss distance
            fuels = gauss_sum(fuels)

        # find the cheapest total
        cost = fuels.sum()
        if cost < cheapest:
            cheapest = cost

    return cheapest


def gauss_sum(n):
    return (n * (n + 1)) // 2


def load(data):
    return np.array(lmap(int, data.split(",")))


if __name__ == "__main__":
    puzzle = Puzzle(year=2021, day=7)

    ans1 = part1(load(puzzle.input_data))
    # puzzle.answer_a = ans1
    ans2 = part2(load(puzzle.input_data))
    # puzzle.answer_b = ans2
