import importlib
import inspect
from numpydoc.docscrape import NumpyDocString
import click


def check_docced_args(module):
    for name, obj in inspect.getmembers(module):
        if (inspect.isclass(obj)
                and obj.__module__ == module.__name__
                and name[0] != '_'):
            signature_args = [
                arg for arg in inspect.getfullargspec(obj.__init__).args
                if arg != 'self'
            ]
            docced_args = [
                arg[0] for arg in
                NumpyDocString(inspect.getdoc(obj))['Parameters']
            ]
            if set(signature_args) != set(docced_args):
                print('class: ', name)
                print('parameters: ', signature_args)
                print('documented: ', docced_args)
        elif (inspect.isfunction(obj)
              and obj.__module__ == module.__name__
              and name[0] != '_'):
            print('function: ', name)
            signature_args = inspect.getfullargspec(obj).args
            docced_args = [
                arg[0] for arg in
                NumpyDocString(inspect.getdoc(obj))['Parameters']
            ]
            if set(signature_args) != set(docced_args):
                print('class: ', name)
                print('parameters: ', signature_args)
                print('documented: ', docced_args)
        elif inspect.ismodule(obj) and obj.__package__ == module.__name__:
            check_docced_args(obj)


@click.command()
@click.argument('modulename')
def cli(modulename=''):
    module = importlib.import_module(modulename)
    check_docced_args(module)
