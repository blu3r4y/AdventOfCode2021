# Advent of Code 2021, Day 22
# (c) blu3r4y

from itertools import permutations

import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from aocd.models import Puzzle
from funcy import print_calls
from parse import parse


@print_calls
def part1(steps):
    grid = np.zeros((101, 101, 101), dtype=int)

    for oxyz in steps:
        state, *xyz = oxyz
        x1, x2, y1, y2, z1, z2 = xyz

        x1, x2 = max(x1, -50), min(x2, 50)
        y1, y2 = max(y1, -50), min(y2, 50)
        z1, z2 = max(z1, -50), min(z2, 50)

        index = np.ix_(range(x1, x2 + 1), range(y1, y2 + 1), range(z1, z2 + 1))
        grid[index] = 1 if state == "on" else 0

    return grid.sum()


@print_calls
def part2(steps, plot=False):
    cubeset = CubeSet()

    for oxyz in steps:
        state, *xyz = oxyz
        x1, x2, y1, y2, z1, z2 = xyz

        # our cubeset assumes that endpoints are inclusive
        xyz_inclusive = x1, x2 + 1, y1, y2 + 1, z1, z2 + 1
        cubeset.assign(xyz_inclusive, state)

        if plot:
            cubeset.plot()

    return cubeset.volume()


###########################################################################


class CubeSet:
    def __init__(self):
        self.oncubes = set()

    def assign(self, xyz, state):
        xyz = tuple(xyz)

        # make room for the new cube xyz by clearing that space
        overlapping = {c for c in self.oncubes if CubeSet.overlap(c, xyz)}
        for overlap in overlapping:
            self.subtract(overlap, xyz)

        # should this actually be set?
        if state == "on":
            self.oncubes.add(xyz)

        # self.check_integrity()

    def subtract(self, a, b):
        # remove cube b from cube a, by splitting cube a
        ax1, ax2, ay1, ay2, az1, az2 = a
        bx1, bx2, by1, by2, bz1, bz2 = b

        # we split this one in half - remove it!
        self.oncubes.remove(a)

        # the two new splits of cube a
        # and the one that still overlaps with b
        s1, s2, sover = None, None, None

        xleft, xright = ax1 < bx1, ax2 > bx2
        yleft, yright = ay1 < by1, ay2 > by2
        zleft, zright = az1 < bz1, az2 > bz2

        # split in x possible2?
        if xleft or xright:
            mx = bx1 if xleft else bx2
            s1 = (ax1, mx, ay1, ay2, az1, az2)
            s2 = (mx, ax2, ay1, ay2, az1, az2)
            sover = s2 if xleft else s1

        # split in y possible?
        elif yleft or yright:
            my = by1 if yleft else by2
            s1 = (ax1, ax2, ay1, my, az1, az2)
            s2 = (ax1, ax2, my, ay2, az1, az2)
            sover = s2 if yleft else s1

        # split in z possible?
        elif zleft or zright:
            mz = bz1 if zleft else bz2
            s1 = (ax1, ax2, ay1, ay2, az1, mz)
            s2 = (ax1, ax2, ay1, ay2, mz, az2)
            sover = s2 if zleft else s1

        # nothing to split?
        else:
            return

        # decompose a into its two new splits
        self.oncubes.add(s1)
        self.oncubes.add(s2)

        # continue splitting the one that still overlaps
        self.subtract(sover, b)

    def volume(self):
        count = 0
        for cube in self.oncubes:
            xmin, xmax, ymin, ymax, zmin, zmax = cube
            count += (xmax - xmin) * (ymax - ymin) * (zmax - zmin)
        return count

    def check_integrity(self):
        for a, b in permutations(self.oncubes, 2):
            assert not CubeSet.overlap(a, b), f"{a} and {b} overlap"

    @staticmethod
    def overlap(a, b):
        # checks if two cubes a and b overlap
        ax1, ax2, ay1, ay2, az1, az2 = a
        bx1, bx2, by1, by2, bz1, bz2 = b

        xint = ax1 < bx2 and bx1 < ax2
        yint = ay1 < by2 and by1 < ay2
        zint = az1 < bz2 and bz1 < az2

        return xint and yint and zint

    @staticmethod
    def contains(a, b):
        # check if a (outer) contains b (inner)
        ax1, ax2, ay1, ay2, az1, az2 = a
        bx1, bx2, by1, by2, bz1, bz2 = b

        xcnt = ax1 <= bx1 and bx2 <= ax2
        ycnt = ay1 <= by1 and by2 <= ay2
        zcnt = az1 <= bz1 and bz2 <= az2

        return xcnt and ycnt and zcnt

    def plot(self):
        objects = []
        colors = px.colors.qualitative.Plotly
        for i, cube in enumerate(self.oncubes):
            xmin, xmax, ymin, ymax, zmin, zmax = cube

            # fmt: off
            vertices = [
                (xmin, ymin, zmin), (xmin, ymax, zmin), (xmax, ymax, zmin), (xmax, ymin, zmin),
                (xmin, ymin, zmax), (xmin, ymax, zmax), (xmax, ymax, zmax), (xmax, ymin, zmax),
            ]

            xs, ys, zs = zip(*vertices)
            color = colors[i % len(colors)]

            scatter = go.Scatter3d(
                x=xs, y=ys, z=zs,
                mode="markers", marker=dict(size=2, color="black"),
            )
            mesh = go.Mesh3d(
                x=xs, y=ys, z=zs,
                # cube mesh triangulation
                i=[7, 0, 0, 0, 4, 4, 6, 6, 4, 0, 3, 2],
                j=[3, 4, 1, 2, 5, 6, 5, 2, 0, 1, 6, 3],
                k=[0, 7, 2, 3, 6, 7, 1, 1, 5, 5, 7, 6],
                opacity=0.3, color=color, flatshading=True,
            )
            # fmt: on

            objects.append(scatter)
            objects.append(mesh)

        fig = go.Figure(data=objects)
        fig.update_layout(showlegend=False)
        fig.show()


###########################################################################


def load(data):
    steps = []

    for line in data.splitlines():
        oxyz = parse("{:w} x={:d}..{:d},y={:d}..{:d},z={:d}..{:d}", line).fixed
        steps.append(oxyz)

        # ensure correct axis orientation
        _, x1, x2, y1, y2, z1, z2 = oxyz
        assert x1 <= x2 and y1 <= y2 and z1 <= z2

    return steps


if __name__ == "__main__":
    puzzle = Puzzle(year=2021, day=22)

    ans1 = part1(load(puzzle.input_data))
    # puzzle.answer_a = ans1
    ans2 = part2(load(puzzle.input_data), plot=False)
    # puzzle.answer_b = ans2
