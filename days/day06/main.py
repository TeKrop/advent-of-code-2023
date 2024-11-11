from functools import reduce
from operator import mul

from scripts.utils import AbstractPuzzleSolver


class PuzzleSolver(AbstractPuzzleSolver):
    ###########################
    # DAY 6 - First Part
    ###########################
    def _solve_first_part(self) -> int:
        races = self.__compute_races()
        return reduce(mul, [race.ways_to_win for race in races])

    def __compute_races(self) -> list["Race"]:
        durations = [int(duration) for duration in self.lines[0].split(":")[1].split()]
        distances = [int(distance) for distance in self.lines[1].split(":")[1].split()]
        return [
            Race(duration, distance) for duration, distance in zip(durations, distances)
        ]

    ###########################
    # DAY 6 - Second Part
    ###########################

    def _solve_second_part(self) -> int:
        single_race = self.__compute_single_race()
        return single_race.ways_to_win

    def __compute_single_race(self) -> "Race":
        duration = int("".join(self.lines[0].split(":")[1].split()))
        distance = int("".join(self.lines[1].split(":")[1].split()))
        return Race(duration, distance)


class Trial:
    holding_time: int
    distance_traveled: int

    def __init__(self, holding_time: int, race_duration: int):
        self.holding_time = holding_time
        remaining_time = race_duration - self.holding_time
        # Speed is the same as the holding time
        self.distance_traveled = remaining_time * self.holding_time


class Race:
    duration: int
    record_distance: int
    ways_to_win: int

    def __init__(self, duration: int, record_distance: int):
        self.duration = duration
        self.record_distance = record_distance
        self.ways_to_win = self.__compute_ways_to_win()

    def __repr__(self) -> str:
        return (
            f"Race(duration={self.duration},"
            f"record_distance={self.record_distance},"
            f"ways_to_win={self.ways_to_win})"
        )

    def __compute_ways_to_win(self) -> int:
        """I noticed the race distance follows a second degree function
        which depends on the race duration.
        Formula : distance = -(holding_time)² + duration * holding_time
        """

        # Retrieve the first trial to win against the record
        first_won_trial = self.__get_first_won_trial()

        # Calculate the number of ways to win depending on it and
        # the total duration of the race. I noticed that the formula is
        # nearly the derivative of the distance function.
        return (self.duration - 2 * first_won_trial.holding_time) + 1

    def __get_first_won_trial(self) -> Trial:
        return next(
            (
                trial
                for holding_time in range(self.duration)
                if (
                    (trial := Trial(holding_time, self.duration)).distance_traveled
                    > self.record_distance
                )
            ),
            None,
        )
