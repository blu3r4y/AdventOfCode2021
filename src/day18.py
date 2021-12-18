# Advent of Code 2021, Day 18
# (c) blu3r4y

from copy import deepcopy
from functools import reduce
from math import ceil, floor
from operator import add

from anytree import NodeMixin, PreOrderIter, RenderTree
from aocd.models import Puzzle
from funcy import lmap, print_calls, with_next, with_prev
from tqdm.auto import tqdm

DEBUG_MODE = False


@print_calls
def part1(snails):
    result = reduce(add, snails)
    return result.magnitude


@print_calls
def part2(snails):
    size = len(snails)
    largest = -1
    for i in tqdm(range(size)):
        for j in range(size):
            if i != j:
                # perform deep copy because of my mutable tree transforms
                # not great, but still with an acceptable execution time ...
                a1, a2 = deepcopy(snails[i]), deepcopy(snails[i])
                b1, b2 = deepcopy(snails[j]), deepcopy(snails[j])

                mag1 = (a1 + b1).magnitude
                mag2 = (b2 + a2).magnitude
                largest = max(largest, max(mag1, mag2))

    return largest


class SnailNode(NodeMixin):
    def __init__(self, num=None, parent=None, children=None):
        self.num = num
        self.parent = parent

        if children:
            assert len(children) == 2
            self.children = children

    def reduce(self):
        while True:
            match = False

            # 1.) explode left-most pair at depth 4
            for node in PreOrderIter(self):
                if node.is_leaf_pair and node.depth == 4:
                    node.explode()
                    match = True
                    break

            # explode happened - go to start of ruleset
            if match:
                continue

            # 2.) split left-most regular number greater than 10
            for node in PreOrderIter(self):
                if node.is_leaf and node.num >= 10:
                    node.split()
                    match = True
                    break

            # no more action applied, we are done reducing
            if not match:
                break

    def explode(self):
        _debug_self = str(self)

        assert self.depth == 4
        assert self.is_leaf_pair
        left, right = self.children

        # find closest left and right leaf and add to their values
        closeleft, closeright = left.closest_left(), right.closest_right()

        if closeleft:
            closeleft.num += left.num
        if closeright:
            closeright.num += right.num

        # replace this with 0 and drop children
        self.num = 0
        self.children = []

        debug("after explode", self.root, "@", _debug_self)

    def split(self):
        _debug_self = str(self)

        assert self.is_leaf

        # transform to up- and down-rounded nodes
        a, b = floor(self.num / 2), ceil(self.num / 2)
        a, b = SnailNode(a), SnailNode(b)

        # replace this with a pair
        self.num = None
        self.children = [a, b]

        debug("after split", self.root, "@", _debug_self)

    def closest_left(self):
        return self.closest_sibling(with_prev)

    def closest_right(self):
        return self.closest_sibling(with_next)

    def closest_sibling(self, window):
        assert self.is_leaf

        # iterate over all nodes in pre-order and return previous or next node
        order = PreOrderIter(self.root, filter_=lambda n: n.is_leaf)
        for node, other in window(order):
            if node == self:
                return other

    @property
    def is_leaf_pair(self):
        if not self.children:
            return False

        # check if this pair only contains plain numbers (i.e, leaves)
        left, right = self.children
        return left.is_leaf and right.is_leaf

    @property
    def magnitude(self):
        if self.is_leaf:
            return self.num

        left, right = self.children
        return 3 * left.magnitude + 2 * right.magnitude

    def __add__(self, other):
        debug()
        debug("add:", self, "+", other)

        root = SnailNode(children=[self, other])
        root.reduce()
        return root

    def __repr__(self):
        if not self.children:
            return str(self.num)
        return "[" + ",".join(map(repr, self.children)) + "]"

    def render(self):
        # render tree for debugging
        print(RenderTree(self))


def load(data):
    return lmap(load_line, data.splitlines())


def load_line(line):
    # this is super dirty, but it was just too tempting ;)
    val = eval(line.replace("[", "(").replace("]", ")"))

    def _transform(val):
        if isinstance(val, tuple):
            a = _transform(val[0])
            b = _transform(val[1])
            return SnailNode(children=[a, b])
        else:
            return SnailNode(val)

    return _transform(val)


def debug(*args):
    if DEBUG_MODE:
        print(*args)


if __name__ == "__main__":
    puzzle = Puzzle(year=2021, day=18)

    ans1 = part1(load(puzzle.input_data))
    # puzzle.answer_a = ans1
    ans2 = part2(load(puzzle.input_data))
    # puzzle.answer_b = ans2
