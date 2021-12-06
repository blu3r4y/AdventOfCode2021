# Advent of Code 2021, Day 6
# (c) blu3r4y

from aocd.models import Puzzle
from funcy import lmap, print_calls


@print_calls
def part1(data, days=80):
    for _ in range(days):
        zeros = data.count(0)
        data = [6 if e == 0 else (e - 1) for e in data]
        data.extend([8] * zeros)
    return len(data)


@print_calls
def part2(data, days=256):
    # this does the same as day 1, but in linear time

    # denote initial birth frequencies
    births = [0] * 9
    for d in data:
        births[d] += 1

    for _ in range(days):
        # step through lifetime by shifting births
        rotate_left(births)
        # fish that are born at 8 will breed again at 6
        births[6] += births[8]

    return sum(births)


def rotate_left(arr):
    # [ 1 2 3 4 ] -> [ 2 3 4 1 ]
    arr[:-1], arr[-1] = arr[1:], arr[0]


def load(data):
    return lmap(int, data.split(","))


if __name__ == "__main__":
    puzzle = Puzzle(year=2021, day=6)

    ans1 = part1(load(puzzle.input_data))
    # puzzle.answer_a = ans1
    ans2 = part2(load(puzzle.input_data))
    # puzzle.answer_b = ans2
