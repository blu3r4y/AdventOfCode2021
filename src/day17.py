# Advent of Code 2021, Day 17
# (c) blu3r4y

from itertools import count, repeat

import numpy as np
from aocd.models import Puzzle
from dotmap import DotMap
from funcy import concat, print_calls
from parse import parse
from tqdm.auto import tqdm


@print_calls
def part1(area):
    highpoint, _ = solve(area, 0, 100)
    return highpoint


@print_calls
def part2(area):
    _, velocities = solve(area, -100, 400)
    return len(velocities)


def solve(area, min_range, max_range):
    highpoint = -np.inf
    velocities = set()

    # brute-force velocities
    for vx in tqdm(range(0, max_range)):
        for vy in range(min_range, max_range):

            # iterate over trajectory
            peak = -np.inf
            for tx, ty in trajectory(vx, vy):
                peak = max(ty, peak)

                if in_target(tx, ty, area):
                    velocities.add((vx, vy))
                    highpoint = max(highpoint, peak)
                    break
                elif out_of_target(tx, ty, area):
                    break

    return highpoint, velocities


def trajectory(vx, vy, x=0, y=0):
    ax = concat(range(vx, 0, -sign(vx)), repeat(0))
    ay = count(vy, -1)

    for dx, dy in zip(ax, ay):
        x += dx
        y += dy
        yield x, y


def in_target(x, y, area):
    return area.x1 <= x <= area.x2 and area.y1 <= y <= area.y2


def out_of_target(x, y, area):
    return x > area.x2 or y < area.y1


def sign(x):
    return -1 if x < 0 else 1


def load(data):
    area = DotMap(parse("target area: x={x1:d}..{x2:d}, y={y1:d}..{y2:d}", data).named)
    assert 0 <= area.x1 <= area.x2 and area.y1 <= area.y2
    return area


if __name__ == "__main__":
    puzzle = Puzzle(year=2021, day=17)

    ans1 = part1(load(puzzle.input_data))
    # puzzle.answer_a = ans1
    ans2 = part2(load(puzzle.input_data))
    # puzzle.answer_b = ans2
