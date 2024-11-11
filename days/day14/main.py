from dataclasses import dataclass
from enum import StrEnum
from functools import cached_property

from scripts.utils import AbstractPuzzleSolver


class PuzzleSolver(AbstractPuzzleSolver):
    ###########################
    # DAY 14 - Common Part
    ###########################
    @cached_property
    def platform(self) -> "Platform":
        return self.__compute_plaform()

    def __compute_plaform(self) -> "Platform":
        return Platform(
            cells=tuple(
                tuple(GroundCell(type=elt) for elt in cells_row)
                for cells_row in self.lines
            )
        )

    ###########################
    # DAY 14 - First Part
    ###########################

    def _solve_first_part(self) -> int:
        # Tilt the platform towards north
        self.platform.tilt()
        # Return the total load
        return self.platform.get_total_load()

    ###########################
    # DAY 14 - Second Part
    ###########################

    def _solve_second_part(self) -> int:
        return None


class GroundType(StrEnum):
    ROUND_ROCK = "O"
    CUBE_ROCK = "#"
    EMPTY = "."


@dataclass
class GroundCell:
    type: GroundType

    def __repr__(self) -> str:
        return self.type


@dataclass
class Platform:
    cells: tuple[tuple[GroundCell]]

    def __init__(self, cells: tuple[tuple[GroundCell]]):
        self.cells = cells

    def __repr__(self) -> str:
        return "\n" + "\n".join("".join(str(row)) for row in self.cells) + "\n"

    @cached_property
    def nb_rows(self) -> int:
        return len(self.cells)

    @cached_property
    def nb_columns(self) -> int:
        return len(self.cells[0])

    def tilt(self) -> None:
        tilted_cells: list[list[GroundCell]] = []

        for row_number, row in enumerate(self.cells):
            new_row: list[GroundCell] = []

            for col_number, cell in enumerate(row):
                match cell.type:
                    # Round rock case, we tilt it on top
                    case GroundType.ROUND_ROCK:
                        new_rock_row_number = 0  # default new row, top row

                        # Check if the rock will encounter anything on his way.
                        # If so, save the row number on which the rock will be
                        for i in range(row_number - 1, -1, -1):
                            if tilted_cells[i][col_number].type != GroundType.EMPTY:
                                new_rock_row_number = i + 1
                                break

                        # Process the new current cell, either it's empty
                        # if the rock moved, or it's the rock if it didn't move
                        if new_rock_row_number == row_number:
                            new_cell = cell
                        else:
                            # Modify the cell on which the rock will be if it moved
                            tilted_cells[new_rock_row_number][col_number] = GroundCell(
                                type=GroundType.ROUND_ROCK
                            )
                            new_cell = GroundCell(type=GroundType.EMPTY)

                    case GroundType.CUBE_ROCK:
                        new_cell = cell

                    case GroundType.EMPTY:
                        new_cell = cell

                new_row.append(new_cell)

            tilted_cells.append(new_row)

        self.cells = tuple(tuple(row) for row in tilted_cells)

    def get_total_load(self) -> int:
        return sum(
            self.__get_row_load(row, row_number)
            for row_number, row in enumerate(self.cells)
        )

    def __get_row_load(self, row: list[GroundCell], row_number: int) -> int:
        nb_round_rocks = len(
            [cell for cell in row if cell.type == GroundType.ROUND_ROCK]
        )
        return nb_round_rocks * (self.nb_rows - row_number)
