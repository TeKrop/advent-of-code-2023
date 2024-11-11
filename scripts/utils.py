from abc import ABC, abstractmethod
from functools import cached_property
from enum import Enum
from pathlib import Path
from rich import print
from typing import Any


class DataType(str, Enum):
    EXAMPLE = "example"
    INPUT = "input"


class AbstractPuzzleSolver(ABC):
    day: int
    data_type: DataType
    lines: list[str]

    def __init__(self, day: int, data_type: DataType):
        self.day = day
        self.data_type = data_type
        self.__get_puzzle_data()

    @cached_property
    def line(self):
        return self.lines[0]

    def __get_puzzle_data(self) -> list[str]:
        data_file = (
            Path(__file__).parent.parent
            / "days"
            / f"day{self.day:02d}"
            / f"{self.data_type.value}.txt"
        )
        print(f"Loading {data_file}...")
        if not data_file.exists():
            raise FileNotFoundError

        with data_file.open() as file:
            self.lines = [line.rstrip("\n") for line in file]

    def solve(self) -> tuple[int, int]:
        return self._solve_first_part(), self._solve_second_part()

    @abstractmethod
    def _solve_first_part(self) -> int: ...

    @abstractmethod
    def _solve_second_part(self) -> int: ...


class Multiton(ABC):
    _instances = {}

    def __new__(cls, key):
        if key not in cls._instances:
            cls._instances[key] = super(Multiton, cls).__new__(cls)
        return cls._instances[key]


def min_and_max(first: Any, second: Any) -> tuple[Any, Any]:
    return min(first, second), max(first, second)
