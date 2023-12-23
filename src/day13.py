from dataclasses import dataclass
from enum import StrEnum
from functools import cached_property
from typing import Iterable

from .utils import AbstractPuzzleSolver


class PuzzleSolver(AbstractPuzzleSolver):
    ###########################
    # DAY 13 - Common Part
    ###########################
    @cached_property
    def patterns(self) -> list["Pattern"]:
        return list(self.__compute_patterns())

    def __compute_patterns(self) -> Iterable["Pattern"]:
        cells: tuple[tuple["GroundCell"]] = []

        for cells_row in self.lines:
            # If we have an empty line, end of pattern
            if not cells_row:
                yield Pattern(cells=tuple(cells))
                cells = []
            # Else, add the current line
            else:
                cells.append([GroundCell(type=elt) for elt in cells_row])

        # If we have some lines remaining (last line)
        if cells:
            yield Pattern(cells=tuple(cells))

    ###########################
    # DAY 13 - First Part
    ###########################

    def _solve_first_part(self) -> int:
        return sum(
            pattern.nb_columns_before_reflection
            + (100 * pattern.nb_rows_above_reflection)
            for pattern in self.patterns
        )

    ###########################
    # DAY 13 - Second Part
    ###########################

    def _solve_second_part(self) -> int:
        return None


class GroundType(StrEnum):
    ASH = "."
    ROCK = "#"


@dataclass
class GroundCell:
    type: GroundType

    def __repr__(self) -> str:
        return self.type


@dataclass
class Pattern:
    cells: tuple[tuple[GroundCell]]

    def __init__(self, cells: tuple[tuple[GroundCell]]):
        self.cells = cells

    def __repr__(self) -> str:
        return (
            "\n"
            + "\n".join("".join(str(ground_row)) for ground_row in self.cells)
            + "\n"
        )

    @cached_property
    def rows(self) -> tuple[int]:
        """Compute row values (one row equals an integer value)"""
        return tuple(self.__cells_value(cells_row) for cells_row in self.cells)

    @cached_property
    def nb_rows_above_reflection(self) -> int:
        return self.__process_reflection(self.rows)

    @cached_property
    def columns(self) -> tuple[int]:
        nb_columns = len(self.cells[0])
        cells_cols = [
            [cells_row[i] for cells_row in self.cells] for i in range(nb_columns)
        ]
        return tuple(self.__cells_value(cells_col) for cells_col in cells_cols)

    @cached_property
    def nb_columns_before_reflection(self) -> int:
        return self.__process_reflection(self.columns)

    @staticmethod
    def __cells_value(cells: tuple[GroundCell]) -> int:
        """Compute cells as if rocks are 1 and ashes are 0. We have
        a binary result that we translate into an integer.
        """
        binary_number = "".join(
            ("1" if cell.type == GroundType.ROCK else "0" for cell in cells)
        )
        return int(binary_number, 2)

    @staticmethod
    def __process_reflection(cells_lists: tuple[int]) -> int:
        # Calculate half number of cells for reflection calculation
        nb_cells = len(cells_lists)
        half_nb_cells = round(nb_cells / 2)

        for cells_number, cells in enumerate(cells_lists):
            # No check on first cell
            if cells_number == 0:
                continue

            # If current cell is not the same than the
            # previous one, continue the checks
            if cells != cells_lists[cells_number - 1]:
                continue

            # Cells are the same, check forward and backward
            is_valid_reflection = True
            for i in range(1, half_nb_cells):
                # First, we check if either one of the two cells are above
                # the cells list. It means we passed the edge, reflection is valid
                first_cells_number = cells_number - 1 - i
                second_cells_number = cells_number + i
                if first_cells_number < 0 or second_cells_number >= nb_cells:
                    break

                # If not at the edge, check if cells have the same value. If
                # not,
                if cells_lists[first_cells_number] != cells_lists[second_cells_number]:
                    is_valid_reflection = False
                    break

            # If we calculated the reflection and found out is was
            # OK, return the current cells number as number of cells
            # before the reflection
            if is_valid_reflection:
                return cells_number

        # If we don't have any reflection, return 0
        return 0
