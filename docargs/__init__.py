from typing import Union, Dict, Optional, Tuple
import importlib
import inspect
import sys

import yaml

from numpydoc.docscrape import NumpyDocString
import click
from colorama import Fore

import ast
import itertools
from functools import singledispatch


def parse_file(filename: str):
    """
    Parse a file's abstract syntax tree.
    """
    with open(filename) as f:
        source = f.read()

    tree = ast.parse(source, filename)

    return tree


def get_signature_params(
    node: Union[ast.FunctionDef, ast.AsyncFunctionDef],
    ignore: tuple = ("self", "cls"),
) -> Tuple[set, bool]:
    return (
        {
            argument.arg
            for argument in itertools.chain(
                node.args.args, node.args.kwonlyargs
            )
            if argument.arg not in ignore
        },
        node.args.vararg is not None or node.args.kwarg is not None,
    )


def get_doc_params(node: Union[ast.FunctionDef, ast.AsyncFunctionDef]):
    docstring = ast.get_docstring(node)
    if docstring is not None:
        return {arg[0] for arg in NumpyDocString(docstring)["Parameters"]}
    else:
        return set()


def get_functions():
    pass


def is_private(
    node: Union[ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef]
):
    return node.name[0] == "_"


def compare_args(signature_args: set, docced_args: set, ambiguous: bool):

    output = {}
    if signature_args - docced_args:
        output["Not in docstring"] = list(signature_args - docced_args)
    if docced_args - signature_args and not ambiguous:
        output["Not in signature"] = list(docced_args - signature_args)

    return output if output else None


@singledispatch
def check(node, ignore_ambiguous_signatures: bool = False) -> Optional[Dict]:
    return None


@check.register
def check_function(
    func: ast.FunctionDef, ignore_ambiguous_signatures: bool = False
) -> Optional[Dict]:
    """
    Check the documented and actual arguments for a function.
    """
    print(func.name)
    signature_args, ambiguous = get_signature_params(func)
    docced_args = get_doc_params(func)

    return {
        func.name: compare_args(
            signature_args,
            docced_args,
            ignore_ambiguous_signatures and ambiguous,
        )
    }


def check_init(
    obj: ast.ClassDef, ignore_ambiguous_signatures: bool = False
) -> Optional[Dict]:
    """
    Check the documented and actual arguments for the __init__ method.
    """
    try:
        init_method = next(
            method
            for method in obj.body
            if isinstance(method, ast.FunctionDef)
            and method.name == "__init__"
        )
    except StopIteration:
        init_method = None

    if init_method is not None:
        signature_args, ambiguous = get_signature_params(init_method)
        docced_args = get_doc_params(obj) | get_doc_params(init_method)
        return compare_args(
            signature_args,
            docced_args,
            ignore_ambiguous_signatures and ambiguous,
        )
    else:
        return None


@check.register
def check_class(
    obj: ast.ClassDef, ignore_ambiguous_signatures: bool = False
) -> Optional[Dict]:

    print(obj.name)
    output = {
        "__init__": check_init(
            obj, ignore_ambiguous_signatures=ignore_ambiguous_signatures
        )
    }

    for node in obj.body:
        check_result = check(
            node, ignore_ambiguous_signatures=ignore_ambiguous_signatures
        )
        if check_result is not None:
            output.update(check_result)

    output = {".".join([obj.name, key]): val for key, val in output.items()}
    return output


@check.register
def check_module(
    module: ast.Module, ignore_ambiguous_signatures: bool = False
):

    output = {}

    for node in module.body:

        check_result = check(
            node, ignore_ambiguous_signatures=ignore_ambiguous_signatures
        )
        if check_result is not None:

            output.update(check_result)

    output = {
        key: val
        for key, val in output.items()
        if val is not None and len(val) > 0
    }

    if len(output) == 0:
        return None
    else:
        return output


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
    for module_file in files:

        syntax_tree = ast.parse(module_file.read())
        check_result = check(syntax_tree, ignore_ambiguous_signatures)
        if check_result is not None:
            failure_tree[module_file.name] = check_result

    if len(failure_tree) > 0:
        click.echo(Fore.LIGHTRED_EX + "Some arguments were not documented:")
        click.echo(
            color_text(yaml.dump(failure_tree, default_flow_style=False))
        )
        failed = True
    else:
        click.echo(Fore.GREEN + "All arguments are documented ✓")
        failed = False

    if failed:
        sys.exit(1)
    else:
        sys.exit(0)


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
