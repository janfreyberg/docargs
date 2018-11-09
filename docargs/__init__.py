import importlib
import inspect
import sys

import yaml

from numpydoc.docscrape import NumpyDocString
import click
from colorama import Fore


def is_private(obj):
    if isinstance(obj, str):
        return obj[0] == "_"
    else:
        # return superintendent._base.__name__.rsplit(".")[-1] == "_"
        return getattr(obj, "__name__", "").rsplit()[-1][0] == "_"


def same_source(obj1, obj2):
    if inspect.ismodule(obj1) and not inspect.ismodule(obj2):
        try:
            return obj2.__module__.startswith(obj1.__package__)
        except AttributeError:
            return False
    elif inspect.ismodule(obj2) and not inspect.ismodule(obj1):
        try:
            return obj1.__module__.startswith(obj2.__package__)
        except AttributeError:
            return False

    try:
        overlap = {
            getattr(obj1, "__module__", None),
            getattr(obj1, "__package__", None),
        } & {
            getattr(obj2, "__module__", None),
            getattr(obj2, "__package__", None),
        } - {
            None
        }

        return len(overlap) > 0

    except TypeError:
        return False


def get_doc_params(obj):
    docstring = inspect.getdoc(obj)
    if docstring is not None:
        return {arg[0] for arg in NumpyDocString(docstring)["Parameters"]}
    else:
        return set()


def get_signature_params(obj, ignore: tuple = ("self", "cls")) -> set:
    return {
        arg for arg in inspect.getfullargspec(obj).args if arg not in ignore
    }


def compare_args(signature_args: set, docced_args: set):

    output = {}
    if signature_args - docced_args:
        output["Not in docstring"] = list(signature_args - docced_args)
    if docced_args - signature_args:
        output["Not in signature"] = list(docced_args - signature_args)

    return output if output else None


def check_function(func):
    """
    Check the documented and actual arguments for a function.
    """
    signature_args = get_signature_params(func)
    docced_args = get_doc_params(func)

    return compare_args(signature_args, docced_args)


def check_init(obj):
    """
    Check the documented and actual arguments for the __init__ method.
    """
    signature_args = get_signature_params(obj) | get_signature_params(
        obj.__init__
    )
    docced_args = get_doc_params(obj) | get_doc_params(obj.__init__)

    return compare_args(signature_args, docced_args)


def check_class(obj):

    output = {"__init__": check_init(obj)}

    for name, method in inspect.getmembers(obj):
        if (
            inspect.isfunction(method)
            and inspect.getsourcefile(method) == inspect.getsourcefile(obj)
            and not is_private(name)
        ):
            output[name] = check_function(method)

    # filter output
    output = {
        ".".join([obj.__module__, obj.__name__, key]): val
        for key, val in output.items()
        if val is not None
    }
    return output


def check_module(module, ignore_ambiguous_signatures):

    output = {}

    for name, obj in inspect.getmembers(module):

        if same_source(obj, module) and not is_private(name):

            if inspect.isclass(obj):
                # output[name] = check_class(obj)
                output.update(check_class(obj))
            elif inspect.isfunction(obj):
                output[".".join([obj.__module__, name])] = check_function(obj)
            elif inspect.ismodule(obj):
                output.update(check_module(obj, ignore_ambiguous_signatures))

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
