# Advent of Code 2021, Day 9
# (c) blu3r4y

import numpy as np
import numpy.ma as ma
from aocd.models import Puzzle
from funcy import print_calls, remove


@print_calls
def part1(heightmap):
    mask = lowest_points(heightmap)
    risk_levels = ma.masked_array(heightmap + 1, ~mask)
    return risk_levels.sum()


@print_calls
def part2(heightmap):
    mask = lowest_points(heightmap)
    coords = np.argwhere(mask == True)

    sizes = []
    for x, y in coords:
        basin = search_basins(heightmap, x, y)
        sizes.append(basin.sum())

    # multiply three largest basins
    a, b, c = sorted(sizes)[-3:]
    return a * b * c


def search_basins(heightmap, x, y):
    # the target point is part of the basin already
    mask = np.zeros_like(heightmap).astype(bool)
    mask[x, y] = True
    visited = {(x, y)}

    # recursive flood fill
    def _fill(_x, _y, BOUNDARY=9):
        indexes = [xy for xy in adjacent(_x, _y, heightmap.shape) if xy not in visited]
        for (ix, iy) in indexes:
            visited.add((ix, iy))
            if heightmap[ix, iy] != BOUNDARY:
                mask[ix, iy] = True
                _fill(ix, iy)

    _fill(x, y)
    return mask


def lowest_points(heightmap):
    shape = heightmap.shape
    mask = np.zeros_like(heightmap).astype(bool)

    for x, y in np.ndindex(shape):
        pt = heightmap[x, y]
        ix = adjacent(x, y, shape)
        vl = [heightmap[i] for i in ix]

        # identify local minimum
        if all(v > pt for v in vl):
            mask[x, y] = True

    return mask


def adjacent(x, y, shape):
    # get neighbours without diagonals and without out of bounds access
    adj = ((x, y - 1), (x, y + 1), (x - 1, y), (x + 1, y))
    return ((a, b) for a, b in adj if 0 <= a < shape[0] and 0 <= b < shape[1])


def load(data):
    # parse into a 2d matrix of integers
    return np.fromiter(remove("\n", data), dtype=int).reshape(-1, data.index("\n"))


if __name__ == "__main__":
    puzzle = Puzzle(year=2021, day=9)

    ans1 = part1(load(puzzle.input_data))
    # puzzle.answer_a = ans1
    ans2 = part2(load(puzzle.input_data))
    # puzzle.answer_b = ans2
