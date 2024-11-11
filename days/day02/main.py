from typing import Iterable

from scripts.utils import AbstractPuzzleSolver


class PuzzleSolver(AbstractPuzzleSolver):
    ###########################
    # DAY 2 - First Part
    ###########################

    def solve(self) -> tuple[int, int]:
        self.games = [Game(line) for line in self.lines]
        return super().solve()

    def _solve_first_part(self) -> int:
        return sum(game.id for game in self.games if game.is_valid())

    ###########################
    # DAY 2 - Second Part
    ###########################

    def _solve_second_part(self) -> int:
        return sum(game.get_power() for game in self.games)


class GameSet:
    red: int = 0
    green: int = 0
    blue: int = 0

    RED_CUBES_MAX = 12
    GREEN_CUBES_MAX = 13
    BLUE_CUBES_MAX = 14

    def __init__(self, red: int, green: int, blue: int):
        self.red = red
        self.green = green
        self.blue = blue

    @classmethod
    def from_data(cls, game_set_data: str) -> "GameSet":
        game_set = GameSet(red=0, green=0, blue=0)
        for subset in game_set_data.strip().split(","):
            subset_data = subset.strip().split(" ")
            cubes_quantity, cubes_color = int(subset_data[0]), subset_data[1]
            setattr(game_set, cubes_color, cubes_quantity)
        return game_set

    def is_valid(self) -> bool:
        return (
            self.red <= self.RED_CUBES_MAX
            and self.green <= self.GREEN_CUBES_MAX
            and self.blue <= self.BLUE_CUBES_MAX
        )

    def get_power(self) -> int:
        return self.red * self.green * self.blue


class Game:
    id: int

    def __init__(self, line: str):
        line_data = line.split(":")
        self.id = int(line_data[0].split(" ")[-1])
        self.game_data = line_data[1].strip()

    @property
    def game_sets(self) -> Iterable[GameSet]:
        for game_set_data in self.game_data.split(";"):
            yield GameSet.from_data(game_set_data)

    def is_valid(self) -> bool:
        return all(game_set.is_valid() for game_set in self.game_sets)

    def get_power(self) -> int:
        minimum_game_set = self.__get_minimum_game_set()
        return minimum_game_set.get_power()

    def __get_minimum_game_set(self) -> GameSet:
        return GameSet(
            red=max(game_set.red for game_set in self.game_sets),
            green=max(game_set.green for game_set in self.game_sets),
            blue=max(game_set.blue for game_set in self.game_sets),
        )
