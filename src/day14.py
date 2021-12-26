# Advent of Code 2021, Day 14
# (c) blu3r4y

from collections import Counter, namedtuple

from aocd.models import Puzzle
from funcy import pairwise, print_calls
from parse import parse

Input = namedtuple("Input", ["seq", "rules"])


@print_calls
def part1(data):
    return solve(data.seq, data.rules, 10)


@print_calls
def part2(data):
    return solve(data.seq, data.rules, 40)


def solve(seq, rules, steps):
    counts = Counter()

    # count initial pairs in sequence
    for pair in pairwise(seq):
        pair = "".join(pair)
        counts[pair] += 1

    # apply transformations
    for _ in range(steps):
        step = counts.copy()
        for pair, count in counts.items():
            assert pair in rules

            a, b = rules[pair]
            step[pair] -= count
            step[a] += count
            step[b] += count

        # change counts in one step
        counts = step

    # count first letters, which is enough because they overlap
    letters = Counter()
    for pair, count in counts.items():
        letters[pair[0]] += count

    # the last letter in the sequence has no pair but always exists
    letters[seq[-1]] += 1

    most = letters.most_common()[0][1]
    least = letters.most_common()[-1][1]

    return most - least


def load(data):
    seq, brules = data.split("\n\n")

    rules = {}
    for pair in brules.splitlines():
        # rule "AB -> C" is storead as AB -> (AC, CB)
        a1, a2, b = parse("{:l}{:l} -> {:l}", pair)
        rules[a1 + a2] = (a1 + b, b + a2)

    return Input(seq, rules)


if __name__ == "__main__":
    puzzle = Puzzle(year=2021, day=14)

    ans1 = part1(load(puzzle.input_data))
    # puzzle.answer_a = ans1
    ans2 = part2(load(puzzle.input_data))
    # puzzle.answer_b = ans2
