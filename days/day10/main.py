from dataclasses import dataclass
from functools import cached_property
from typing import Iterable

from scripts.utils import AbstractPuzzleSolver


class PuzzleSolver(AbstractPuzzleSolver):
    ###########################
    # DAY 10 - Common Part
    ###########################
    pipeline: "Pipeline"

    def solve(self) -> tuple[int, int]:
        self.pipeline = Pipeline(self.lines)
        return super().solve()

    ###########################
    # DAY 10 - First Part
    ###########################

    def _solve_first_part(self) -> int:
        return self.__get_farthest_distance_from_animal()

    def __get_farthest_distance_from_animal(self) -> int:
        return round(len(self.pipeline.main_loop) / 2)

    ###########################
    # DAY 10 - Second Part
    ###########################

    # Current line number when exploring the pipeline
    current_line: int | None = None

    # Number of times we hit the loop, reset in new lines
    nb_hits: int = 0

    # Memorize the current connection we made in order to ignore
    # continuous lines when counting. A straight line coming from north
    # and then going back to north doesn't count as a hit
    current_connection: "Connection" = None

    def _solve_second_part(self) -> int:
        return self.__count_tiles_inside_loop()

    def __count_tiles_inside_loop(self) -> int:
        """Count the tiles inside the loop and return it.

        In order to do this, we're going to use the ray casting algorithm by
        going from left to right, line by line. Depending on the number of
        times we pass through the main loop, we'll know if we're inside (odd
        number) or outside the loop (even number).
        """

        # Counter of inside tiles
        nb_tiles_inside_loop = 0

        for position, pipe in self.pipeline.pipes.items():
            # If we're on a new line, reset state variables
            if self.current_line != position[0]:
                self.__reset_exploration_state(position[0])

            # If the pipe is not in the main loop, check the number of
            # hits in order to know if it's inside the loop or not
            if pipe not in self.pipeline.main_loop:
                # If we hit the loop an odd number of times, we're inside it.
                # We just have to add the modulo 2 of number of hits.
                nb_tiles_inside_loop += self.nb_hits % 2
                continue

            # We're counting the current pipe as a hit
            self.nb_hits += 1

            # Now we check if the previous pipe was connected to the current one
            # and was in the main loop. If that's the case, this pipe doesn't
            # count. If not, we don't have any connection.
            previous_pipe = pipe.west_pipe
            if (
                previous_pipe
                and previous_pipe in self.pipeline.main_loop
                and previous_pipe in pipe.neighbours
            ):
                self.nb_hits -= 1
            else:
                self.last_connection = None

            # If the current pipe as at least a north or south connection,
            # we must check the last connection in order to know if we should
            # ignore it or not
            if pipe.connection.north or pipe.connection.south:
                # If we didn't have a connection yet, store the current
                if not self.last_connection:
                    self.last_connection = pipe.connection
                    continue

                # Else, make the check, and ignore current pipe if we're
                # going in the same direction than the previous connection
                if (
                    pipe.connection.north == self.last_connection.north
                    or pipe.connection.south == self.last_connection.south
                ):
                    self.nb_hits -= 1

                # In both ways, we don't have a connection anymore, reset
                self.last_connection = None

        return nb_tiles_inside_loop

    def __reset_exploration_state(self, line_number: int) -> None:
        self.current_line = line_number
        self.nb_hits = 0
        self.last_connection = None


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

    def __repr__(self):
        return str(self.connection)

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
    def neighbours(self) -> list["Pipe"]:
        return list(self.__get_neighbours())

    def __get_neighbours(self) -> Iterable["Pipe"]:
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
