"""Installer."""
from setuptools import setup

# To use a consistent encoding
from codecs import open
import os.path

modulename = "docargs"
here = os.path.dirname(os.path.abspath(__file__))

version_ns = {}
with open(os.path.join(here, modulename, "version.py")) as f:
    exec(f.read(), {}, version_ns)
version = version_ns["version"]

blurb = "Check that all arguments are documented."
if os.path.isfile("README.md"):
    readme = open("README.md", "r").read()
else:
    readme = blurb

setup(
    name=modulename,
    version=version,
    description=blurb,
    long_description=readme,
    long_description_content_type="text/markdown",
    url="https://github.com/janfreyberg/{}".format(modulename),
    download_url=(
        "https://github.com/janfreyberg/{0}/{1}.tar.gz".format(
            modulename, version_ns["version"]
        )
    ),
    # Author details
    author="Jan Freyberg",
    author_email="jan@asidatascience.com",
    packages=["docargs"],
    keywords=["linting"],
    install_requires=["numpydoc", "click", "colorama", "pyyaml"],
    entry_points={"console_scripts": ["docargs = docargs:cli"]},
)
