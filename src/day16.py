# Advent of Code 2021, Day 16
# (c) blu3r4y

from collections import namedtuple
from functools import reduce
from operator import mul

from aocd.models import Puzzle
from bitarray import bitarray
from funcy import print_calls

Packet = namedtuple("Packet", "i version type value")

DEBUG_MODE = False


@print_calls
def part1(bits):
    packet = parse_packet(bits, perform_ops=False)

    def _sum_version(pkt):
        if isinstance(pkt.value, list):
            return pkt.version + sum(_sum_version(p) for p in pkt.value)
        else:
            return pkt.version

    return _sum_version(packet)


@print_calls
def part2(bits):
    packet = parse_packet(bits, perform_ops=True)
    return packet.value


def parse_packet(bits, i=0, perform_ops=True):
    _, _, type_id = parse_header(bits, i)
    if type_id == 4:
        return parse_literal(bits, i, perform_ops)
    else:
        return parse_operator(bits, i, perform_ops)


def parse_header(bits, i=0):
    version = integer(bits[i : (i + 3)])
    i += 3
    type_id = integer(bits[i : (i + 3)])
    i += 3

    return i, version, type_id


def parse_literal(bits, i=0, perform_ops=True):
    i, version, type_id = parse_header(bits, i)
    assert type_id == 4, f"expected type == 4, got {type_id} <{bin(type_id)}>"

    debug(". [lit] version:", version)
    debug(". [lit] type:", version)

    # parse literal blocks
    value = bitarray()
    while True:
        part = bits[(i + 1) : (i + 5)]
        value.extend(part)
        i += 5

        # last block indicator (before increment consumed it)
        if bits[i - 5] == 0:
            break

    pkt = Packet(i, version, type_id, integer(value))
    debug("parsed literal:", pkt)
    return pkt


def parse_operator(bits, i=0, perform_ops=True):
    i, version, type_id = parse_header(bits, i)
    assert type_id != 4, f"expected type != 4, got {type_id} <{bin(type_id)}>"

    debug(". [op] version:", version)
    debug(". [op] type:", version)

    # length type id specifies mode 0 or 1
    length_type = bits[i]
    debug(". [op] length type id:", length_type)
    i += 1

    packets = []

    # mode 0 - next 15 represent total length
    if length_type == 0:
        subpacket_length = integer(bits[i : (i + 15)])
        debug(". [op] [mod 0] subpacket length:", subpacket_length)
        i += 15

        j = i
        while j < i + subpacket_length:
            pkt = parse_packet(bits, j, perform_ops)
            packets.append(pkt)
            j = pkt.i

        # advance, we parsed all subpackets up to that length
        assert j == i + subpacket_length
        i = j

    # mode 1 - next 11 represent number of sub-packets
    elif length_type == 1:
        num_subpackets = integer(bits[i : (i + 11)])
        debug(". [op] [mod 1] number of subpackets:", num_subpackets)
        i += 11

        n = 0
        while n < num_subpackets:
            pkt = parse_packet(bits, i, perform_ops)
            packets.append(pkt)
            i = pkt.i
            n += 1

    # perform operations for part 2 only
    value = perform_operation(type_id, packets) if perform_ops else packets
    pkt = Packet(i, version, type_id, value)
    debug("parsed operator result:", pkt)
    return pkt


def perform_operation(type_id, pkts):
    if type_id == 0:
        return sum(p.value for p in pkts)
    elif type_id == 1:
        return reduce(mul, (p.value for p in pkts))
    elif type_id == 2:
        return min(p.value for p in pkts)
    elif type_id == 3:
        return max(p.value for p in pkts)
    elif type_id == 5:
        assert len(pkts) == 2
        return 1 if pkts[0].value > pkts[1].value else 0
    elif type_id == 6:
        assert len(pkts) == 2
        return 1 if pkts[0].value < pkts[1].value else 0
    elif type_id == 7:
        assert len(pkts) == 2
        return 1 if pkts[0].value == pkts[1].value else 0

    raise Exception(f"unknown packet type {type_id} for packets {pkts}")


def load(data):
    # convert hex number to bitarray
    num = bin(int(data.strip(), 16))
    bits = bitarray(num[2:])

    # look up how many padding bits there are
    pad = bits.buffer_info()[3]
    bits = bitarray("0" * pad) + bits

    return bits


def integer(bits):
    return int(bits.to01(), 2)


def debug(*args):
    if DEBUG_MODE:
        print(*args)


if __name__ == "__main__":
    puzzle = Puzzle(year=2021, day=16)

    ans1 = part1(load(puzzle.input_data))
    # puzzle.answer_a = ans1
    ans2 = part2(load(puzzle.input_data))
    # puzzle.answer_b = ans2
