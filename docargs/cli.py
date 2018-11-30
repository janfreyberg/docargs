import sys

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

    Parameters
    ----------
    ignore_ambiguous_signatures : bool
        Whether to be strict on ambiguous function signatures
    files : list
        The files to check.
    """

    failed = False
    for module_file in files:
        source_code = module_file.read()
        tree = ast.parse(source_code)

        for statement, underdocumented, overdocumented in check(tree):
            failed = True
            if underdocumented or overdocumented:
                cli_error(
                    module_file.name,
                    statement,
                    underdocumented,
                    overdocumented,
                )

    if failed:
        sys.exit(1)
    else:
        click.echo(Fore.GREEN + "All arguments are documented ✓")
        sys.exit(0)


def cli_error(  # noqa DOO1
    file_name, statement, underdocumented, overdocumented
):
    click.echo(
        "{}:{}:{}: ".format(file_name, statement.lineno, statement.col_offset)
    )
    if len(underdocumented) > 0:
        click.secho(
            (
                "These parameters are not "
                "documented: {}".format(", ".join(underdocumented))
            ),
            fg="red",
        )
    if len(overdocumented) > 0:
        click.secho(
            (
                "These parameters are documented but not in the "
                "function signature: {}".format(", ".join(overdocumented))
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
