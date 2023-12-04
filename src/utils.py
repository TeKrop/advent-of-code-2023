from abc import ABC, abstractmethod


class AbstractPuzzleSolver(ABC):
    day: int
    example: bool
    lines: list[str]

    def __init__(self, day: int, example: bool):
        self.day = day
        self.example = example
        self.__get_puzzle_data()

    def __get_puzzle_data(self) -> list[str]:
        filename = "example" if self.example else "input"
        filepath = f"data/day{self.day}/{filename}.txt"
        with open(filepath, "r") as file:
            self.lines = [line.rstrip("\n") for line in file]

    def solve(self) -> tuple[int, int]:
        return self._solve_first_part(), self._solve_second_part()

    @abstractmethod
    def _solve_first_part(self) -> int:
        ...

    @abstractmethod
    def _solve_second_part(self) -> int:
        ...
