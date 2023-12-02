from .utils import AbstractPuzzleSolver


class PuzzleSolver(AbstractPuzzleSolver):
    ###########################
    # DAY 1 - First Part
    ###########################

    def _solve_first_part(self) -> int:
        return sum(self.get_digit_calibration_value(line) for line in self.lines)

    @staticmethod
    def get_digit_calibration_value(line: str) -> int:
        digits = [char for char in line if char.isdigit()]
        return int(digits[0] + digits[-1])

    ###########################
    # DAY 1 - Second Part
    ###########################

    def _solve_second_part(self) -> int:
        return sum(self.get_full_calibration_value(line) for line in self.lines)

    def get_full_calibration_value(self, line: str) -> int:
        line = self.insert_digits_into_numbers(line)
        return self.get_digit_calibration_value(line)

    @staticmethod
    def insert_digits_into_numbers(line: str) -> str:
        numbers_replacements = {
            "one": "o1e",
            "two": "t2o",
            "three": "t3ree",
            "four": "4our",
            "five": "5ive",
            "six": "6ix",
            "seven": "7even",
            "eight": "e8ght",
            "nine": "n9ne",
        }
        for number, digit in numbers_replacements.items():
            line = line.replace(number, digit)
        return line
