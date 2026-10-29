import argparse
import sys

from controllers.task_controller import TaskController


def _task_id(value):
    try:
        task_id = int(value)
    except ValueError as error:
        raise argparse.ArgumentTypeError("ID must be a positive integer.") from error
    if task_id < 1:
        raise argparse.ArgumentTypeError("ID must be a positive integer.")
    return task_id


def _build_parser():
    parser = argparse.ArgumentParser(
        description="Manage tasks stored in tasks.json in the current directory."
    )
    commands = parser.add_subparsers(dest="command", required=True)

    add = commands.add_parser("add", help="add a task")
    add.add_argument("description")

    update = commands.add_parser("update", help="update a task description")
    update.add_argument("id", type=_task_id)
    update.add_argument("description")

    delete = commands.add_parser("delete", help="delete a task")
    delete.add_argument("id", type=_task_id)

    mark_in_progress = commands.add_parser(
        "mark-in-progress", aliases=["start"], help="mark a task in progress"
    )
    mark_in_progress.add_argument("id", type=_task_id)

    mark_done = commands.add_parser(
        "mark-done", aliases=["complete"], help="mark a task done"
    )
    mark_done.add_argument("id", type=_task_id)

    list_tasks = commands.add_parser("list", aliases=["ls"], help="list tasks")
    list_tasks.add_argument(
        "status",
        nargs="?",
        choices=("all", "done", "not-done", "in-progress"),
        default="all",
    )

    for command, aliases, help_text in (
        ("list-done", ["done"], "list completed tasks"),
        ("list-not-done", [], "list tasks that are not done"),
        ("list-in-progress", [], "list tasks in progress"),
    ):
        commands.add_parser(command, aliases=aliases, help=help_text)

    return parser


def main(argv=None):
    args = _build_parser().parse_args(argv)
    controller = TaskController()

    try:
        if args.command == "add":
            controller.add_task(args.description)
        elif args.command == "update":
            controller.update_task(args.id, args.description)
        elif args.command == "delete":
            controller.delete_task(args.id)
        elif args.command in ("mark-in-progress", "start"):
            controller.mark_task_in_progress(args.id)
        elif args.command in ("mark-done", "complete"):
            controller.mark_task_done(args.id)
        elif args.command in ("list", "ls"):
            controller.list_tasks(args.status)
        else:
            status = {
                "list-done": "done",
                "done": "done",
                "list-not-done": "not-done",
                "list-in-progress": "in-progress",
            }[args.command]
            controller.list_tasks(status)
    except (OSError, ValueError) as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1
    return 0

if __name__ == "__main__":
    raise SystemExit(main())