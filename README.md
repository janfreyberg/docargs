# docargs

A package to check that you have documented all your parameters.

Docargs is written with continuous integration in mind: It will raise an error
if you have not documented all your function arguments. It's easy to forget, but
it's also important not to - so you should automate a test of it!

To use, simply `pip install docargs`, and run `docargs mypackage/**/*py`. Alternatively, docargs integrates with flake8, so running `flake8 mypackage` will also work.

To see it in action, check out the travis CI configuration
on this [repository](https://travis-ci.org/janfreyberg/docargs)

Currently, `docargs` only works with `numpydoc`-style docstrings. 
