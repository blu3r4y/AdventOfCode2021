# Advent of Code 2021, Day 20
# (c) blu3r4y

from collections import defaultdict, namedtuple

from aocd.models import Puzzle
from funcy import first, lmap, print_calls, second

Input = namedtuple("Input", "image lookup")


@print_calls
def part1(data):
    return solve(data, 2)


@print_calls
def part2(data):
    return solve(data, 50)


def solve(data, steps):
    image, void = data.image, "0"
    for _ in range(steps):
        image, void = enhance(image, data.lookup, void)

    return list(image.values()).count("1")


def enhance(image, lookup, void="0"):
    image.default_factory = lambda: void
    result = defaultdict(lambda: void)

    # get bounds
    xs, ys = lmap(first, image.keys()), lmap(second, image.keys())
    xmin, xmax, ymin, ymax = min(xs), max(xs), min(ys), max(ys)

    # iterate over all pixels, with extra padding of 1
    for x in range(xmin - 1, xmax + 2):
        for y in range(ymin - 1, ymax + 2):
            idx = bits(image, x, y)
            result[(x, y)] = lookup[idx]

    newvoid = lookup[int(void * 9, 2)]
    return result, newvoid


def bits(image, x, y):
    bits = ""
    for ax, ay in adjacent(x, y):
        bits += image[(ax, ay)]
    return int(bits, 2)


def adjacent(x, y):
    return (
        # row 1
        (x - 1, y - 1),
        (x, y - 1),
        (x + 1, y - 1),
        # row 2
        (x - 1, y),
        (x, y),
        (x + 1, y),
        # row 2
        (x - 1, y + 1),
        (x, y + 1),
        (x + 1, y + 1),
    )


def load(data):
    blocks = data.split("\n\n")

    lookup = blocks[0].replace(".", "0").replace("#", "1")
    image = defaultdict(int)
    for y, line in enumerate(blocks[1].splitlines()):
        for x, px in enumerate(line):
            image[(x, y)] = px.replace(".", "0").replace("#", "1")

    return Input(image, lookup)


if __name__ == "__main__":
    puzzle = Puzzle(year=2021, day=20)

    ans1 = part1(load(puzzle.input_data))
    # puzzle.answer_a = ans1
    ans2 = part2(load(puzzle.input_data))
    # puzzle.answer_b = ans2
