import importlib
from pathlib import Path

import typer
from dotenv import load_dotenv
from pyinstrument import Profiler
from rich import print
from typing_extensions import Annotated

from scripts.utils import (
    AnswerResult,
    DataType,
    create_empty_file,
    get_input,
    submit_answer,
)

load_dotenv()
app = typer.Typer()


@app.command()
def run(
    day: Annotated[
        int,
        typer.Argument(min=1, max=26, help="Day of solution to run (ex: 1 for day01)"),
    ],
    data_type: Annotated[
        DataType,
        typer.Option(
            help="Data type: 'input' for user data, or 'example' for example data",
        ),
    ] = DataType.INPUT,
    benchmark: Annotated[
        bool, typer.Option(help="Activate benchmark mode is specified")
    ] = False,
    submit: Annotated[
        bool, typer.Option(help="Submit the solution on AoC (AOC_SESSION_ID needed)")
    ] = False,
):
    """
    Run the solution for a given day.

    If --benchmark is used, pyinstrument will profile the process.

    If --submit is used, solution will be submitted on AoC website using your AOC_SESSION_ID.
    """

    # Load module of the day
    try:
        day_module = importlib.import_module(f"days.day{day:02d}.main")
    except ModuleNotFoundError:
        print(f"[red]No puzzle solver for [bold]day {day}[/bold] yet.[/red]")
        raise typer.Exit(1)

    # Instanciate puzzle solver
    try:
        puzzle_solver = day_module.PuzzleSolver(
            day=day,
            data_type=data_type,
        )
    except FileNotFoundError:
        print(
            f"[red]File [bold]{data_type.value}.txt[/bold] not found for day {day}.[/red]"
        )
        raise typer.Exit(1)

    print(f"Running puzzle solver for day {day}...")
    if is_example := data_type == DataType.EXAMPLE:
        print("Computing example data...")

    # Execution with benchmark if specified
    if benchmark is True:
        print("Benchmark mode activated !")
        profiler = Profiler()
        profiler.start()
        results = puzzle_solver.solve()
        profiler.stop()
        print(f"[green]Results : [bold]{results}[/bold][/green]")
        profiler.print()
    else:
        results = puzzle_solver.solve()
        print(f"[green]Results : [bold]{results}[/bold][/green]")

    # Stop here if we're not planning to submit anything
    if not submit:
        return

    # Make sure we're not sending example data
    if is_example is True:
        print(f"[red]You can't send an answer for example data[/red]")
        raise typer.Exit(1)

    # Send the solution for the tasks having an answer
    for task, result in enumerate(results, 1):
        if result is None:
            continue

        match submit_answer(day=day, task=task, answer=result):
            case AnswerResult.ALREADY_SOLVED:
                print(f"[red]Task {task} has already been solved ![/red]")
            case AnswerResult.RIGHT_ANSWER:
                print(f"[green]Your answer for task {task} is right ![/green]")
            case AnswerResult.WRONG_ANSWER:
                print(f"[red]Your answer for task {task} is wrong ![/red]")
            case _:
                continue


@app.command()
def create_next_day():
    """
    Create the folder structure and files for the next day
    """
    days_path = Path(__file__).parent / "days"
    days_path.mkdir(exist_ok=True)  # Make sure "days" folder exists

    # Load main.py template
    template_path = Path(__file__).parent / "scripts" / "day_template.py"
    if not template_path.exists():
        print(
            "[red]Model [bold]day_template.py[/bold] not found in [bold]scripts[/bold] folder.[/red]"
        )
        raise typer.Exit(1)

    template_content = template_path.read_text()

    # Find the last existing day
    existing_days = sorted(days_path.glob("day*/"), key=lambda p: int(p.name[3:]))
    if existing_days:
        last_day_num = int(existing_days[-1].name[3:])
        next_day_num = last_day_num + 1
    else:
        next_day_num = 1  # Start with day 1 if no folder exists

    # If we're already the last day, don't create a new one
    if next_day_num > 26:
        print("[red]The last day has already been created, nothing to do.[/red]")
        raise typer.Exit(1)

    day_str = f"day{next_day_num:02d}"
    day_path = days_path / day_str

    # Create folder of the day
    day_path.mkdir(parents=True)
    print(f"[green] Folder [bold]{day_str}[/bold] created.[/green]")

    # Create main.py file
    main_file = day_path / "main.py"
    main_content = template_content.replace("X", f"{next_day_num:02d}")
    main_file.write_text(main_content)
    print(
        f"[green]File [bold]{main_file.name}[/bold] created successfully from model.[/green]"
    )

    # Create example.txt data file
    create_empty_file(file_path=day_path / "example.txt")

    # Import input.txt from AoC or create empty file
    input_file_path = day_path / "input.txt"
    if input_content := get_input(day=next_day_num):
        input_file_path.write_text(input_content, encoding="utf-8")
    else:
        create_empty_file(file_path=input_file_path)


if __name__ == "__main__":
    app()
