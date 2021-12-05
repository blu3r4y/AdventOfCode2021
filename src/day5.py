# Advent of Code 2021, Day 5
# (c) blu3r4y

from collections import defaultdict

from aocd.models import Puzzle
from dotmap import DotMap
from funcy import print_calls
from parse import parse


@print_calls
def part1(data):
    return solve(data)


@print_calls
def part2(data):
    return solve(data, diagonal=True)


def solve(data, diagonal=False):
    canvas = defaultdict(set)

    for no, e in enumerate(data):
        if e.x1 == e.x2:
            draw_orthogonal(no, e.x1, e.y1, e.y2, canvas)
        elif e.y1 == e.y2:
            draw_orthogonal(no, e.y1, e.x1, e.x2, canvas, swap=True)
        elif diagonal:
            draw_diagonal(no, e.x1, e.y1, e.x2, e.y2, canvas)

    num_overlaps = sum([len(pt) > 1 for pt in canvas.values()])
    return num_overlaps


def draw_orthogonal(i, x, y1, y2, canvas, swap=False):
    y1, y2 = sorted((y1, y2))
    for yn in range(y1, y2 + 1):
        point = (x, yn) if not swap else (yn, x)
        canvas[point].add(i)


def draw_diagonal(i, x1, y1, x2, y2, canvas):
    x, y = x1, y1
    while x != x2 and y != y2:
        canvas[(x, y)].add(i)

        x += 1 if x < x2 else -1
        y += 1 if y < y2 else -1

    canvas[(x2, y2)].add(i)


def load(data):
    return [
        DotMap(parse("{x1:d},{y1:d} -> {x2:d},{y2:d}", line).named)
        for line in data.split("\n")
    ]


if __name__ == "__main__":
    puzzle = Puzzle(year=2021, day=5)

    ans1 = part1(load(puzzle.input_data))
    # puzzle.answer_a = ans1
    ans2 = part2(load(puzzle.input_data))
    # puzzle.answer_b = ans2
