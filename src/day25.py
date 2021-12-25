# Advent of Code 2021, Day 25
# (c) blu3r4y

from itertools import count

import numpy as np
from aocd.models import Puzzle
from funcy import print_calls, remove

# identifies '.', '>', 'v'
FREE, EAST, SOUTH = 0, 1, 2


@print_calls
def part1(grid):
    for i in count(1):
        n1 = move_char(grid, EAST)
        n2 = move_char(grid, SOUTH)
        if n1 + n2 == 0:
            return i


def move_char(grid, char):
    lookahead = east if char == EAST else south
    moves = []

    # check if this char can move
    for xy, val in np.ndenumerate(grid):
        if val == char:
            px, py = lookahead(*xy, grid.shape)
            if grid[px, py] == FREE:
                moves.append((*xy, px, py))

    # perform the moves
    for x, y, px, py in moves:
        grid[x, y] = FREE
        grid[px, py] = char

    return len(moves)


def east(x, y, shape):
    return (x, (y + 1) % shape[1])


def south(x, y, shape):
    return ((x + 1) % shape[0], y)


def load(data):
    # parse into a 2d matrix of integers
    data = data.replace(".", "0").replace(">", "1").replace("v", "2")
    return np.fromiter(remove("\n", data), dtype=int).reshape(-1, data.index("\n"))


if __name__ == "__main__":
    puzzle = Puzzle(year=2021, day=25)

    ans1 = part1(load(puzzle.input_data))
    assert ans1 == 300
    # puzzle.answer_a = ans1
