# Using `docargs` as a command line tool

If you don't want to use the [flake8 integration](using-flake8.md), you can
simply use docargs from the command line. Running the following:

```
docargs my_python_file.py
```

will check the specified file for signature / docstring mismatches. If you want
to run this on many files at once, you can do the following:

```
docargs my_module/**/*.py
```

This will check every file ending in `.py` in the directory *my_module*.

Because docargs will exit with an error code if there are mismatches, you can
use this in your CI pipeline. 
