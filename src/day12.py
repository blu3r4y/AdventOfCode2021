# Advent of Code 2021, Day 12
# (c) blu3r4y

import networkx as nx
from aocd.models import Puzzle
from funcy import ilen, print_calls

START, END = "start", "end"


@print_calls
def part1(graph):
    return ilen(dfs(graph, [START]))


@print_calls
def part2(graph):
    return ilen(dfs(graph, [START], double_visit=True))


def dfs(g, path, double_visit=False):
    for succ in g.neighbors(path[-1]):
        # never go back to the start
        if succ == START:
            continue

        # allow visiting a small cave twice only if we
        # didn't visit any other small twice already
        if succ.islower() and succ in path:
            if not double_visit or visited_small_cave_twice(path):
                continue

        next_path = path.copy()
        next_path.append(succ)

        # do not recurse after we reached the end,
        # but, continue looking at other neigbors
        if succ == END:
            yield next_path
            continue

        # depth-first traversal of next neighbors
        for t in dfs(g, next_path, double_visit=double_visit):
            yield t


def visited_small_cave_twice(path):
    for p in path:
        if p.islower():
            if path.count(p) > 1:
                return True


def load(data):
    graph = nx.Graph()
    for line in data.splitlines():
        a, b = line.split("-")
        graph.add_edge(a, b)
    return graph


if __name__ == "__main__":
    puzzle = Puzzle(year=2021, day=12)

    ans1 = part1(load(puzzle.input_data))
    # puzzle.answer_a = ans1
    ans2 = part2(load(puzzle.input_data))
    # puzzle.answer_b = ans2
