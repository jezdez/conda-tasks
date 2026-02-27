"""CLI for ``conda task`` -- argparse configuration and dispatch."""

from __future__ import annotations

import argparse
from pathlib import Path

from conda.cli.helpers import (
    add_output_and_prompt_options,
    add_parser_help,
    add_parser_prefix,
)


def generate_parser() -> argparse.ArgumentParser:
    """Build and return the parser -- used by sphinxarg.ext for docs."""
    parser = argparse.ArgumentParser(
        prog="conda task",
        description="Run, list, and manage project tasks.",
        add_help=False,
    )
    configure_parser(parser)
    return parser


def configure_parser(parser: argparse.ArgumentParser) -> None:
    """Set up ``conda task`` CLI with subcommands."""
    add_parser_help(parser)

    parser.add_argument(
        "--file",
        "-f",
        type=Path,
        default=None,
        help="Path to a specific task file instead of auto-detection.",
    )

    sub = parser.add_subparsers(dest="subcmd")

    run_parser = sub.add_parser("run", help="Run a task.", add_help=False)
    add_parser_help(run_parser)
    add_parser_prefix(run_parser)
    add_output_and_prompt_options(run_parser)
    run_parser.add_argument("task_name", help="Name of the task to run.")
    run_parser.add_argument(
        "task_args",
        nargs="*",
        default=[],
        help="Arguments to pass to the task.",
    )
    run_parser.add_argument(
        "--clean-env",
        action="store_true",
        default=False,
        help="Run in a clean environment (minimal env vars).",
    )
    run_parser.add_argument(
        "--skip-deps",
        action="store_true",
        default=False,
        help="Skip dependency tasks, run only the named task.",
    )
    run_parser.add_argument(
        "--cwd",
        type=Path,
        default=None,
        help="Override the working directory for the task.",
    )
    run_parser.add_argument(
        "--templated",
        action="store_true",
        default=False,
        help="Treat the command as a Jinja2 template (for ad-hoc commands).",
    )

    list_parser = sub.add_parser("list", help="List available tasks.", add_help=False)
    add_parser_help(list_parser)
    add_output_and_prompt_options(list_parser)

    add_parser_cmd = sub.add_parser(
        "add", help="Add a task to the manifest.", add_help=False
    )
    add_parser_help(add_parser_cmd)
    add_output_and_prompt_options(add_parser_cmd)
    add_parser_cmd.add_argument("task_name", help="Name for the new task.")
    add_parser_cmd.add_argument("cmd", help="Command string for the task.")
    add_parser_cmd.add_argument(
        "--depends-on",
        nargs="*",
        default=[],
        help="Tasks this task depends on.",
    )
    add_parser_cmd.add_argument(
        "--description",
        default=None,
        help="Human-readable description.",
    )

    rm_parser = sub.add_parser(
        "remove", help="Remove a task from the manifest.", add_help=False
    )
    add_parser_help(rm_parser)
    add_output_and_prompt_options(rm_parser)
    rm_parser.add_argument("task_name", help="Name of the task to remove.")

    export_parser = sub.add_parser(
        "export",
        help="Export tasks to conda.toml format.",
        add_help=False,
    )
    add_parser_help(export_parser)
    add_output_and_prompt_options(export_parser)
    export_parser.add_argument(
        "-o",
        "--output",
        type=Path,
        default=None,
        help="Write to a file instead of stdout.",
    )


def execute(args: argparse.Namespace) -> int:
    """Main entry point dispatched by the conda plugin system."""
    subcmd = args.subcmd

    if subcmd is None:
        if hasattr(args, "task_name") and args.task_name:
            subcmd = "run"
        else:
            generate_parser().print_help()
            return 0

    if subcmd == "run":
        from .run import execute_run

        return execute_run(args)
    elif subcmd == "list":
        from .list import execute_list

        return execute_list(args)
    elif subcmd == "add":
        from .add import execute_add

        return execute_add(args)
    elif subcmd == "remove":
        from .remove import execute_remove

        return execute_remove(args)
    elif subcmd == "export":
        from .export import execute_export

        return execute_export(args)
    else:
        generate_parser().print_help()
        return 0
