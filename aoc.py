import typer
import importlib
from pathlib import Path
from pyinstrument import Profiler
from scripts.utils import DataType
from typing_extensions import Annotated
from rich import print

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
):
    """
    Run the solution for a given day.

    If --benchmark is used, pyinstrument will profile the process.
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
    if data_type == DataType.EXAMPLE:
        print("Computing example data...")

    # Exécution avec ou sans benchmark
    if benchmark:
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

    # Create example.txt and input.txt data files
    for data_file in {"example.txt", "input.txt"}:
        file_path = day_path / data_file
        if not file_path.exists():
            file_path.touch()
            print(f"[green]File [bold]{file_path.name}[/bold] created.[/green]")
        else:
            print(
                f"[orange]File [bold]{file_path.name}[/bold] already exists.[/orange]"
            )


if __name__ == "__main__":
    app()
