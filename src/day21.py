# Advent of Code 2021, Day 21
# (c) blu3r4y

from collections import namedtuple
from functools import cache
from itertools import count, cycle, product

from aocd.models import Puzzle
from funcy import collecting, print_calls, take
from parse import parse

State = namedtuple("State", "p1 p2 s1 s2 turn")


@print_calls
def part1(pos, min_score=1000):
    state = State(*pos, 0, 0, 0)
    die = cycle(range(1, 100 + 1))

    for turn in count(1):
        roll = sum(take(3, die))
        state = advance(state, roll)

        win = winner(state, min_score)
        if win is not None:
            break

    # get the score of the losing player
    other = state.s2 if win == 0 else state.s1
    return other * 3 * turn


@print_calls
def part2(pos, min_score=21):
    state = State(*pos, 0, 0, 0)
    u1, u2 = play(state, min_score)
    return max(u1, u2)


@cache
def play(state, min_score):
    win = winner(state, min_score)
    if win is not None:
        return (1, 0) if win == 0 else (0, 1)

    u1, u2 = 0, 0
    for roll in quantum_roll():
        nextstate = advance(state, roll)
        d1, d2 = play(nextstate, min_score)
        u1, u2 = u1 + d1, u2 + d2

    return u1, u2


def advance(state, roll):
    turn = 1 - state.turn

    # move with overflow 10 -> 1 and increase score
    if state.turn == 0:
        p1 = (state.p1 + roll - 1) % 10 + 1
        s1 = state.s1 + p1
        return State(p1, state.p2, s1, state.s2, turn)

    elif state.turn == 1:
        p2 = (state.p2 + roll - 1) % 10 + 1
        s2 = state.s2 + p2
        return State(state.p1, p2, state.s1, s2, turn)


def winner(state, min_score):
    if state.s1 >= min_score:
        return 0
    if state.s2 >= min_score:
        return 1
    return None


@cache
@collecting
def quantum_roll():
    for u, v, w in product(range(1, 4), repeat=3):
        yield u + v + w


def load(data):
    lines = data.splitlines()
    p1 = parse("Player 1 starting position: {pos:d}", lines[0])["pos"]
    p2 = parse("Player 2 starting position: {pos:d}", lines[1])["pos"]
    return p1, p2


if __name__ == "__main__":
    puzzle = Puzzle(year=2021, day=21)

    ans1 = part1(load(puzzle.input_data))
    # puzzle.answer_a = ans1
    ans2 = part2(load(puzzle.input_data))
    # puzzle.answer_b = ans2
