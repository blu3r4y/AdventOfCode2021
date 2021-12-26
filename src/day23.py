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


class State:
    def __init__(self, rooms, hallway=None):
        self.rooms = tuple(rooms)
        self.hallway = tuple(hallway) if hallway else (None,) * HALLWAY_SIZE

    def __hash__(self):
        return hash(self.rooms) ^ hash(self.hallway)

    def __eq__(self, other):
        return self.rooms == other.rooms and self.hallway == other.hallway

    def __lt__(self, other):
        return self.estimate_remaining_energy() < other.estimate_remaining_energy()

    def __repr__(self):
        theuristic = self.estimate_remaining_energy()
        tgoal = "GOAL" if self.is_goal() else f"~ {theuristic} to goal"
        thall = "".join([h or "." for h in self.hallway])
        trooms0 = " ".join(r[0] if len(r) > 0 else "." for r in self.rooms)
        trooms1 = " ".join(r[1] if len(r) > 1 else "." for r in self.rooms)

        text = []
        text.append(f"State {tgoal}")
        text.append(f"{thall}")
        text.append(f"  {trooms1}")
        text.append(f"  {trooms0}")
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
        assert tstart == "room" or tstart == "hallway"
        assert tend == "room" or tend == "hallway"
        assert not (tstart == "hallway" and tend == "hallway")

        osteps, hsteps, isteps = 0, 0, 0
        hstart, hend = None, None

        if tstart == "room":
            # steps out of start room
            assert 0 <= start <= NUM_ROOMS - 1
            osteps = 3 - len(self.rooms[start]) if not admissible else 1
            hstart = State.get_hallway_position(start)
        else:
            assert 0 <= start <= HALLWAY_SIZE - 1
            hstart = start

        if tend == "room":
            # steps into end room
            assert 0 <= end <= NUM_ROOMS - 1
            isteps = 3 - len(self.rooms[end]) if not admissible else 2
            hend = State.get_hallway_position(end)
        else:
            assert 0 <= end <= HALLWAY_SIZE - 1
            hend = end

        # steps in hallway
        hsteps = abs(hend - hstart) - 1
        if tend == "hallway":
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
        if len(room) != 2:
            return False

        bot, top = room
        d = State.get_destination_room(room[0])
        return bot == top and d == r

    def is_hallway_free(self, start, end, skipstart=False):
        # check if the hallway path from start to end is empty
        assert start != end
        s, e = (start, end + 1) if start < end else (end, start + 1)

        if skipstart:
            s = s + 1 if start < end else s
            e = e - 1 if start > end else e

        # print(f"hallway [{s:2d} : {e:2d}]", self.hallway[s:e])
        return all(pos is None for pos in self.hallway[s:e])

    def is_destination_ready(self, amph):
        # check if the destination is empty or occupied by the same amphipod
        room = self.rooms[self.get_destination_room(amph)]
        return len(room) == 0 or (len(room) == 1 and room[0] == amph)

    ###########################################################################

    @staticmethod
    def get_energy(src, dst):
        # compute exact cost from a to b
        # where b is known the be a successor of a
        if src == dst:
            return 0

        for energy, succ in src.successors():
            if succ == dst:
                return energy

    def estimate_remaining_energy(self):
        # admissible heuristic for the remaining total energy to the goal state
        cost = 0

        for r, room in enumerate(self.rooms):
            if len(room) == 0:
                continue  # no amphipods in room

            # estimate for bottom amphipod in room
            amph0, d0 = room[0], self.get_destination_room(room[0])
            if d0 != r:
                nsteps = self.get_steps("room", r, "room", d0, admissible=True)
                cost += ENERGY[amph0] * nsteps

            if len(room) == 1:
                continue  # only one amphipod in room

            # estimate for top amphipod in room
            amph1, d1 = room[1], self.get_destination_room(room[1])
            if d1 == r and d0 != r:
                cost += ENERGY[amph1] * 4  # make room once (2 out, 2 in)
            elif d1 != r:
                nsteps = self.get_steps("room", r, "room", d1, admissible=True)
                cost += ENERGY[amph1] * nsteps

        for h, amph in enumerate(self.hallway):
            if amph is None:
                continue

            d = self.get_destination_room(amph)
            nsteps = self.get_steps("hallway", h, "room", d, admissible=True)
            cost += ENERGY[amph] * nsteps

        return cost

    ###########################################################################

    def can_move_from_room(self, r):
        # can any amphipod in room r move to its destination room?
        assert 0 <= r <= NUM_ROOMS - 1

        if len(self.rooms[r]) == 0:
            return False  # empty room

        amph = self.rooms[r][-1]
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

        if self.hallway[h] is None:
            return False  # no amphipod at that hallway position

        amph = self.hallway[h]
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

        if len(self.rooms[r]) == 0:
            return False  # empty room

        if self.is_room_done(r):
            return False  # amphipods reached their destination

        amph = self.rooms[r][-1]
        d = self.get_destination_room(amph)
        if len(self.rooms[r]) == 1 and d == r:
            return False  # the one amphipod is already in its destination

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
        nsteps = self.get_steps("room", r, "room", d)

        # mutate to new state
        _rooms = list(self.rooms)
        _rooms[r] = _rooms[r][:-1]
        _rooms[d] = _rooms[d] + (amph,)
        energy = ENERGY[amph] * nsteps
        return energy, State(_rooms, self.hallway)

    def move_from_hallway(self, h):
        # move amphipod in the hallway at position h to its destination room
        assert 0 <= h <= HALLWAY_SIZE - 1

        amph = self.hallway[h]
        d = self.get_destination_room(amph)
        nsteps = self.get_steps("hallway", h, "room", d)

        # mutate to new state
        _rooms, _hallway = list(self.rooms), list(self.hallway)
        _rooms[d] = _rooms[d] + (amph,)
        _hallway[h] = None
        energy = ENERGY[amph] * nsteps
        return energy, State(_rooms, _hallway)

    def move_to_hallway(self, r, h):
        # move amphipod in romm r to the hallway at position h
        assert 0 <= r <= NUM_ROOMS - 1
        assert 0 <= h <= HALLWAY_SIZE - 1

        amph = self.rooms[r][-1]
        nsteps = self.get_steps("room", r, "hallway", h)

        # mutate to new state
        _rooms, _hallway = list(self.rooms), list(self.hallway)
        _rooms[r] = _rooms[r][:-1]
        _hallway[h] = amph
        energy = ENERGY[amph] * nsteps
        return energy, State(_rooms, _hallway)

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


@print_calls
def part1(state, debug=False):
    (total_cost, goal), parents = astar_search(state)

    if debug:
        # show the full path in debug mode
        for s in reconstruct_path(parents, start=state, goal=goal):
            print(s)
            print()

    return total_cost


def astar_search(start):
    # perform A* search from start state to goal state
    openpq = PriorityQueue()
    openpq.put((0, start))
    closed = {start: 0}

    # remember parents for path reconstruction
    parents = {start: None}
    total_cost, goal = None, None

    with tqdm() as pbar:
        while not openpq.empty():
            total_cost, current = openpq.get()
            if current.is_goal():
                goal = current
                break

            pbar.set_postfix(total_cost=total_cost, refresh=False)
            pbar.update()

            for energy, succ in current.successors():
                new_energy = closed[current] + energy
                if succ not in closed or new_energy < closed[succ]:
                    parents[succ] = current
                    closed[succ] = new_energy
                    estimate = new_energy + succ.estimate_remaining_energy()
                    openpq.put((estimate, succ))

    return (total_cost, goal), parents


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
    # ans2 = part2(load(puzzle.input_data))
    # puzzle.answer_b = ans2
