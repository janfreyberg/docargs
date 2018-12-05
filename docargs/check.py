import ast
import itertools
from functools import singledispatch
from typing import Set, Tuple, Union, Iterator, List, Container

from numpydoc.docscrape import NumpyDocString

from .identify import find_init, is_private


@singledispatch
def check(node, ignore_ambiguous_signatures: bool = True) -> None:
    """Check an object's argument documentation.

    Parameters
    ----------
    node : ast.AST
        The object to check.
    ignore_ambiguous_signatures : bool, optional
        Whether to not fail extra documented parameters if the object
        takes *args or *kwargs (the default is True)

    Returns
    -------
    Optional[Dict]
        [description]
    """

    return None


@check.register
def check_function(
    func: ast.FunctionDef, ignore_ambiguous_signatures: bool = True
) -> Iterator[Tuple[ast.FunctionDef, List[str], List[str]]]:
    """Check the documented and actual arguments for a function.

    Parameters
    ----------
    func : ast.FunctionDef
        The function to check
    ignore_ambiguous_signatures : bool, optional
        Whether to ignore extra docstring parameters if the function signature
        is ambiguous (the default is True).

    Returns
    -------
    ast.FunctionDef
        The function
    Set[str]
        Parameters in the signature but not in the docstring.
    Set[str]]
        Parameters in the docstring but not in the signature.
    """

    signature_args, ambiguous = get_signature_params(func)
    docced_args = get_doc_params(func)

    underdocumented, overdocumented = compare_args(
        signature_args, docced_args, ignore_ambiguous_signatures and ambiguous
    )

    yield func, underdocumented, overdocumented


def check_init(
    obj: ast.ClassDef, ignore_ambiguous_signatures: bool = False
) -> Iterator[Tuple[ast.FunctionDef, List[str], List[str]]]:
    """Check the documented and actual arguments for an init method.

    This combines the parameters in the init method docstring and the class
    docstring, as either are OK.

    Parameters
    ----------
    obj : ast.ClassDef
        The class for which to check the __init__ method.
    ignore_ambiguous_signatures : bool, optional
        Whether to ignore extra docstring parameters if the function signature
        is ambiguous (the default is True).

    Yields
    ------
    ast.FunctionDef
        The __init__ method AST node.
    Set[str]
        Parameters in the signature but not in the docstring.
    Set[str]]
        Parameters in the docstring but not in the signature.
    """
    init_method = find_init(obj)

    if init_method is not None:
        signature_args, ambiguous = get_signature_params(init_method)
        docced_args = get_doc_params(obj) | get_doc_params(init_method)
        underdocumented, overdocumented = compare_args(
            signature_args,
            docced_args,
            ignore_ambiguous_signatures and ambiguous,
        )
        yield init_method, underdocumented, overdocumented


@check.register
def check_class(
    obj: ast.ClassDef, ignore_ambiguous_signatures: bool = False
) -> Iterator[Tuple[ast.FunctionDef, List[str], List[str]]]:
    """Check the documented and actual arguments for a class's methods.

    Parameters
    ----------
    obj : ast.ClassDef
        The class to check.
    ignore_ambiguous_signatures : bool, optional
        Whether to ignore extra docstring parameters if the function signature
        is ambiguous (the default is True).

    Yields
    ------
    ast.FunctionDef
        The __init__ method AST node.
    Set[str]
        Parameters in the signature but not in the docstring.
    Set[str]]
        Parameters in the docstring but not in the signature.
    """

    if find_init(obj) is not None:
        yield from check_init(obj, ignore_ambiguous_signatures)

    for node in ast.iter_child_nodes(obj):

        if not is_private(node):
            check_result = check(node, ignore_ambiguous_signatures)
            if check_result is not None:
                yield from check_result


@check.register
def check_module(
    module: ast.Module, ignore_ambiguous_signatures: bool = True
) -> Iterator[Tuple[ast.FunctionDef, Set[str], Set[str]]]:
    """Check a module.

    Parameters
    ----------
    module : ast.Module
        The module in which to check functions and classes.
    ignore_ambiguous_signatures : bool, optional
        Whether to ignore extra documented arguments if the function as an
        ambiguous (*args / **kwargs) signature (the default is True).

    Returns
    -------
    dict
    """

    for node in ast.iter_child_nodes(module):
        if not is_private(node):
            check_result = check(node, ignore_ambiguous_signatures)
            if check_result is not None:
                yield from check_result


def get_signature_params(
    node: Union[ast.FunctionDef, ast.AsyncFunctionDef],
    ignore: Container[str] = ("self", "cls"),
) -> Tuple[Set[str], bool]:
    """Get parameters in a function signature.

    Parameters
    ----------
    node : Union[ast.FunctionDef, ast.AsyncFunctionDef]
        An ast function node
    ignore : tuple
        Which parameter names to ignore (the default is ("self", "cls"),
        which don't need documenting)

    Returns
    -------
    signature_params : Set[str]
    ambiguous : bool
    """

    signature_params = {
        argument.arg
        for argument in itertools.chain(node.args.args, node.args.kwonlyargs)
        if argument.arg not in ignore
    }
    ambiguous = node.args.vararg is not None or node.args.kwarg is not None
    return signature_params, ambiguous


def get_doc_params(
    node: Union[ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef]
) -> Set[str]:
    """Get parameters in a function signature.

    Parameters
    ----------
    node : Union[ast.FunctionDef, ast.AsyncFunctionDef]
        An ast function node

    Returns
    -------
    signature_params : Set[str]
    ambiguous : bool
    """
    docstring = ast.get_docstring(node)
    if docstring is not None:
        return {arg[0] for arg in NumpyDocString(docstring)["Parameters"]}
    else:
        return set()


def compare_args(
    signature_args: set, docced_args: set, ambiguous: bool
) -> Tuple[list, list]:
    """[summary]

    Parameters
    ----------
    signature_args : set
        The arguments in the function signature
    docced_args : set
        The arguments in the docstring.
    ambiguous : bool
        Whether the function is ambiguous.

    Returns
    -------
    underdocumented : list
    overdocumented : list
    """

    underdocumented = list(signature_args - docced_args)
    overdocumented = [] if ambiguous else list(docced_args - signature_args)

    return underdocumented, overdocumented
