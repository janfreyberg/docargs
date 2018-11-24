import ast
import itertools
import yaml
from functools import singledispatch
from typing import Dict, Optional, Set, Tuple, Union

from numpydoc.docscrape import NumpyDocString

from .identify import is_private, find_init


@singledispatch
def check(node, ignore_ambiguous_signatures: bool = True) -> Optional[Dict]:
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
    func: ast.FunctionDef, ignore_ambiguous_signatures: bool = False
) -> Optional[Dict]:
    """
    Check the documented and actual arguments for a function.
    """
    signature_args, ambiguous = get_signature_params(func)
    docced_args = get_doc_params(func)

    undocumented, overdocumented = compare_args(
        signature_args, docced_args, ignore_ambiguous_signatures and ambiguous
    )

    yield func, undocumented, overdocumented


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
        undocumented, overdocumented = compare_args(
            signature_args,
            docced_args,
            ignore_ambiguous_signatures and ambiguous,
        )
        yield init_method, undocumented, overdocumented


@check.register
def check_class(
    obj: ast.ClassDef, ignore_ambiguous_signatures: bool = False
) -> Optional[Dict]:

    if find_init(obj) is not None:
        yield from check_init(obj)

    for node in ast.iter_child_nodes(obj):

        if not is_private(node):
            check_result = check(node, ignore_ambiguous_signatures)
            if check_result is not None:
                yield from check_result


@check.register
def check_module(
    module: ast.Module, ignore_ambiguous_signatures: bool = True
) -> Dict:
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
                # print(node.name)
                # print(check_result)
                # node, underdocumented, overdocumented = check_result
                # if underdocumented or overdocumented:
                #     yield node, underdocumented, overdocumented


def get_signature_params(
    node: Union[ast.FunctionDef, ast.AsyncFunctionDef],
    ignore: Tuple[str] = ("self", "cls"),
) -> Tuple[Set[str], bool]:
    """Get parameters in a function signature.

    Parameters
    ----------
    node : Union[ast.FunctionDef, ast.AsyncFunctionDef]
        An ast function node
    ignore : tuple, optional
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
    node: Union[ast.FunctionDef, ast.AsyncFunctionDef]
) -> Set[str]:
    docstring = ast.get_docstring(node)
    if docstring is not None:
        return {arg[0] for arg in NumpyDocString(docstring)["Parameters"]}
    else:
        return set()


def compare_args(
    signature_args: set, docced_args: set, ambiguous: bool
) -> Tuple[list, list]:

    output = {}
    if signature_args - docced_args:
        output["Not in docstring"] = list(signature_args - docced_args)
    if docced_args - signature_args and not ambiguous:
        output["Not in signature"] = list(docced_args - signature_args)

    underdocumented = list(signature_args - docced_args)
    overdocumented = [] if ambiguous else list(docced_args - signature_args)

    return underdocumented, overdocumented
