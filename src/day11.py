from dataclasses import dataclass, field
from itertools import combinations, count

from .utils import AbstractPuzzleSolver

EMPTY_SPACE_SYMBOL = "."
GALAXY_SYMBOL = "#"


class PuzzleSolver(AbstractPuzzleSolver):
    ###########################
    # DAY 11 - Common Part
    ###########################
    universe: "Universe"

    ###########################
    # DAY 11 - First Part
    ###########################

    def _solve_first_part(self) -> int:
        # First, create the universe and expand it
        self.universe = Universe(self.lines)
        self.universe.expand()

        # Create pairs of galaxies
        galaxy_pairs = combinations(self.universe.galaxies, 2)

        # Return the sum of their shortest path length
        return sum(
            self.__get_shortest_path_length(galaxy_pair) for galaxy_pair in galaxy_pairs
        )

    def __get_shortest_path_length(self, galaxy_pair: tuple["Galaxy", "Galaxy"]) -> int:
        """The shortest past, by only going up/right/down/left, is just the sum of
        the absolute value of difference between coordinates.
        """
        first_galaxy, second_galaxy = galaxy_pair
        y_diff = abs(second_galaxy.pos.y - first_galaxy.pos.y)
        x_diff = abs(second_galaxy.pos.x - first_galaxy.pos.x)
        return x_diff + y_diff

    ###########################
    # DAY 11 - Second Part
    ###########################

    def _solve_second_part(self) -> int:
        return None


@dataclass
class Position:
    x: int
    y: int


@dataclass
class Galaxy:
    identifier: int = field(default_factory=count().__next__, init=False)
    pos: Position


class Universe:
    data: list[list[str]]

    def __init__(self, lines: list[str]):
        self.data = [[char for char in line] for line in lines]

    def __repr__(self):
        return "\n".join("".join(line) for line in self.data)

    @property
    def galaxies(self) -> list[Galaxy]:
        return [
            Galaxy(pos=Position(line_idx, column_idx))
            for line_idx, line in enumerate(self.data)
            for column_idx, char in enumerate(line)
            if char == GALAXY_SYMBOL
        ]

    def expand(self) -> None:
        # First, retrieve the lines and columns to expand
        lines_to_expand, columns_to_expand = self.__get_empty_columns_and_lines()

        # Then, create a whole new expanded universe and replace current one
        universe_data: list[list[str]] = []

        for line_idx, line in enumerate(self.data):
            # Construct a new universe line column per column
            new_line: list[str] = []
            for column_idx, char in enumerate(line):
                new_line.append(char)
                # If the column must be expanded, add a new one
                if column_idx in columns_to_expand:
                    new_line.append(EMPTY_SPACE_SYMBOL)

            # Add the new line to the universe
            universe_data.append(new_line)

            # If the line must be expanded, add a new line again
            if line_idx in lines_to_expand:
                universe_data.append(new_line)

        self.data = universe_data

    def __get_empty_columns_and_lines(self) -> tuple[set[int], set[int]]:
        lines_to_expand: set[int] = set()
        columns_to_expand: set[int] = set(i for i, _ in enumerate(self.data[0]))

        for line_idx, line in enumerate(self.data):
            # Gather galaxies indexes on this line
            galaxies_indexes: set[int] = {
                column_idx
                for column_idx, char in enumerate(line)
                if char == GALAXY_SYMBOL
            }

            # Remove galaxies indexes from columns to expand
            columns_to_expand -= galaxies_indexes

            # If we don't have any galaxy, the line will be expanded
            if not galaxies_indexes:
                lines_to_expand.add(line_idx)

        return lines_to_expand, columns_to_expand
