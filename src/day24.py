# Advent of Code 2021, Day 24
# (c) blu3r4y

from aocd.models import Puzzle
from funcy import collecting, print_calls

NUMBER_LENGTH = 14


@print_calls
def part1(instructions):
    inp = [9] * NUMBER_LENGTH

    facs = factors(instructions)
    for wi, wj, diff in restrictions(instructions, facs):
        # make sure that the dependent number is
        # AS LARGE AS POSSIBLE and still within the 1..9 range
        inp[wj] = min(9, inp[wi] - diff)
        inp[wi] = inp[wj] + diff

    # run MONAD once to check that it returns 0
    assert monad(facs, inp) == 0
    return "".join(map(str, inp))


@print_calls
def part2(instructions):
    inp = [1] * NUMBER_LENGTH

    facs = factors(instructions)
    for wi, wj, diff in restrictions(instructions, facs):
        # make sure that the dependent number is
        # AS SMALL AS POSSIBLE and still within the 1..9 range
        inp[wj] = max(1, inp[wi] - diff)
        inp[wi] = inp[wj] + diff

    # run MONAD once to check that it returns 0
    assert monad(facs, inp) == 0
    return "".join(map(str, inp))


@collecting
def restrictions(instructions, facs):
    stack = []
    for wi, (_, ax, ay) in enumerate(facs):
        if ax >= 0:
            # push: this will increase z
            stack.append((wi, ay))
        else:
            # pop: this will decrease z
            wj, jax = stack.pop()
            diff = jax + ax

            # word at wi must be word at wj + diff
            # for this pop to equal 'x == w - ax'
            # and therefore skip the next push
            yield (wi, wj, diff)


def monad(facs, stdin):
    z = 0

    for (dz, ax, ay), w in zip(facs, stdin):
        # both reverse-engineered cycles should compute the same
        r1 = cycle_rev1(dz, ax, ay, w, z)
        r2 = cycle_rev2(ax, ay, w, z)
        assert r1 == r2

        z = r1

    return z


def cycle_rev2(ax, ay, w, z):
    assert 1 <= w <= 9

    # pop from stack
    x = z % 26
    if ax < 0:
        z //= 26

    # skip next push (must hold)
    # this will keep z small
    if x == w - ax:
        return z

    # push to stack
    return 26 * z + w + ay


def cycle_rev1(dz, ax, ay, w, z):
    assert 1 <= w <= 9
    # inp w | mul x 0 | add x z | mod x 26 | div z {DIVZ} | add x {ADDX}
    x = (z % 26) + ax
    z = z // dz
    # eql x w | eql x 0
    x = 1 if x != w else 0
    # mul y 0 | add y 25 | mul y x | add y 1
    y = (25 * x) + 1
    # mul z y
    z = z * y
    # mul y 0 | add y {ADDY} | add y 9 | mul y x
    y = (w + ay) * x
    # add z y
    z = z + y
    return z


@collecting
def factors(instructions):
    for r in range(NUMBER_LENGTH):
        dz = instructions[18 * r + 4][2]
        ax = instructions[18 * r + 5][2]
        ay = instructions[18 * r + 15][2]

        assert (dz == 1 and ax >= 0) or (dz == 26 and ax < 0)

        yield (dz, ax, ay)


@collecting
def load(data):
    for line in data.splitlines():
        parts = line.split(" ")

        if line.startswith("inp"):
            # one-argument instruction
            op, a, b = (*parts, None)

        else:
            # two-argument instruction
            op, a, b = parts

            try:
                b = int(b)
            except ValueError:
                pass

        yield (op, a, b)


if __name__ == "__main__":
    puzzle = Puzzle(year=2021, day=24)

    ans1 = part1(load(puzzle.input_data))
    # puzzle.answer_a = ans1
    ans2 = part2(load(puzzle.input_data))
    # puzzle.answer_b = ans2
