from collections import defaultdict
from functools import cache
from typing import Iterable

from .utils import AbstractPuzzleSolver


class PuzzleSolver(AbstractPuzzleSolver):
    ###########################
    # DAY 3 - Shared code
    ###########################

    # Shared attribute
    number_digits: list[str] = []

    @property
    def number_value(self) -> int:
        return int("".join(self.number_digits))

    def __reset_state_variables(self):
        self.number_digits = []
        self.is_part_number = False
        self.is_part_number_linked_to_star = False
        self.current_stars = set()

    @cache
    def __get_char(self, line_idx: int, char_idx: int) -> str | None:
        # Don't support negative indexes
        if line_idx < 0 or char_idx < 0:
            return None

        # Try to retrieve char, return None in case it
        # doesn't exist (edge-case position)
        try:
            return self.lines[line_idx][char_idx]
        except IndexError:
            return None

    ###########################
    # DAY 3 - First Part
    ###########################

    # In order to know if current is part number
    is_part_number: bool = False

    def _solve_first_part(self) -> int:
        # Initialize state variables
        return sum(self.__get_part_numbers())

    def __get_part_numbers(self) -> Iterable[int]:
        for line_idx, line in enumerate(self.lines):
            # New line, check if we had an adjacent number on previous line
            yield from self.__get_number_if_is_part_number()

            for char_idx, char in enumerate(line):
                if char.isdigit():
                    self.number_digits.append(char)
                    self.is_part_number |= self.__is_part_number(line_idx, char_idx)
                else:
                    yield from self.__get_number_if_is_part_number()

        # End of the file, in case there was a number at the end
        yield from self.__get_number_if_is_part_number()

    def __get_number_if_is_part_number(self) -> Iterable[int]:
        # In case we don't have any number registered yet
        if not self.number_digits:
            return

        # Compute the number
        number = self.number_value if self.is_part_number else None

        # Reset the state for next number process
        self.__reset_state_variables()

        # Yield the number if it's a part number
        if number:
            yield number

    def __is_part_number(self, line_idx: int, char_idx: int) -> bool:
        """A number is a "part" number if it's adjacent to at least one symbol"""
        return any(
            self.__is_symbol(line_idx + delta_line, char_idx + delta_char)
            for delta_line in (-1, 0, 1)
            for delta_char in (-1, 0, 1)
            if not (delta_line == 0 and delta_char == 0)  # exclude current
        )

    @cache
    def __is_symbol(self, line_idx: int, char_idx: int) -> bool:
        if not (char := self.__get_char(line_idx, char_idx)):
            return False
        return char != "." and not char.isdigit()

    ###########################
    # DAY 3 - Second Part
    ###########################

    # In order to know if current is part number
    is_part_number_linked_to_star: bool = False

    # List of stars coordinates, linked to current number
    current_stars: set[tuple[int, int]]

    # Star symbols and their linked parts. Ex: (1,1) -> [45, 1458]
    star_symbols: dict[tuple[int, int], list[int]] = defaultdict(list)

    def _solve_second_part(self) -> int:
        return sum(gear.get_ratio() for gear in self.__get_gears())

    def __get_gears(self) -> Iterable["Gear"]:
        for line_idx, line in enumerate(self.lines):
            # New line, check if we had an adjacent number on previous line
            self.__handle_processed_number()

            for char_idx, char in enumerate(line):
                if char.isdigit():
                    self.number_digits.append(char)
                    self.is_part_number_linked_to_star |= (
                        self.__is_part_number_linked_to_star(line_idx, char_idx)
                    )
                else:
                    self.__handle_processed_number()

        # End of the file, in case there was a number at the end
        self.__handle_processed_number()

        yield from (
            Gear(linked_part_numbers)
            for linked_part_numbers in self.star_symbols.values()
            if len(linked_part_numbers) == 2
        )

    def __is_part_number_linked_to_star(self, line_idx: int, char_idx: int) -> bool:
        linked_stars = set(
            (line_idx + delta_line, char_idx + delta_char)
            for delta_line in (-1, 0, 1)
            for delta_char in (-1, 0, 1)
            if (
                (not (delta_line == 0 and delta_char == 0))  # exclude current
                and self.__get_char(line_idx + delta_line, char_idx + delta_char) == "*"
            )
        )

        # Add stars to current linked stars if any
        self.current_stars |= linked_stars

        # Return result depending on found stars
        return len(linked_stars) > 0

    def __handle_processed_number(self) -> Iterable[int]:
        # In case we don't have any number registered yet
        if not self.number_digits:
            return

        # Compute the number and update the stars symbols if linked to stars
        if self.is_part_number_linked_to_star:
            for star_coord in self.current_stars:
                self.star_symbols[star_coord].append(self.number_value)

        # Reset the state for next number process
        self.__reset_state_variables()


class Gear:
    part_numbers: list[int]

    def __init__(self, part_numbers: list[int, int]):
        self.part_numbers = part_numbers

    def get_ratio(self):
        return self.part_numbers[0] * self.part_numbers[1]
