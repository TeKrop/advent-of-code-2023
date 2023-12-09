from functools import cached_property

from .utils import AbstractPuzzleSolver


class PuzzleSolver(AbstractPuzzleSolver):
    ###########################
    # DAY 9 - First Part
    ###########################

    def _solve_first_part(self) -> int:
        return sum(Sequence(line=line).next_value for line in self.lines)

    ###########################
    # DAY 9 - Second Part
    ###########################

    def _solve_second_part(self) -> int:
        return sum(Sequence(line=line).previous_value for line in self.lines)


class Sequence:
    numbers: list[int]

    def __init__(self, line: str | None = None, numbers: list[int] | None = None):
        if line:
            self.numbers = [int(number) for number in line.split()]
        else:
            self.numbers = numbers

    def __getitem__(self, index: int) -> int:
        return self.numbers[index]

    def __len__(self):
        return len(self.numbers)

    @cached_property
    def next_value(self) -> int:
        # The next value for the final sequence is always 0
        if self.is_final_sequence:
            return 0

        return self[-1] + self.next_sequence.next_value

    @cached_property
    def previous_value(self) -> int:
        # The previous value for the final sequence is always 0
        if self.is_final_sequence:
            return 0

        return self[0] - self.next_sequence.previous_value

    @cached_property
    def next_sequence(self) -> "Sequence":
        # There is no next sequence if this is the final one
        if self.is_final_sequence:
            return None

        # Next sequence composition
        return Sequence(numbers=[self[i] - self[i - 1] for i in range(1, len(self))])

    @cached_property
    def is_final_sequence(self) -> bool:
        return all(number == 0 for number in self)
