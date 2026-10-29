# Task Tracker CLI

A standard-library-only Python command-line application for managing tasks.

## Project URL
https://roadmap.sh/projects/task-tracker

## Requirements

Python 3.7 or newer. No third-party packages are required.

## Usage

Open **Command Prompt (CMD)** and run commands from the project directory.
The `task.bat` launcher is intended for CMD; the documented `task` command is
not supported in PowerShell or other shells.

```text
task add "Write project documentation"
task update 1 "Finish project documentation"
task mark-in-progress 1
task mark-done 1
task delete 1

task list
task list done
task list not-done
task list in-progress
```

The equivalent filter commands are `list-done`, `list-not-done`, and
`list-in-progress`. These commands store `tasks.json` in the current working
directory.

Descriptions containing spaces should be quoted. IDs must be positive integers.
The `not-done` filter includes both `todo` and `in-progress` tasks.

## Task data

The application creates `tasks.json` in the current working directory when
needed. Each task contains an integer `id`, a `description`, a `status`
(`todo`, `in-progress`, or `done`), and ISO-8601 UTC `createdAt` and
`updatedAt` timestamps.

## Tests

Run the standard-library test suite from the project directory:

```text
python -m unittest discover -s tests -v
```
