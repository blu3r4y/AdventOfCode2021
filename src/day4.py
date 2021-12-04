# Advent of Code 2021, Day 4
# (c) blu3r4y

import numpy as np
import numpy.ma as ma

from aocd.models import Puzzle
from funcy import print_calls, lmap

BOARD_SHAPE = 5


@print_calls
def part1(draws, boards):
    return bingo(draws, boards)


@print_calls
def part2(draws, boards):
    return bingo(draws, boards, first_winner=False)


def bingo(draws, boards, first_winner=True):
    num_boards = len(boards)

    # allocate an empty mask for each board
    masks = [np.zeros_like(boards[0], dtype=bool) for _ in range(num_boards)]

    # index of winning boards in order
    winners = []

    draw = None
    for draw in draws:

        # (1) mask boards
        for i in range(num_boards):
            masks[i] = mask_board(boards[i], masks[i], draw)

        # (2) search winners
        for i in range(num_boards):
            if i not in winners and has_won(masks[i]):
                winners.append(i)

                # immediate return if we only search the first winner
                if first_winner:
                    return score(boards[i], masks[i], draw)

        # (3) stop entire game if all players won
        if len(winners) == num_boards:
            break

    # alternative routine for part 2 - where we output the last winner score
    assert not first_winner
    last = winners[-1]
    return score(boards[last], masks[last], draw)


def mask_board(board, mask, draw):
    return np.logical_or(mask, (board == draw))


def has_won(mask):
    col = any(mask.sum(axis=0) == BOARD_SHAPE)
    row = any(mask.sum(axis=1) == BOARD_SHAPE)
    return row or col


def score(board, mask, draw):
    masked = ma.masked_array(board, mask)
    unmarked = masked.sum()
    return unmarked * draw


def load(data):
    lines = data.split("\n")
    draws = lmap(int, lines[0].split(","))
    boards = []
    for i in range(2, len(lines), BOARD_SHAPE + 1):
        board = lines[i : (i + BOARD_SHAPE)]
        board = [lmap(int, row.split()) for row in board]
        board = np.array(board, dtype=int)
        boards.append(board)

    return draws, boards


if __name__ == "__main__":
    puzzle = Puzzle(year=2021, day=4)

    ans1 = part1(*load(puzzle.input_data))
    # puzzle.answer_a = ans1
    ans2 = part2(*load(puzzle.input_data))
    # puzzle.answer_b = ans2
