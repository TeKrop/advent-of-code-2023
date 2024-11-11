from enum import StrEnum
from functools import cached_property
from itertools import cycle
from math import lcm

from scripts.utils import AbstractPuzzleSolver, Multiton


# Use the Multiton pattern, as a Node will always be the same
class Node(Multiton):
    def __init__(self, name: str):
        self.name = name

    def __repr__(self) -> str:
        return self.name

    @cached_property
    def is_starting_node(self) -> bool:
        return self.name.endswith("A")

    @cached_property
    def is_finish_node(self) -> bool:
        return self.name.endswith("Z")


class PuzzleSolver(AbstractPuzzleSolver):
    ###########################
    # DAY 8 - Common Part
    ###########################
    @cached_property
    def directions_line(self):
        return self.lines[0]

    @cached_property
    def directions(self) -> list["Direction"]:
        return [Direction(letter) for letter in self.directions_line]

    @cached_property
    def network(self) -> dict[str, "NetworkLine"]:
        return {
            network_line.start_node: network_line
            for line in self.lines[2::]
            if (network_line := NetworkLine(line))
        }

    ###########################
    # DAY 8 - First Part
    ###########################
    starting_node: str = Node("AAA")
    finish_node: str = Node("ZZZ")

    def _solve_first_part(self) -> int:
        nb_steps = 0
        current_node = self.starting_node
        for direction in cycle(self.directions):
            # Travel through the network
            current_node = self.network[current_node][direction]
            # Increase number of steps
            nb_steps += 1
            # If we arrived on ZZZ, it's finished
            if current_node == self.finish_node:
                break

        return nb_steps

    ###########################
    # DAY 8 - Second Part
    ###########################
    @cached_property
    def starting_nodes(self) -> list[str]:
        return [node for node in self.network.keys() if node.is_starting_node]

    def _solve_second_part(self) -> int:
        # Find the steps at which the starting nodes arrives on a Z
        finish_steps: set[int] = set()

        for starting_node in self.starting_nodes:
            current_node = starting_node
            nb_steps = 0

            for direction in cycle(self.directions):
                # Travel through the network
                current_node = self.network[current_node][direction]
                # Increase number of steps
                nb_steps += 1
                # If we're on a finish node, we keep track of it
                # and we stop the exploration for this node
                if current_node.is_finish_node:
                    finish_steps.add(nb_steps)
                    break

        # Calculate the lower common multiple for all of
        # these, this is the number we're interested in
        return lcm(*finish_steps)


class Direction(StrEnum):
    LEFT = "L"
    RIGHT = "R"


class NetworkLine:
    start_node: Node
    left_node: Node
    right_node: Node

    def __init__(self, line: str):
        start, directions = [text.strip() for text in line.split("=")]
        self.start_node = Node(start)

        directions = directions.lstrip("(").rstrip(")")
        self.left_node, self.right_node = [
            Node(text.strip()) for text in directions.split(",")
        ]

    def __repr__(self) -> str:
        return (
            f"NetworkLine("
            f"start={self.start_node},"
            f"left={self.left_node},"
            f"right={self.right_node})"
        )

    def __getitem__(self, direction: Direction) -> Node:
        match direction:
            case Direction.LEFT:
                return self.left_node
            case Direction.RIGHT:
                return self.right_node
            case _:
                raise ValueError("Invalid direction")
