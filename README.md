# docargs

A package to check that you have documented all your parameters.

Docargs is written with continuous integration in mind: It will raise an error
if you have not documented all your function arguments. It's easy to forget, but
it's also important not to - so you should automate a test of it!

To use, simply `pip install git+https://github.com/janfreyberg/docargs`, and run
`docargs <packagename>`.

`docargs` will import your package, so if there are side effects on import,
those will occur.

Currently, `docargs` only works with `numpydoc`-style docstrings. 
