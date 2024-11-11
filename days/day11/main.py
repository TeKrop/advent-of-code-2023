from dataclasses import dataclass, field
from itertools import combinations, count

from scripts.utils import AbstractPuzzleSolver, min_and_max

EMPTY_SPACE_SYMBOL = "."
GALAXY_SYMBOL = "#"


class PuzzleSolver(AbstractPuzzleSolver):
    ###########################
    # DAY 11 - Common Part
    ###########################
    universe: "Universe"
    galaxy_pairs: list[tuple["Galaxy", "Galaxy"]]
    expandable_lines: set[int]
    expandable_columns: set[int]

    def solve(self) -> tuple[int, int]:
        # First, create the universe, but don't expand it
        self.universe = Universe(self.lines)

        # Create pairs of galaxies now, before expansion
        self.galaxy_pairs = list(combinations(self.universe.galaxies, 2))

        # Get expandable columns and lines
        (
            self.expandable_lines,
            self.expandable_columns,
        ) = self.universe.get_expandable_lines_and_columns()

        return super().solve()

    def __get_shortest_path_length(self, galaxy_pair: tuple["Galaxy", "Galaxy"]) -> int:
        # First calculate the distance before expansion
        initial_distance = self.__get_initial_distance(galaxy_pair)
        first_galaxy, second_galaxy = galaxy_pair

        # Then, calculate how much we must travel in addition because of expansion
        # For that, retrieve the number of expanded columns and lines we have
        # between the two galaxies
        min_x, max_x = min_and_max(first_galaxy.pos.x, second_galaxy.pos.x)
        nb_lines = sum(
            1 for line_idx in self.expandable_lines if line_idx in range(min_x, max_x)
        )

        min_y, max_y = min_and_max(first_galaxy.pos.y, second_galaxy.pos.y)
        nb_columns = sum(
            1
            for column_idx in self.expandable_columns
            if column_idx in range(min_y, max_y)
        )

        # We use self.expansion_factory - 1, as we already counted the column once
        # in the initial distance calculation
        expansion_distance = (nb_lines + nb_columns) * (self.expansion_factor - 1)

        return initial_distance + expansion_distance

    def __get_initial_distance(self, galaxy_pair: tuple["Galaxy", "Galaxy"]) -> int:
        """The shortest past, by only going up/right/down/left, is just the sum of
        the absolute value of difference between coordinates.
        """
        first_galaxy, second_galaxy = galaxy_pair
        y_diff = abs(second_galaxy.pos.y - first_galaxy.pos.y)
        x_diff = abs(second_galaxy.pos.x - first_galaxy.pos.x)
        return x_diff + y_diff

    ###########################
    # DAY 11 - First Part
    ###########################

    def _solve_first_part(self) -> int:
        # For the first part, the expansion of the universe is just
        # doubling the empty lines and columns
        self.expansion_factor = 2

        # Return the sum of their shortest path length
        return sum(
            self.__get_shortest_path_length(galaxy_pair)
            for galaxy_pair in self.galaxy_pairs
        )

    ###########################
    # DAY 11 - Second Part
    ###########################

    def _solve_second_part(self) -> int:
        # For the second part, the expansion of the universe is multiplying
        # by 1_000_000 the empty lines and columns
        self.expansion_factor = 1_000_000

        # Return the sum of their shortest path length
        return sum(
            self.__get_shortest_path_length(galaxy_pair)
            for galaxy_pair in self.galaxy_pairs
        )


@dataclass
class Position:
    x: int  # line index
    y: int  # column index


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

    def get_expandable_lines_and_columns(self) -> tuple[set[int], set[int]]:
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
