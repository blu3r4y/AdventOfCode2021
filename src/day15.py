# Advent of Code 2021, Day 15
# (c) blu3r4y

from itertools import product

import networkx as nx
import numpy as np
from aocd.models import Puzzle
from funcy import print_calls, remove


@print_calls
def part1(arr):
    return solve(arr)


@print_calls
def part2(arr):
    arr = full_map(arr, 5)
    return solve(arr)


def solve(arr):
    grid = nx.grid_2d_graph(*arr.shape)

    # shortest path by using target vertex weight as edge weight in dijkstra
    end = arr.shape[0] - 1, arr.shape[1] - 1
    path = nx.dijkstra_path(grid, (0, 0), end, weight=lambda u, v, d: arr[v])

    # sum of weights, except the first
    risk = sum(arr[p] for p in path[1:])
    return risk


def full_map(tile, n):
    w, h = tile.shape
    full = np.zeros((w * n, h * n), dtype=int)

    for ix, iy in product(range(n), repeat=2):
        for x, y in np.ndindex(tile.shape):
            # let value overflow from 9 -> 1
            value = (tile[x, y] - 1 + ix + iy) % 9 + 1
            full[x + w * ix, y + h * iy] = value

    return full


def load(data):
    # parse into a 2d matrix of integers
    return np.fromiter(remove("\n", data), dtype=int).reshape(-1, data.index("\n"))


if __name__ == "__main__":
    puzzle = Puzzle(year=2021, day=15)

    ans1 = part1(load(puzzle.input_data))
    # puzzle.answer_a = ans1
    ans2 = part2(load(puzzle.input_data))
    # puzzle.answer_b = ans2
