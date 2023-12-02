import argparse
import importlib


def parse_parameters() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run the Advent of Code 2023 solution script for a given day",
    )

    parser.add_argument(
        "-d",
        "--day",
        action="store",
        type=int,
        choices=range(1, 26),
        help="day of solution to run",
        required=True,
    )
    parser.add_argument(
        "-e",
        "--example",
        action="store_true",
        default=False,
        help="use example data instead of definitive data",
    )

    return parser.parse_args()


def main():
    args = parse_parameters()

    try:
        module_of_the_day = importlib.import_module(f"src.day{args.day}")
    except ModuleNotFoundError:
        print(f"No puzzle solver for day {args.day} yet")
        return

    try:
        puzzle_solver = module_of_the_day.PuzzleSolver(
            day=args.day,
            example=args.example,
        )
    except FileNotFoundError:
        print(f"No data found for day {args.day}")
        return

    print("Running puzzle solver for day", args.day)
    if args.example:
        print("Computing example data")

    results = puzzle_solver.solve()
    print("Results :", results)


if __name__ == "__main__":
    main()
