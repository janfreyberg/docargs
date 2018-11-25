# Using `docargs` as a flake8 plugin

[flake8](http://flake8.pycqa.org/en/latest/) is a popular python
[linting program](https://en.wikipedia.org/wiki/Lint_(software)). Since many
people use it already, docargs integrates with flake8 and provides these two
errors:

- **D001** is raised if you have not documented some of your arguments.
- **D002** is raised if you have a parameter in your docstring that is not in your function signature.

flake8 is enabled by default when you install docargs. Because many editors,
such as [Visual Studio Code](https://code.visualstudio.com/) or
[Atom](https://atom.io/), support flake8 integration, docargs can integrate
with those editors.

This also means that any flake8 checks you run from the command line will
fail if you have not yet documented your parameters. For an example of how
to leverage this in your CI pipeline, take a look at the
[travis configuration](https://github.com/janfreyberg/docargs/blob/master/.travis.yml)
for docargs.
