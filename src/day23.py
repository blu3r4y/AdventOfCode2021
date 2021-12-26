from queue import PriorityQueue

from aocd.models import Puzzle
from funcy import print_calls
from tqdm.auto import tqdm

# amphipods and their energy levels
AMPHIPODS = ("A", "B", "C", "D")
ENERGY = {"A": 1, "B": 10, "C": 100, "D": 1000}

# one room per amphipod
NUM_ROOMS = len(AMPHIPODS)

# hallway size and locations we shall not reach
HALLWAY_SIZE = 11
ILLEGAL_STOPS = (2, 4, 6, 8)

# type variables for step computation
TROOM, THALLWAY = 0, 1


@print_calls
def part1(state, debug=False):
    return solve(state, debug)


@print_calls
def part2(state, debug=False):
    # mutate state to include two new room levels
    ro = list(state.rooms)
    ro[0] = (ro[0][0], "D", "D", ro[0][1])
    ro[1] = (ro[1][0], "B", "C", ro[1][1])
    ro[2] = (ro[2][0], "A", "B", ro[2][1])
    ro[3] = (ro[3][0], "C", "A", ro[3][1])
    newstate = State(ro, state.hallway, roomdepth=4)

    return solve(newstate, debug)


def solve(state, debug=False):
    (total_cost, goal), parents = astar_search(state)
    assert goal is not None, "could not find goal state"

    if debug:
        # show the full path in debug mode
        for s in reconstruct_path(parents, start=state, goal=goal):
            print(s, end="\n\n")

    return total_cost


###########################################################################


class State:
    def __init__(self, rooms, hallway=None, roomdepth=2):
        self.rooms = tuple(rooms)
        self.hallway = tuple(hallway) if hallway else (None,) * HALLWAY_SIZE
        self.roomdepth = roomdepth

    def __hash__(self):
        return hash(self.rooms) ^ hash(self.hallway)

    def __eq__(self, other):
        return self.rooms == other.rooms and self.hallway == other.hallway

    def __lt__(self, other):
        return self.estimate_remaining_energy() < other.estimate_remaining_energy()

    def __repr__(self):
        theuristic = self.estimate_remaining_energy()
        tgoal = "GOAL" if self.is_goal() else f"≥ {theuristic} to goal"
        thall = "".join([h or "." for h in self.hallway])

        trooms = []
        for depth in range(self.roomdepth):
            amphs = (r[depth] if len(r) > depth else "." for r in self.rooms)
            trooms.append(" ".join(amphs))

        text = []
        text.append(f"State {tgoal}")
        text.append(f"{thall}")
        for troom in reversed(trooms):
            text.append(f"  {troom}")
        return "\n".join(text)

    ###########################################################################

    @staticmethod
    def get_hallway_position(r):
        # the hallway position for room r
        return 2 + 2 * r

    @staticmethod
    def get_destination_room(amph):
        # the room where the amphipod must move to
        return AMPHIPODS.index(amph)

    def get_steps(self, tstart, start, tend, end, admissible=False):
        # helper to compute the full number of steps from any start to any end
        # (in admissible mode, we will underestimate the osteps and isteps)
        assert tstart == TROOM or tstart == THALLWAY
        assert tend == TROOM or tend == THALLWAY
        assert not (tstart == THALLWAY and tend == THALLWAY)

        osteps, hsteps, isteps = 0, 0, 0
        hstart, hend = None, None
        depth = self.roomdepth + 1

        if tstart == TROOM:
            # steps out of start room
            assert 0 <= start <= NUM_ROOMS - 1
            osteps = depth - len(self.rooms[start]) if not admissible else 1
            hstart = State.get_hallway_position(start)
        else:
            assert 0 <= start <= HALLWAY_SIZE - 1
            hstart = start

        if tend == TROOM:
            # steps into end room
            assert 0 <= end <= NUM_ROOMS - 1
            isteps = depth - len(self.rooms[end]) if not admissible else 2
            hend = State.get_hallway_position(end)
        else:
            assert 0 <= end <= HALLWAY_SIZE - 1
            hend = end

        # steps in hallway
        hsteps = abs(hend - hstart) - 1
        if tend == THALLWAY:
            hsteps += 1

        return osteps + hsteps + isteps

    ###########################################################################

    def is_goal(self):
        # check if all amphipods are in their destinaton room
        for r in range(NUM_ROOMS):
            if not self.is_room_done(r):
                return False
        return True

    def is_room_done(self, r):
        # check if this room contains all amphipods of the correct type
        assert 0 <= r <= NUM_ROOMS - 1

        room = self.rooms[r]
        if len(room) != self.roomdepth:
            return False

        d = State.get_destination_room(room[0])
        return all(e == room[0] for e in room) and d == r

    def is_hallway_free(self, start, end, skipstart=False):
        # check if the hallway path from start to end is empty
        assert start != end
        s, e = (start, end + 1) if start < end else (end, start + 1)

        if skipstart:
            s = s + 1 if start < end else s
            e = e - 1 if start > end else e

        return all(pos is None for pos in self.hallway[s:e])

    def is_destination_ready(self, amph):
        # check if the destination is empty or occupied by the same amphipod
        room = self.rooms[self.get_destination_room(amph)]
        return len(room) == 0 or all(e == amph for e in room)

    ###########################################################################

    @staticmethod
    def get_energy(src, dst):
        # exact energy that a state transition from a to b did cost
        # (assumes that dst is a successor of src)
        if src == dst:
            return 0

        for energy, succ in src.successors():
            if succ == dst:
                return energy

        raise ValueError("dst is not a successor of src")

    def estimate_remaining_energy(self):
        # admissible heuristic for the remaining total energy to the goal state
        energy = 0

        for r, room in enumerate(self.rooms):
            blocked = False
            for depth, amph in enumerate(room):
                d = self.get_destination_room(amph)
                if d != r:
                    # assume direct move from here to destination room
                    blocked = True
                    nsteps = self.get_steps(TROOM, r, TROOM, d, admissible=True)
                    nsteps += self.roomdepth - 1 - depth  # estimate extra out steps
                    energy += ENERGY[amph] * nsteps

                elif d == r and blocked:
                    # assume that this amphipod 'steps out and in' once,
                    # to let the blocked amphipod on the lower levels leave
                    energy += ENERGY[amph] * (4 + 2 * (self.roomdepth - 1 - depth))

        for h, amph in enumerate(self.hallway):
            if amph is None:
                continue

            # assume direct move from hallway to destination room
            d = self.get_destination_room(amph)
            nsteps = self.get_steps(THALLWAY, h, TROOM, d, admissible=True)
            energy += ENERGY[amph] * nsteps

        return energy

    ###########################################################################

    def can_move_from_room(self, r):
        # can any amphipod in room r move to its destination room?
        assert 0 <= r <= NUM_ROOMS - 1

        room = self.rooms[r]
        if len(room) == 0:
            return False  # empty room

        amph = room[-1]
        if not self.is_destination_ready(amph):
            return False  # destination not ready

        d = self.get_destination_room(amph)
        start = State.get_hallway_position(r)
        end = State.get_hallway_position(d)
        if start == end or not self.is_hallway_free(start, end):
            return False  # path blocked

        return True

    def can_move_from_hallway(self, h):
        # can any amphipod in the hallway move to its destination room?
        assert 0 <= h <= HALLWAY_SIZE - 1

        amph = self.hallway[h]
        if amph is None:
            return False  # no amphipod at that hallway position

        if not self.is_destination_ready(amph):
            return False  # destination not ready

        d = self.get_destination_room(amph)
        end = State.get_hallway_position(d)
        if not self.is_hallway_free(h, end, skipstart=True):
            return False  # path blocked

        return True

    def can_move_to_hallway(self, r, h):
        # can any amphipod in room move to the hallway at hallpos?
        assert 0 <= r <= NUM_ROOMS - 1
        assert 0 <= h <= HALLWAY_SIZE - 1

        if h in ILLEGAL_STOPS:
            return False  # can not move here

        room = self.rooms[r]
        if len(room) == 0:
            return False  # empty room

        amph = room[-1]
        d = self.get_destination_room(amph)
        if all(e == amph for e in room) and d == r:
            return False  # what's here, is already at its destination

        start = State.get_hallway_position(r)
        if not self.is_hallway_free(start, h):
            return False  # path blocked

        return True

    ###########################################################################

    def move_from_room(self, r):
        # move amphipod in room r to its destination room
        assert 0 <= r <= NUM_ROOMS - 1

        amph = self.rooms[r][-1]
        d = self.get_destination_room(amph)
        nsteps = self.get_steps(TROOM, r, TROOM, d)

        # mutate to new state
        _rooms = list(self.rooms)
        _rooms[r] = _rooms[r][:-1]
        _rooms[d] = _rooms[d] + (amph,)
        energy = ENERGY[amph] * nsteps
        return energy, State(_rooms, self.hallway, self.roomdepth)

    def move_from_hallway(self, h):
        # move amphipod in the hallway at position h to its destination room
        assert 0 <= h <= HALLWAY_SIZE - 1

        amph = self.hallway[h]
        d = self.get_destination_room(amph)
        nsteps = self.get_steps(THALLWAY, h, TROOM, d)

        # mutate to new state
        _rooms, _hallway = list(self.rooms), list(self.hallway)
        _rooms[d] = _rooms[d] + (amph,)
        _hallway[h] = None
        energy = ENERGY[amph] * nsteps
        return energy, State(_rooms, _hallway, self.roomdepth)

    def move_to_hallway(self, r, h):
        # move amphipod in romm r to the hallway at position h
        assert 0 <= r <= NUM_ROOMS - 1
        assert 0 <= h <= HALLWAY_SIZE - 1

        amph = self.rooms[r][-1]
        nsteps = self.get_steps(TROOM, r, THALLWAY, h)

        # mutate to new state
        _rooms, _hallway = list(self.rooms), list(self.hallway)
        _rooms[r] = _rooms[r][:-1]
        _hallway[h] = amph
        energy = ENERGY[amph] * nsteps
        return energy, State(_rooms, _hallway, self.roomdepth)

    ###########################################################################

    def successors(self, debug=False):
        # compute all possible successor states
        # (in debug mode, only return the function signature)
        for r in range(NUM_ROOMS):
            if self.can_move_from_room(r):
                if debug:
                    yield f"move_from_room({r})"
                else:
                    yield self.move_from_room(r)

        for h in range(HALLWAY_SIZE):
            if self.can_move_from_hallway(h):
                if debug:
                    yield f"move_from_hallway({h})"
                else:
                    yield self.move_from_hallway(h)

        for r in range(NUM_ROOMS):
            for h in range(HALLWAY_SIZE):
                if self.can_move_to_hallway(r, h):
                    if debug:
                        yield f"move_to_hallway({r}, {h})"
                    else:
                        yield self.move_to_hallway(r, h)


###########################################################################


def astar_search(start):
    # perform A* search from start state to goal state
    openpq = PriorityQueue()
    openpq.put((0, start))
    closed = {start: 0}

    # remember parents for path reconstruction
    parents = {start: None}
    total_energy, goal = None, None

    with tqdm() as pbar:
        while not openpq.empty():
            total_energy, current = openpq.get()
            if current.is_goal():
                goal = current
                break

            pbar.set_postfix(total_energy=total_energy, refresh=False)
            pbar.update()

            for energy, succ in current.successors():
                new_energy = closed[current] + energy
                if succ not in closed or new_energy < closed[succ]:
                    parents[succ] = current
                    closed[succ] = new_energy
                    estimate = new_energy + succ.estimate_remaining_energy()
                    openpq.put((estimate, succ))

    return (total_energy, goal), parents


def reconstruct_path(parents, start, goal):
    # traverse parent relationship to reconstruct full solution path
    path, current = [], goal
    while current != start:
        path.append(current)
        current = parents[current]
    path.append(start)
    path.reverse()

    return path


def load(data):
    lines = data.splitlines()
    top, bot = lines[2][3:11:2], lines[3][3:11:2]
    rooms = zip(bot, top)
    return State(rooms)


if __name__ == "__main__":
    puzzle = Puzzle(year=2021, day=23)

    ans1 = part1(load(puzzle.input_data), debug=True)
    # puzzle.answer_a = ans1
    ans2 = part2(load(puzzle.input_data), debug=True)
    # puzzle.answer_b = ans2
