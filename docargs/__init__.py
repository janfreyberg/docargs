import importlib
import inspect
import sys

from numpydoc.docscrape import NumpyDocString
import click
from colorama import Fore


def check_docced_args(module):
    failures = 0
    for name, obj in inspect.getmembers(module):
        if name[0] != "_" and (
                getattr(obj, '__module__', None) == module.__name__
                or getattr(obj, '__package__', None) == module.__name__
        ):
            if (
                inspect.isclass(obj)
            ):
                signature_args = [
                    arg
                    for arg in inspect.getfullargspec(obj.__init__).args
                    if arg != "self"
                ]
                docced_args = [
                    arg[0]
                    for arg in NumpyDocString(inspect.getdoc(obj))[
                        "Parameters"
                    ]
                ]
                if set(signature_args) != set(docced_args):
                    print(
                        "{lead_col}class: {0}; ".format(
                            name, lead_col=Fore.CYAN
                        ),
                        "not documented: {missing_col}{0}".format(
                            ", ".join(set(signature_args) - set(docced_args)),
                            missing_col=Fore.RED
                        )
                    )
                    failures += 1
            elif (
                inspect.isfunction(obj)
                and obj.__module__ == module.__name__
                and name[0] != "_"
            ):
                signature_args = inspect.getfullargspec(obj).args
                docced_args = [
                    arg[0]
                    for arg in NumpyDocString(inspect.getdoc(obj))[
                        "Parameters"
                    ]
                ]
                if set(signature_args) != set(docced_args):
                    print(
                        "{lead_col}class: {0}; ".format(
                            name, lead_col=Fore.GREEN
                        ),
                        "not documented: {missing_col}{0}".format(
                            ", ".join(set(signature_args) - set(docced_args)),
                            missing_col=Fore.RED
                        )
                    )
                    failures += 1
            elif inspect.ismodule(obj) and obj.__package__ == module.__name__:
                print(name)
                failures += check_docced_args(obj)

    return failures


@click.command()
@click.argument("modulename")
def cli(modulename=""):
    module = importlib.import_module(modulename)
    failures = check_docced_args(module)
    if failures > 0:
        print(
            Fore.RED + str(failures)
            + " undocumented parameters in non-private function or classes!"
        )
        sys.exit(1)
