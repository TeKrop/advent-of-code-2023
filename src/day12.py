from enum import StrEnum
from functools import cached_property
from itertools import product

from .utils import AbstractPuzzleSolver, ObjectiveCounter


class PuzzleSolver(AbstractPuzzleSolver):
    ###########################
    # DAY 12 - First Part
    ###########################

    def _solve_first_part(self) -> int:
        return sum(
            len(spring_row.arrangements)
            for line in self.lines
            if (spring_row := SpringRow(line))
        )

    ###########################
    # DAY 12 - Second Part
    ###########################

    def _solve_second_part(self) -> int:
        return None


class SpringState(StrEnum):
    OPERATIONAL = "."
    DAMAGED = "#"
    UNKNOWN = "?"


class SpringRow:
    states: list[SpringState]
    damaged_groups_sizes: list[int]

    def __init__(self, line: str):
        states_data, sizes_data = line.split()
        self.states = [SpringState(state) for state in states_data]
        self.damaged_groups_sizes = [int(size) for size in sizes_data.split(",")]

    def __repr__(self):
        return "".join(self.states)

    @cached_property
    def arrangements(self) -> list[list[SpringState]]:
        return [
            state for state in self.possible_states if self.__is_valid_state_row(state)
        ]

    @cached_property
    def possible_states(self) -> list[list[SpringState]]:
        # First, assemble possible states for each position
        possible_states = [
            [SpringState.DAMAGED, SpringState.OPERATIONAL]
            if state == SpringState.UNKNOWN
            else [state]
            for state in self.states
        ]
        # Then, constitute a list by using the product method from itertools
        return [states for states in product(*possible_states)]

    def __is_valid_state_row(self, states_row: list[SpringState]) -> bool:
        # We'll keep track of the current damaged group we're exploring
        counter: ObjectiveCounter = None
        groups_sizes = iter(self.damaged_groups_sizes)

        for state in states_row:
            match state:
                # If the current spring is damaged, rize the count
                case SpringState.DAMAGED:
                    # If this is the first of the group, init
                    if not counter:
                        try:
                            counter = ObjectiveCounter(objective=next(groups_sizes))
                        except StopIteration:
                            # If we don't have more group on the list, invalid
                            return False
                    else:
                        # Else, rise the count
                        counter += 1

                case SpringState.OPERATIONAL:
                    # If we had a group, check its size. If it's not
                    # the same as counted, if not a valid group
                    if counter and not counter.is_valid:
                        return False
                    counter = None

                # If we have an unknown state, it's not valid
                case SpringState.UNKNOWN:
                    return False

        # After looping over all the springs, check if we still had a
        # group and if it's valid if it's the case
        if counter and not counter.is_valid:
            return False

        # Now, check if we still had groups to check
        try:
            next(groups_sizes)
        except StopIteration:
            # We had the exception, meaning the iteration is complete
            pass
        else:
            # Still at least one group, state is invalid
            return False

        # If we passed all the checks, this is good
        return True
