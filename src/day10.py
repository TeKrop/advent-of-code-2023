from dataclasses import dataclass
from functools import cached_property
from typing import Iterable

from .utils import AbstractPuzzleSolver


class PuzzleSolver(AbstractPuzzleSolver):
    ###########################
    # DAY 10 - First Part
    ###########################

    def _solve_first_part(self) -> int:
        pipeline = Pipeline(self.lines)
        return self.__get_farthest_distance_from_animal(pipeline)

    @staticmethod
    def __get_farthest_distance_from_animal(pipeline: "Pipeline"):
        return round(len(pipeline.main_loop) / 2)

    ###########################
    # DAY 10 - Second Part
    ###########################

    def _solve_second_part(self) -> int:
        return None


@dataclass
class Connection:
    north: bool = False
    east: bool = False
    south: bool = False
    west: bool = False


class Pipe:
    symbol: str
    is_animal: bool = False

    # Neighbour pipes, to be computed
    north_pipe: "Pipe" = None
    east_pipe: "Pipe" = None
    south_pipe: "Pipe" = None
    west_pipe: "Pipe" = None

    def __init__(self, char: str):
        self.symbol = char
        self.is_animal = self.symbol == "S"

    @cached_property
    def connection(self) -> Connection | None:
        match self.symbol:
            case "|":  # vertical pipe
                return Connection(north=True, south=True)
            case "-":  # horizontal pipe
                return Connection(west=True, east=True)
            case "L":  # 90-degree bend NE
                return Connection(north=True, east=True)
            case "J":  # 90-degree bend NW
                return Connection(north=True, west=True)
            case "7":  # 90-degree bend SW
                return Connection(south=True, west=True)
            case "F":  # 90-degree bend SE
                return Connection(south=True, east=True)
            case ".":  # No pipe, no connection
                return Connection()
            case "S":  # animal starting position, compute connection
                return self.__compute_animal_connection()
            case _:
                raise ValueError("Unknown pipe type")

    @cached_property
    def neighbours(self) -> Iterable["Pipe"]:
        if self.connection.north and self.north_pipe.connection.south:
            yield self.north_pipe

        if self.connection.east and self.east_pipe.connection.west:
            yield self.east_pipe

        if self.connection.south and self.south_pipe.connection.north:
            yield self.south_pipe

        if self.connection.west and self.west_pipe.connection.east:
            yield self.west_pipe

    def __compute_animal_connection(self) -> Connection:
        return Connection(
            north=bool(self.north_pipe and self.north_pipe.connection.south),
            east=bool(self.east_pipe and self.east_pipe.connection.west),
            south=bool(self.south_pipe and self.south_pipe.connection.north),
            west=bool(self.west_pipe and self.west_pipe.connection.east),
        )


class Pipeline:
    pipes: dict[tuple[int, int], Pipe]

    def __init__(self, lines: list[str]):
        # Initialize pipes grid
        self.pipes = {
            (x, y): Pipe(symbol)
            for x, line in enumerate(lines)
            for y, symbol in enumerate(line)
        }

        # Compute pipes connections
        for position, pipe in self.pipes.items():
            x, y = position
            pipe.north_pipe = self.pipes.get((x - 1, y))
            pipe.east_pipe = self.pipes.get((x, y + 1))
            pipe.south_pipe = self.pipes.get((x + 1, y))
            pipe.west_pipe = self.pipes.get((x, y - 1))

    def __getitem__(self, key: tuple[int, int]):
        return self.pipes[key]

    def __len__(self):
        return len(self.pipes)

    @cached_property
    def animal_pipe(self) -> Pipe:
        return next(pipe for pipe in self.pipes.values() if pipe.is_animal)

    @cached_property
    def main_loop(self) -> list[Pipe]:
        main_loop = [self.animal_pipe]

        # Start from it and count until we reach the animal pipe again
        previous_pipe = None
        current_pipe = self.animal_pipe

        # Infinite loop until we reach the animal pipe again, as we know for
        # sure we will encounter it again
        while True:
            # Decide about the next pipe depending on the one
            # we come from, we don't want to go back and forth
            next_pipe = next(
                neighbour
                for neighbour in current_pipe.neighbours
                if neighbour != previous_pipe
            )

            # If we reached the animal pipe again, end of the loop
            if next_pipe == self.animal_pipe:
                break

            # Add the next pipe into the main loop
            main_loop.append(next_pipe)

            # Update looping pipe references
            previous_pipe, current_pipe = current_pipe, next_pipe

        return main_loop
