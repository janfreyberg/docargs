import ast
from docargs.check import get_doc_params, get_signature_params, check

SAMPLE_DOCCED_FN = ast.parse("""
def function_with_types_in_docstring(param1, param2):
    \"\"\"Example function with types documented in the docstring.

    `PEP 484`_ type annotations are supported. If attribute, parameter, and
    return types are annotated according to `PEP 484`_, they do not need to be
    included in the docstring:

    Parameters
    ----------
    param1 : int
        The first parameter.
    param2 : str
        The second parameter.

    Returns
    -------
    bool
        True if successful, False otherwise.

    .. _PEP 484:
        https://www.python.org/dev/peps/pep-0484/

    \"\"\"
""").body[0]


def test_correctly_docced_fn():
    _, over, under = next(check(SAMPLE_DOCCED_FN))
    assert over == under == []
    assert (get_doc_params(SAMPLE_DOCCED_FN)
            == get_signature_params(SAMPLE_DOCCED_FN)[0]
            == {"param1", "param2"})


SAMPLE_UNDOCCED_FN = ast.parse("""
def function_with_types_in_docstring(param1, param2):
    \"\"\"Example function with types documented in the docstring.

    `PEP 484`_ type annotations are supported. If attribute, parameter, and
    return types are annotated according to `PEP 484`_, they do not need to be
    included in the docstring:

    Returns
    -------
    bool
        True if successful, False otherwise.

    .. _PEP 484:
        https://www.python.org/dev/peps/pep-0484/

    \"\"\"
""").body[0]


def test_incorrectly_docced_fn():
    _, under, over = next(check(SAMPLE_UNDOCCED_FN))
    assert over == []
    assert set(under) == {"param1", "param2"}
    assert get_doc_params(SAMPLE_UNDOCCED_FN) == set()
    assert (
        get_signature_params(SAMPLE_UNDOCCED_FN)[0]
        == {"param1", "param2"}
    )
    assert (
        get_doc_params(SAMPLE_UNDOCCED_FN)
        != get_signature_params(SAMPLE_UNDOCCED_FN)[0]
    )


SAMPLE_OVERDOCCED_FN = ast.parse("""
def function_with_types_in_docstring(param1, param2):
    \"\"\"Example function with types documented in the docstring.

    `PEP 484`_ type annotations are supported. If attribute, parameter, and
    return types are annotated according to `PEP 484`_, they do not need to be
    included in the docstring:

    Parameters
    ----------
    param1 : int
        The first parameter.
    param2 : str
        The second parameter.
    param3 : None
        An extra param

    Returns
    -------
    bool
        True if successful, False otherwise.

    .. _PEP 484:
        https://www.python.org/dev/peps/pep-0484/

    \"\"\"
""").body[0]


def test_over_docced_fn():
    _, under, over = next(check(SAMPLE_OVERDOCCED_FN))
    assert under == []
    assert set(over) == {"param3"}


DOCCED_CLASS = ast.parse("""
class ExampleClass(object):
    \"\"\"The summary line for a class docstring should fit on one line.

    If the class has public attributes, they may be documented here
    in an ``Attributes`` section and follow the same formatting as a
    function's ``Args`` section. Alternatively, attributes may be documented
    inline with the attribute's declaration (see __init__ method below).

    Properties created with the ``@property`` decorator should be documented
    in the property's getter method.

    Attributes
    ----------
    attr1 : str
        Description of `attr1`.
    attr2 : :obj:`int`, optional
        Description of `attr2`.

    \"\"\"

    def __init__(self, param1, param2, param3):
        \"\"\"Example of docstring on the __init__ method.

        The __init__ method may be documented in either the class level
        docstring, or as a docstring on the __init__ method itself.

        Either form is acceptable, but the two should not be mixed. Choose one
        convention to document the __init__ method and be consistent with it.

        Parameters
        ----------
        param1 : str
            Description of `param1`.
        param2 : :obj:`list` of :obj:`str`
            Description of `param2`. Multiple
            lines are supported.
        param3 : :obj:`int`, optional
            Description of `param3`.

        \"\"\"
""").body[0]


def test_cls_with_param_docs_in_init_docstring():
    _, over, under = next(check(DOCCED_CLASS))
    assert over == under == []


ALT_DOCCED_CLASS = ast.parse("""
class ExampleClass(object):
    \"\"\"The summary line for a class docstring should fit on one line.

    If the class has public attributes, they may be documented here
    in an ``Attributes`` section and follow the same formatting as a
    function's ``Args`` section. Alternatively, attributes may be documented
    inline with the attribute's declaration (see __init__ method below).

    Properties created with the ``@property`` decorator should be documented
    in the property's getter method.

    Parameters
    ----------
    param1 : str
        Description of `param1`.
    param2 : :obj:`list` of :obj:`str`
        Description of `param2`. Multiple
        lines are supported.
    param3 : :obj:`int`, optional
        Description of `param3`.

    Attributes
    ----------
    attr1 : str
        Description of `attr1`.
    attr2 : :obj:`int`, optional
        Description of `attr2`.

    \"\"\"

    def __init__(self, param1, param2, param3):
        \"\"\"Example of docstring on the __init__ method.

        The __init__ method may be documented in either the class level
        docstring, or as a docstring on the __init__ method itself.

        Either form is acceptable, but the two should not be mixed. Choose one
        convention to document the __init__ method and be consistent with it.

        \"\"\"
""").body[0]


def test_cls_with_param_docs_in_class_docstring():
    _, over, under = next(check(ALT_DOCCED_CLASS))
    assert over == under == []


UN_DOCCED_CLASS = ast.parse("""
class ExampleClass(object):
    \"\"\"The summary line for a class docstring should fit on one line.

    If the class has public attributes, they may be documented here
    in an ``Attributes`` section and follow the same formatting as a
    function's ``Args`` section. Alternatively, attributes may be documented
    inline with the attribute's declaration (see __init__ method below).

    Properties created with the ``@property`` decorator should be documented
    in the property's getter method.

    Parameters
    ----------
    param1 : str
        Description of `param1`.
    param2 : :obj:`list` of :obj:`str`
        Description of `param2`. Multiple
        lines are supported.

    Attributes
    ----------
    attr1 : str
        Description of `attr1`.
    attr2 : :obj:`int`, optional
        Description of `attr2`.

    \"\"\"

    def __init__(self, param1, param2, param3):
        \"\"\"Example of docstring on the __init__ method.

        The __init__ method may be documented in either the class level
        docstring, or as a docstring on the __init__ method itself.

        Either form is acceptable, but the two should not be mixed. Choose one
        convention to document the __init__ method and be consistent with it.

        \"\"\"
""").body[0]


def test_cls_one_param_missing():
    _, under, over = next(check(UN_DOCCED_CLASS))
    assert set(under) == {"param3"}
    assert set(over) == set()


OVER_DOCCED_CLASS = ast.parse("""
class ExampleClass(object):
    \"\"\"The summary line for a class docstring should fit on one line.

    If the class has public attributes, they may be documented here
    in an ``Attributes`` section and follow the same formatting as a
    function's ``Args`` section. Alternatively, attributes may be documented
    inline with the attribute's declaration (see __init__ method below).

    Properties created with the ``@property`` decorator should be documented
    in the property's getter method.

    Parameters
    ----------
    param1 : str
        Description of `param1`.
    param2 : :obj:`list` of :obj:`str`
        Description of `param2`. Multiple
        lines are supported.
    param3 : :obj:`int`, optional
        Description of `param3`.
    param4 : :obj:`int`, optional
        Description of `param3`.

    Attributes
    ----------
    attr1 : str
        Description of `attr1`.
    attr2 : :obj:`int`, optional
        Description of `attr2`.

    \"\"\"

    def __init__(self, param1, param2, param3):
        \"\"\"Example of docstring on the __init__ method.

        The __init__ method may be documented in either the class level
        docstring, or as a docstring on the __init__ method itself.

        Either form is acceptable, but the two should not be mixed. Choose one
        convention to document the __init__ method and be consistent with it.

        \"\"\"
""").body[0]


def test_cls_one_param_extra():
    _, under, over = next(check(UN_DOCCED_CLASS))
    assert set(under) == {"param3"}
    assert set(over) == set()
