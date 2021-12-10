# Advent of Code 2021, Day 10
# (c) blu3r4y

from aocd.models import Puzzle
from funcy import print_calls

STARTS = {"(": ")", "[": "]", "{": "}", "<": ">"}

SCORE_CORRUPT = {")": 3, "]": 57, "}": 1197, ">": 25137}
SCORE_INCOMPLETE = {")": 1, "]": 2, "}": 3, ">": 4}


@print_calls
def part1(data):
    result = 0
    for chunk in data:
        p = Parser(chunk)
        p.parse()
        result += p.corrupt

    return result


@print_calls
def part2(data):
    result = []
    for chunk in data:
        p = Parser(chunk)
        p.parse()

        # skip corrupt lines now
        if p.corrupt > 0:
            continue

        score = autocomplete_score(p.postfix)
        result.append(score)

    # get mid point in sorted result list
    result = sorted(result)
    mid = len(result) // 2
    return result[mid]


def autocomplete_score(postfix):
    score = 0
    for ch in postfix:
        score *= 5
        score += SCORE_INCOMPLETE[ch]
    return score


class Parser:
    def __init__(self, chunk, debug=False):
        self.chunk = chunk
        self.debug = debug  # verbose debug output
        self.pos = 0  # scanner position
        self.corrupt = 0  # corruption score
        self.postfix = ""  # autocomplete for incomplete line

    @property
    def eof(self):
        return self.pos == len(self.chunk)

    @property
    def peek(self):
        if self.eof:
            return None

        # get next character without consuming
        return self.chunk[self.pos]

    def scan(self):
        if self.eof:
            return None

        # consume and get next character
        ch = self.chunk[self.pos]
        self.pos += 1
        return ch

    def parse(self):
        while self.peek in STARTS:
            self.parse_chunk()

    def parse_chunk(self):
        # parse start character
        start = self.scan()

        assert start in STARTS, f"expected start, not {start} @{self.pos - 1}"
        match = STARTS[start]

        # parse inner chunk if available
        ch = self.peek
        if ch in STARTS:
            self.parse()

        # parse correct or wrong close character
        close = self.scan()
        if close != match:
            if close:
                self.corrupt += SCORE_CORRUPT[close]
                self._debug(f"CORRUPT: expected {match}, got {close} @{self.pos - 1}")
            else:
                self.postfix += match
                self._debug(f"INCOMPLETE: expected {match}, got EOF @{self.pos - 1}")

    def _debug(self, line):
        if self.debug:
            print(line)


def load(data):
    return data.split("\n")


if __name__ == "__main__":
    puzzle = Puzzle(year=2021, day=10)

    ans1 = part1(load(puzzle.input_data))
    # puzzle.answer_a = ans1
    ans2 = part2(load(puzzle.input_data))
    # puzzle.answer_b = ans2
