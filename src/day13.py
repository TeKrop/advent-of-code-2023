from copy import deepcopy
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

    def __patterns_sum(self, patterns: list["Pattern"]) -> int:
        return sum(pattern.reflections_sum for pattern in patterns)

    ###########################
    # DAY 13 - First Part
    ###########################

    def _solve_first_part(self) -> int:
        return self.__patterns_sum(self.patterns)

    ###########################
    # DAY 13 - Second Part
    ###########################

    def _solve_second_part(self) -> int:
        return self.__patterns_sum(
            self.__repaired_pattern(pattern) for pattern in self.patterns
        )

    def __repaired_pattern(self, pattern: "Pattern") -> "Pattern":
        # We're going to try switching one pattern symbol at a time, and compute
        # new reflections. If we find a new reflection pattern, we stop here and
        # return the corresponding pattern
        for i in range(pattern.nb_rows):
            for j in range(pattern.nb_columns):
                # Create new set of cells, and create a new pattern with it
                new_cells = deepcopy(pattern.cells)
                new_cells[i][j].type = (
                    GroundType.ROCK
                    if new_cells[i][j].type == GroundType.ASH
                    else GroundType.ASH
                )

                new_pattern = Pattern(cells=new_cells)

                # If the new pattern doesn't have any reflection, nothing to do
                if new_pattern.reflections == Reflection({0}, {0}):
                    continue

                # If new pattern reflections are the same than current one,
                # it's not the one we're searching for
                if new_pattern.reflections == pattern.reflections:
                    continue

                # Remove simular reflections from new pattern. If it means
                # not having any reflection, we put 0 a special "null" value.
                new_pattern.reflections.vertical -= pattern.reflections.vertical
                if not new_pattern.reflections.vertical:
                    new_pattern.reflections.vertical = {0}

                new_pattern.reflections.horizontal -= pattern.reflections.horizontal
                if not new_pattern.reflections.horizontal:
                    new_pattern.reflections.horizontal = {0}

                return new_pattern

        # We didn't found any new pattern, that's not normal, stop here
        raise ValueError


class GroundType(StrEnum):
    ASH = "."
    ROCK = "#"


@dataclass
class GroundCell:
    type: GroundType

    def __repr__(self) -> str:
        return self.type


@dataclass
class Reflection:
    horizontal: set[int]
    vertical: set[int]


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
    def nb_rows(self):
        return len(self.cells)

    @cached_property
    def rows(self) -> tuple[int]:
        """Compute row values (one row equals an integer value)"""
        return tuple(self.__cells_value(cells_row) for cells_row in self.cells)

    @cached_property
    def nb_columns(self):
        return len(self.cells[0])

    @cached_property
    def columns(self) -> tuple[int]:
        cells_cols = [
            [cells_row[i] for cells_row in self.cells] for i in range(self.nb_columns)
        ]
        return tuple(self.__cells_value(cells_col) for cells_col in cells_cols)

    @cached_property
    def reflections(self) -> Reflection:
        """Tuple with horizontal reflections (rows) and vertical reflections (col)"""
        return Reflection(
            horizontal=self.__process_reflections(self.rows, self.nb_rows),
            vertical=self.__process_reflections(self.columns, self.nb_columns),
        )

    @cached_property
    def reflections_sum(self) -> int:
        """We assume the reflections only have one element each
        when we're doing the sum calculation.
        """
        return next(iter(self.reflections.vertical)) + (
            100 * next(iter(self.reflections.horizontal))
        )

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
    def __process_reflections(cells_lists: tuple[int], nb_cells: int) -> set[int]:
        # Calculate half number of cells for reflection calculation
        half_nb_cells = round(nb_cells / 2)
        found_cells: set[int] = set()

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

            # If we calculated the reflection and found out it was
            # OK, add the current cells number as number of cells
            # before one reflection
            if is_valid_reflection:
                found_cells.add(cells_number)

        # Return found reflection cells if any, else it means we have
        # not reflection so we return a set with only 0 as value
        return found_cells or {0}
