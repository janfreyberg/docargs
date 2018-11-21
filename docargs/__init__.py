from typing import Union, Dict, Optional
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
) -> set:
    return {
        argument.arg
        for argument in itertools.chain(node.args.args, node.args.kwonlyargs)
        if argument.arg not in ignore
    }


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


# def same_source(obj1, obj2):
#     if inspect.ismodule(obj1) and not inspect.ismodule(obj2):
#         try:
#             return obj2.__module__.startswith(obj1.__package__)
#         except AttributeError:
#             return False
#     elif inspect.ismodule(obj2) and not inspect.ismodule(obj1):
#         try:
#             return obj1.__module__.startswith(obj2.__package__)
#         except AttributeError:
#             return False

#     try:
#         overlap = {
#             getattr(obj1, "__module__", None),
#             getattr(obj1, "__package__", None),
#         } & {
#             getattr(obj2, "__module__", None),
#             getattr(obj2, "__package__", None),
#         } - {
#             None
#         }

#         return len(overlap) > 0

#     except TypeError:
#         return False


def compare_args(signature_args: set, docced_args: set):

    output = {}
    if signature_args - docced_args:
        output["Not in docstring"] = list(signature_args - docced_args)
    if docced_args - signature_args:
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
    signature_args = get_signature_params(func)
    docced_args = get_doc_params(func)

    return compare_args(signature_args, docced_args)


def check_init(
    obj: ast.ClassDef, ignore_ambiguous_signatures: bool = False
) -> Optional[Dict]:
    """
    Check the documented and actual arguments for the __init__ method.
    """
    init_method = next(
        method for method in obj.body if method.name == "__init__"
    )
    signature_args = get_signature_params(init_method)
    docced_args = get_doc_params(obj) | get_doc_params(obj.__init__)
    return compare_args(signature_args, docced_args)


@check.register
def check_class(
    obj: ast.ClassDef, ignore_ambiguous_signatures: bool = False
) -> Optional[Dict]:

    output = {"__init__": check_init(obj)}

    for node in obj.body:
        check_result = check(node)
        if check_result is not None:
            output[node.name] = check_result

    output = {".".join([obj.name, key]): val for key, val in output.items()}
    return output


@check.register
def check_module(
    module: ast.Module, ignore_ambiguous_signatures: bool = False
):

    output = {}

    for node in module.body:

        check_result = check(node)

        if check_result is not None:

            output.update(check_result)

    if not ignore_ambiguous_signatures:
        output = {
            key: val
            for key, val in output.items()
            if val is not None and len(val) > 0
        }
    else:
        output = {
            key: val
            for key, val in output.items()
            if val is not None and "Not in docstring" in val
        }
        output = {
            key: val
            for key, val in output.items()
            if val is not None and len(val) > 0
        }
    return output


@click.command()
@click.option("--ignore-ambiguous-signatures", default=False, is_flag=True)
@click.argument("modulenames", nargs=-1)
def cli(ignore_ambiguous_signatures=False, modulenames=()):

    failed = False
    for modulename in modulenames:

        module = importlib.import_module(modulename)
        failure_tree = check_module(module, ignore_ambiguous_signatures)

        if len(failure_tree) > 0:
            print(Fore.LIGHTRED_EX + "Some arguments were not documented:")
            print(
                color_text(yaml.dump(failure_tree, default_flow_style=False))
            )
            failed = True
        else:
            print(Fore.GREEN + "All arguments are documented ✓")
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
