# Advent of Code 2021, Day 2
# (c) blu3r4y

from aocd.models import Puzzle
from dotmap import DotMap
from funcy import print_calls
from parse import parse


@print_calls
def part1(instructions):
    hor, dep = 0, 0
    for e in instructions:
        if e.dir == "forward":
            hor += e.num
        elif e.dir == "down":
            dep += e.num
        elif e.dir == "up":
            dep -= e.num

    return hor * dep


@print_calls
def part2(instructions):
    hor, dep, aim = 0, 0, 0
    for e in instructions:
        if e.dir == "forward":
            hor += e.num
            dep += aim * e.num
        elif e.dir == "down":
            aim += e.num
        elif e.dir == "up":
            aim -= e.num

    return hor * dep


def load(data):
    return [DotMap(parse("{dir:l} {num:d}", line).named) for line in data.split("\n")]


if __name__ == "__main__":
    puzzle = Puzzle(year=2021, day=2)

    ans1 = part1(load(puzzle.input_data))
    # puzzle.answer_a = ans1
    ans2 = part2(load(puzzle.input_data))
    # puzzle.answer_b = ans2
