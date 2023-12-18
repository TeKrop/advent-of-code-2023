from enum import StrEnum
from functools import cache, cached_property
from time import perf_counter

from .utils import AbstractPuzzleSolver


class PuzzleSolver(AbstractPuzzleSolver):
    ###########################
    # DAY 12 - First Part
    ###########################

    def _solve_first_part(self) -> int:
        return sum(
            spring_row.nb_arrangements
            for line in self.lines
            if (spring_row := SpringRow(line=line))
        )

    ###########################
    # DAY 12 - Second Part
    ###########################

    def _solve_second_part(self) -> int:
        return sum(
            spring_row.nb_arrangements
            for line in self.lines
            if (spring_row := SpringRow(line=line, unfold=True))
        )


class SpringState(StrEnum):
    OPERATIONAL = "."
    DAMAGED = "#"
    UNKNOWN = "?"

    def __repr__(self):
        return self.value


class SpringRow:
    states: tuple[SpringState]
    damaged_groups_sizes: tuple[int]

    def __init__(self, line: str, unfold: bool = False):
        states_data, sizes_data = line.split()

        # Part 2, we unfold the spring
        if unfold:
            states_data = "?".join([states_data] * 5)
            sizes_data = ",".join([sizes_data] * 5)

        # In order for the algorithm to process the end of groups correctly if
        # we have a damaged spring at the end, we add an additional dot at the end
        self.states = tuple(
            [SpringState(state) for state in states_data] + [SpringState.OPERATIONAL]
        )
        self.damaged_groups_sizes = tuple(int(size) for size in sizes_data.split(","))

    def __repr__(self):
        return "".join(self.states)

    @cached_property
    def nb_arrangements(self) -> int:
        return self.__compute_arrangements(
            states=self.states, groups_sizes=self.damaged_groups_sizes
        )

    @cache
    def __compute_arrangements(
        self,
        states: tuple[SpringState],
        groups_sizes: tuple[int],
        current_counter: int = 0,
    ) -> int:
        # Stop condition of recursive function, verify that we don't have any
        # group to search, and we're not in the middle of a group
        if not states:
            return not groups_sizes and not current_counter

        # Initialize the number of arrangements
        nb_arrangements = 0

        # In an iteration, just check the current
        # state and recursively process the others
        next_state = states[0]
        possible_states = (
            [SpringState.DAMAGED, SpringState.OPERATIONAL]
            if next_state == SpringState.UNKNOWN
            else [next_state]
        )

        # Loop over possible states
        for state in possible_states:
            match state:
                # If this is a damaged spring, we're continuing
                # to fill in the current group
                case SpringState.DAMAGED:
                    nb_arrangements += self.__compute_arrangements(
                        states[1:], groups_sizes, current_counter + 1
                    )

                # Else, this is an operational spring. We may be at the
                # end of an existing group, we have some checks
                case SpringState.OPERATIONAL:
                    # If the current_counter is not empty, it means we're in a group
                    if current_counter:
                        # We must check if it matches the next group size. If
                        # that's the case, then we ended one group, and go next
                        if groups_sizes:
                            next_group_size = groups_sizes[0]
                            if current_counter == next_group_size:
                                nb_arrangements += self.__compute_arrangements(
                                    states[1:], groups_sizes[1:]
                                )
                        # Else, it's the same case, we're still
                        # in the middle of an ongoing group
                    else:
                        # Else, same arrangement, continue with next
                        nb_arrangements += self.__compute_arrangements(
                            states[1:], groups_sizes
                        )

        return nb_arrangements
