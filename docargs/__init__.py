import sys

import yaml
import click
from colorama import Fore
import ast

from .check import check


@click.command()
@click.option(
    "--ignore-ambiguous-signatures",
    default=True,
    is_flag=True,
    help=(
        "Whether to ignore extra arguments in docstrings if the function "
        "has *args or **kwargs."
    ),
)
@click.argument("files", nargs=-1, type=click.File("r"))
def cli(ignore_ambiguous_signatures=False, files=()):
    """
    Check if arguments in functions in FILES have been documented.
    """

    failure_tree = {}
    failed = False
    for module_file in files:
        source_code = module_file.read()
        tree = ast.parse(source_code)

        for statement, underocumented, overdocumented in check(tree):
            failed = True
            if underocumented or overdocumented:
                cli_error(
                    module_file.name, statement, underocumented, overdocumented
                )

    if failed:
        sys.exit(1)
    else:
        click.echo(Fore.GREEN + "All arguments are documented ✓")
        sys.exit(0)


def cli_error(file_name, statement, underocumented, overdocumented):
    click.echo(f"{file_name}:{statement.lineno}:{statement.col_offset}: ")
    if len(underocumented) > 0:
        click.secho(
            (
                f"These parameters are not "
                f"documented: {', '.join(underocumented)}"
            ),
            fg="red",
        )
    if len(overdocumented) > 0:
        click.secho(
            (
                f"These parameters are documented but not in the "
                f"function signature: {', '.join(overdocumented)}"
            ),
            fg="yellow",
        )


def color_text(text: str) -> str:
    colored_text = []
    for line in text.split("\n"):
        if "Not in" in line:
            colored_text.append(Fore.LIGHTRED_EX + line)
        elif "- " not in line:
            colored_text.append(Fore.RESET + line)
        else:
            colored_text.append(line)
    colored_text.append(Fore.RESET)
    return "\n".join(colored_text)
