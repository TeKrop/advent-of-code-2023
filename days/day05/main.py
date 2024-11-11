from collections import defaultdict
from functools import cache, cached_property
from typing import Iterable

from scripts.utils import AbstractPuzzleSolver


class PuzzleSolver(AbstractPuzzleSolver):
    ###########################
    # DAY 5 - Shared code
    ###########################
    maps: list["Map"]

    @cached_property
    def seed_line(self):
        return self.lines[0]

    @cached_property
    def seed_numbers(self) -> list[int]:
        seed_numbers_data = self.seed_line.split(":")[1]
        return [int(number) for number in seed_numbers_data.split()]

    def solve(self) -> tuple[int, int]:
        self.maps = self.__construct_maps()
        return super().solve()

    def __construct_maps(self) -> list["Map"]:
        # Variable to store current map
        maps_dict = defaultdict(Map)
        current_map: Map = None

        # Construct maps (start on second line)
        for line in self.lines[2::]:
            # We don't have a map, it's a new one
            if not current_map:
                current_map = Map(line)
                maps_dict[current_map.name] = current_map
            # empty line, end of block, we save the map
            elif not line:
                # Reset current map
                current_map = None
            else:
                # Add data from current line
                maps_dict[current_map.name].add_mapping(Mapping(line))

        return list(maps_dict.values())

    ###########################
    # DAY 5 - First Part
    ###########################

    def _solve_first_part(self) -> int:
        # Get the lowest location number from the list
        return min(
            self.__get_seed_location(seed_number) for seed_number in self.seed_numbers
        )

    def __get_seed_location(self, seed_number: int) -> int:
        next_value = seed_number

        # Loop over the maps to retrieve the corresponding value
        for current_map in self.maps:
            next_value = current_map.get_destination(next_value)

        return next_value

    ###########################
    # DAY 5 - Second Part
    ###########################

    def _solve_second_part(self) -> int:
        # Retrieve seeds ranges
        seed_ranges = self.__get_seed_ranges()

        # Retrieve their ranges locations. We can have several
        # location ranges for only one initial seed range
        seed_location_ranges = []
        for seed_range in seed_ranges:
            location_ranges = self.__get_seed_location_ranges(seed_range)
            seed_location_ranges += location_ranges

        # Return the minimum start of all the location ranges we have
        return min(
            seed_location_range.start for seed_location_range in seed_location_ranges
        )

    def __get_seed_ranges(self) -> Iterable["SeedRange"]:
        for i in range(0, len(self.seed_numbers) - 1, 2):
            yield SeedRange(start=self.seed_numbers[i], length=self.seed_numbers[i + 1])

    def __get_seed_location_ranges(self, seed_range: "SeedRange") -> list["SeedRange"]:
        next_ranges = [seed_range]
        for current_map in self.maps:
            next_ranges = current_map.get_destination_ranges(next_ranges)
        return next_ranges


class SeedRange:
    def __init__(self, start: int, end: int | None = None, length: int | None = None):
        """Constructor based on start value, and either end value or length"""
        self.start = start
        self.end = end
        self.length = length

        if not self.end:
            self.end = self.start + self.length - 1
        if not self.length:
            self.length = self.end - self.start + 1

    def __repr__(self):
        return f"SeedRange({self.start}..{self.end})"

    def __sub__(self, other: "SeedRange") -> list["SeedRange"]:
        """Substract two ranges. As other is necessarily a subpart of self, we'll
        have two resulting ranges, and one can be empty (if the other is at either
        left or right edge of self).
        """
        difference_ranges = []

        if self.start != other.start:
            difference_ranges.append(SeedRange(self.start, other.start - 1))
        if self.end != other.end:
            difference_ranges.append(SeedRange(other.end + 1, self.end))

        return [result_range for result_range in difference_ranges if result_range]

    def __bool__(self) -> bool:
        """Used to check if the SeedRange is empty"""
        return self.length > 0


class Mapping:
    destination_start: int
    source_start: int
    range_length: int

    @cached_property
    def source_end(self):
        return self.source_start + self.range_length - 1

    @cached_property
    def delta(self) -> int:
        return self.destination_start - self.source_start

    def __init__(self, line: str):
        self.destination_start, self.source_start, self.range_length = [
            int(value) for value in line.split()
        ]

    def __repr__(self):
        return (
            f"Mapping({self.destination_start},{self.source_start},{self.range_length})"
        )

    @cache
    def get_destination(self, source: int) -> int | None:
        return (
            self.destination_start + (source - self.source_start)
            if self.source_start <= source <= self.source_end
            else None
        )

    def process_ranges(
        self, source_ranges: list[SeedRange], destination_ranges: list[SeedRange]
    ) -> tuple[list[SeedRange], list[SeedRange]]:
        updated_source_ranges = []
        for source_range in source_ranges:
            # Get the intersection range between the range and the mapping
            intersection_range = self.get_intersection_range(source_range)

            # In case the range in not included in the mapping
            # at all, continue to the next mapping
            if not intersection_range:
                updated_source_ranges.append(source_range)
                continue

            # Add the destination of the intersection range
            # into the destination ranges list
            destination_ranges.append(self.get_destination_range(intersection_range))

            # Put the remaining source ranges in the updated source ranges
            # (ranges resulting in the difference between source
            # range and the intersection)
            updated_source_ranges += source_range - intersection_range

        # Clean empty source ranges and update the list accordingly
        source_ranges = [
            source_range for source_range in updated_source_ranges if source_range
        ]
        return source_ranges, destination_ranges

    def get_intersection_range(self, seed_range: SeedRange) -> SeedRange | None:
        intersection_start = max(self.source_start, seed_range.start)
        intersection_end = min(self.source_end, seed_range.end)
        return (
            SeedRange(start=intersection_start, end=intersection_end)
            if intersection_start <= intersection_end
            else None
        )

    def get_destination_range(self, seed_range: SeedRange) -> SeedRange:
        return SeedRange(
            start=seed_range.start + self.delta, end=seed_range.end + self.delta
        )


class Map:
    mappings: list[Mapping]
    name: str

    def __init__(self, map_name_line: str):
        self.mappings = []
        self.name = map_name_line.split()[0]

    def __repr__(self):
        return self.name

    def add_mapping(self, mapping: Mapping):
        self.mappings.append(mapping)

    def get_destination(self, source_value: int) -> int:
        return next(
            (
                mapping.get_destination(source_value)
                for mapping in self.mappings
                if mapping.get_destination(source_value)
            ),
            source_value,
        )

    def get_destination_ranges(self, seed_ranges: list[SeedRange]) -> list[SeedRange]:
        return [
            destination
            for seed_range in seed_ranges
            for destination in self.__get_seed_range_destinations(seed_range)
        ]

    def __get_seed_range_destinations(self, seed_range: SeedRange) -> list[SeedRange]:
        # Init source and destination ranges
        source_ranges = [seed_range]
        destination_ranges = []

        # Loop over mappings, calculate destination ranges and keep
        # delta seed ranges mapping after mapping
        for mapping in self.mappings:
            source_ranges, destination_ranges = mapping.process_ranges(
                source_ranges, destination_ranges
            )

        # If we still have remaining non-empty source ranges after looping
        # over every mappings, we add them into the result ranges as
        # destination range which didn't change
        destination_ranges += source_ranges

        return destination_ranges
