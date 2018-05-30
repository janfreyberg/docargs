import importlib
import inspect
from numpydoc.docscrape import NumpyDocString
import click


def check_docced_args(module):
    failures = 0
    for name, obj in inspect.getmembers(module):
        if (
            inspect.isclass(obj)
            and obj.__module__ == module.__name__
            and name[0] != "_"
        ):
            signature_args = [
                arg
                for arg in inspect.getfullargspec(obj.__init__).args
                if arg != "self"
            ]
            docced_args = [
                arg[0]
                for arg in NumpyDocString(inspect.getdoc(obj))["Parameters"]
            ]
            if set(signature_args) != set(docced_args):
                print(
                    "class: {}; not documented: {}".format(
                        name, ', '.join(set(signature_args) - set(docced_args))
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
                for arg in NumpyDocString(inspect.getdoc(obj))["Parameters"]
            ]
            if set(signature_args) != set(docced_args):
                print(
                    "function: {}; not documented: {}".format(
                        name, ', '.join(set(signature_args) - set(docced_args))
                    )
                )
                failures += 1
        elif inspect.ismodule(obj) and obj.__package__ == module.__name__:
            failures += check_docced_args(obj)

    return failures


@click.command()
@click.argument("modulename")
def cli(modulename=""):
    module = importlib.import_module(modulename)
    failures = check_docced_args(module)
    if failures > 0:
        raise ValueError(
            "Undocumented parameters in non-private function or classes!"
        )
