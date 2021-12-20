# Advent of Code 2021, Day 19
# (c) blu3r4y

from collections import defaultdict, deque
from functools import lru_cache
from itertools import product

from aocd.models import Puzzle
from funcy import collecting, print_calls
from parse import parse
from tqdm.auto import tqdm

ROTATIONS = [
    lambda x, y, z: (x, z, -y),
    lambda x, y, z: (-z, x, -y),
    lambda x, y, z: (-x, -z, -y),
    lambda x, y, z: (z, -x, -y),
    lambda x, y, z: (z, -y, x),
    lambda x, y, z: (y, z, x),
    lambda x, y, z: (-z, y, x),
    lambda x, y, z: (-y, -z, x),
    lambda x, y, z: (-y, x, z),
    lambda x, y, z: (-x, -y, z),
    lambda x, y, z: (y, -x, z),
    lambda x, y, z: (x, y, z),
    lambda x, y, z: (-z, -x, y),
    lambda x, y, z: (x, -z, y),
    lambda x, y, z: (z, x, y),
    lambda x, y, z: (-x, z, y),
    lambda x, y, z: (-x, y, -z),
    lambda x, y, z: (-y, -x, -z),
    lambda x, y, z: (x, -y, -z),
    lambda x, y, z: (y, x, -z),
    lambda x, y, z: (y, -z, -x),
    lambda x, y, z: (z, y, -x),
    lambda x, y, z: (-y, z, -x),
    lambda x, y, z: (-z, -y, -x),
]


@print_calls
def part1(scans):
    reference, _ = solve(scans)
    return len(reference)


@print_calls
def part2(scans):
    _, offsets = solve(scans)
    largest = 0

    # compute manhatte distance and store largest
    for (ax, ay, az), (bx, by, bz) in product(offsets, repeat=2):
        l1 = abs(ax - bx) + abs(ay - by) + abs(az - bz)
        largest = max(largest, l1)

    return largest


@lru_cache
def solve(scans, min_beacons=12):
    reference = set(scans[0])
    queue = deque(scans.keys())
    queue.remove(0)

    offsets = []

    with tqdm(total=len(queue)) as progress:
        # match scanner by scanner
        while queue:
            i = queue.pop()

            match = match_beacons(reference, scans[i], min_beacons)
            if not match:
                # no match found, re-visit this scanner at the end again
                queue.appendleft(i)
                continue

            # transform scanner beacons and merge them with the reference
            r, offset = match
            beacons = set(transform(scans[i], r, offset))
            reference.update(beacons)

            offsets.append(offset)
            progress.update(1)

    return reference, offsets


def transform(scan, rot, offset):
    # rotate and translate all points in scan
    dx, dy, dz = offset
    for s in scan:
        sx, sy, sz = ROTATIONS[rot](*s)
        yield sx + dx, sy + dy, sz + dz


def match_beacons(ascan, bscan, min_beacons):
    # rotate b in all different DoFs and try extracting the offset
    for r, rot in enumerate(ROTATIONS):
        brot = rotated(bscan, rot)
        offset = scanner_offset(ascan, brot, min_beacons)
        if offset:
            return r, offset


def scanner_offset(ascan, bscan, min_beacons):
    dists = defaultdict(set)
    for p1 in ascan:
        for p2 in bscan:
            # group by distance vectors
            # for all points p1 from a and p2 from b
            d = distance(p2, p1)
            dists[d].add((p1, p2))

            # enough equal vectors identify the scanner offset
            if len(dists[d]) >= min_beacons:
                return d


def distance(a, b):
    (ax, ay, az), (bx, by, bz) = a, b
    return bx - ax, by - ay, bz - az


@collecting
def rotated(scan, rot):
    for xyz in scan:
        yield rot(*xyz)


def load(data):
    blocks = data.split("\n\n")
    scanners = {}
    for i, block in enumerate(blocks):
        lines = block.split("\n")[1:]
        xyz = frozenset(tuple(parse("{:d},{:d},{:d}", e)) for e in lines)
        scanners[i] = xyz
    return frozendict(scanners)


class frozendict(dict):
    def __hash__(self):
        # primitive dict hash, needed for lru_cache on solve()
        return hash((frozenset(self.keys()), frozenset(self.values())))


if __name__ == "__main__":
    puzzle = Puzzle(year=2021, day=19)

    ans1 = part1(load(puzzle.input_data))
    # puzzle.answer_a = ans1
    ans2 = part2(load(puzzle.input_data))
    # puzzle.answer_b = ans2
