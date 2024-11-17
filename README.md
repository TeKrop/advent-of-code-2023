# 🎅 Advent of Code 2023
![Made with Python](https://img.shields.io/badge/Python-v3.13-blue?logo=python&logoColor=white)
[![AoC 2023](https://img.shields.io/badge/2023-⭐%2027-gray?logo=adventofcode&labelColor=8a2be2)](https://adventofcode.com/2023)
[![License: MIT](https://img.shields.io/github/license/TeKrop/advent-of-code-2023)](https://github.com/TeKrop/advent-of-code-2023/blob/main/LICENSE)

Advent of Code 2023 solutions in Python. It uses `uv` for dependencies management, `typer` for CLI commands, and `pyinstrument` for profiling. My goal is to write the most readable, understandable and maintainable solutions IMO, which are not necessarily the most performant ones.

The project comes with a dotenv file in which you can specify an `AOC_SESSION_ID` if you wish to automate your input retrieval, and make an answer from CLI directly.

## 💽 Install
The project uses `uv` for dependencies management, install it first : https://docs.astral.sh/uv/getting-started/installation/

Then, install dependencies with `uv sync`

## 🏃 Run

Global usage
```
Usage: aoc.py [OPTIONS] COMMAND [ARGS]...

╭─ Options ───────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ --install-completion          Install completion for the current shell.                                         │
│ --show-completion             Show completion for the current shell, to copy it or customize the installation.  │
│ --help                        Show this message and exit.                                                       │
╰─────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
╭─ Commands ──────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ run               Run the solution for a given day.                                                             │
│ create-next-day   Create the folder structure and files for the next day                                        │
╰─────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
```

Run solution for a given day
```
Usage: aoc.py run [OPTIONS] DAY

Run the solution for a given day.
If --benchmark is used, pyinstrument will profile the process.
If --submit is used, solution will be submitted on AoC website using your AOC_SESSION_ID.

╭─ Arguments ────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ *    day      INTEGER RANGE  Day of solution to run (ex: 1 for day01) [default: None] [required]                                       │
╰────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
╭─ Options ──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ --data-type                      [example|input]  Data type: 'input' for user data, or 'example' for example data [default: input]     │
│ --benchmark    --no-benchmark                     Activate benchmark mode is specified [default: no-benchmark]                         │
│ --submit       --no-submit                        Submit the solution on AoC (AOC_SESSION_ID needed) [default: no-submit]              │
│ --help                                            Show this message and exit.                                                          │
╰────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
```