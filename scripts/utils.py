import os
from abc import ABC, abstractmethod
from enum import Enum, auto
from functools import cached_property
from pathlib import Path
from typing import Any

import httpx
from rich import print


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


def create_empty_file(file_path: Path) -> None:
    if not file_path.exists():
        file_path.touch()
        print(f"[green]File [bold]{file_path.name}[/bold] created.[/green]")
    else:
        print(f"[rouge]File [bold]{file_path.name}[/bold] already exists.[/rouge]")


def get_input(day: int) -> str | None:
    if not (session_id := os.getenv("AOC_SESSION_ID")):
        print(f"[rouge]No session ID found, input can't be retrieved from AoC[/rouge]")
        return

    input_url = f"{os.getenv('AOC_BASE_URL')}/day/{day}/input"
    print(f"Retrieving input data from AoC...")
    response = httpx.get(input_url, cookies={"session": session_id})
    if response.status_code != httpx.codes.OK:
        print(f"[red]Error from AoC when retrieving input : {response}[/red]")
        return

    print(f"[green]Input data retrieved from AoC ![/green]")
    return response.text


class AnswerResult(Enum):
    ALREADY_SOLVED = auto()
    RIGHT_ANSWER = auto()
    WRONG_ANSWER = auto()


def submit_answer(day: int, task: int, answer: int) -> AnswerResult | None:
    if not (session_id := os.getenv("AOC_SESSION_ID")):
        print(f"[rouge]No session ID found, input can't be retrieved from AoC[/rouge]")
        return

    print(f"Submitting answer for task {task} to AoC...")
    submit_url = f"{os.getenv('AOC_BASE_URL')}/day/{day}/answer"
    response = httpx.post(
        submit_url,
        cookies={"session": session_id},
        data={"level": task, "answer": str(answer)},
    )
    if response.status_code != httpx.codes.OK:
        print(f"[red]Error from AoC when submitting solution : {response}[/red]")
        return

    print(f"[green]Answer submitted to AoC ![/green]")

    if "That's the right answer" in response.text:
        return AnswerResult.RIGHT_ANSWER
    elif "You don't seem to be solving the right level" in response.text:
        return AnswerResult.ALREADY_SOLVED
    else:
        return AnswerResult.WRONG_ANSWER
