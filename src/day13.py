# Advent of Code 2021, Day 13
# (c) blu3r4y

from collections import namedtuple

import matplotlib.pylab as plt
import numpy as np
import pylab as plt
from aocd.models import Puzzle
from funcy import print_calls
from parse import parse

Input = namedtuple("Input", ["dots", "folds"])


@print_calls
def part1(data):
    return solve(data, first_fold=True)


@print_calls
def part2(data):
    return solve(data)


def solve(data, first_fold=False):
    paper = fill(data.dots)
    for ax, num in data.folds:
        fold = foldx if ax == "x" else foldy
        paper = fold(paper, num)

        # number of dots after one fold
        if first_fold:
            return paper.sum()

    # final letters
    plt.imshow(paper.T)
    plt.show()


def fill(dots):
    width, height = dots.max(axis=0) + 1

    # ensure canvas is even after folding on either axis
    if width % 2 == 0:
        width += 1
    if height % 2 == 0:
        height += 1

    paper = np.zeros((width, height), dtype=int)

    # set dots in paper
    mask = np.ravel_multi_index(dots.T, paper.shape)
    np.ravel(paper)[mask] = 1

    return paper


def foldx(paper, x):
    # ensure empty fold line and symmetric canvas
    assert paper[x, :].sum() == 0
    assert paper.shape[0] == 2 * x + 1

    right = paper[(x + 1) :, :]
    right = np.flipud(right)

    paper = paper[:x, :]
    paper[right == 1] = 1

    return paper


def foldy(paper, y):
    # ensure empty fold line and symmetric canvas
    assert paper[:, y].sum() == 0
    assert paper.shape[1] == 2 * y + 1

    lower = paper[:, (y + 1) :]
    lower = np.fliplr(lower)

    paper = paper[:, :y]
    paper[lower == 1] = 1

    return paper


def load(data):
    bldots, blfolds = data.split("\n\n")

    dots = []
    for line in bldots.splitlines():
        dot = parse("{:d},{:d}", line)
        dots.append(tuple(dot))
    dots = np.array(dots)

    folds = []
    for line in blfolds.splitlines():
        fold = parse("fold along {:w}={:d}", line)
        folds.append(tuple(fold))

    return Input(dots, folds)


if __name__ == "__main__":
    puzzle = Puzzle(year=2021, day=13)

    ans1 = part1(load(puzzle.input_data))
    # puzzle.answer_a = ans1
    ans2 = part2(load(puzzle.input_data))
    # puzzle.answer_b = ans2
