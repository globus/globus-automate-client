# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
import os
import sys

sys.path.insert(0, os.path.abspath("../../"))
autodoc_mock_imports = [
    "globus_sdk",
    "jsonschema",
    "graphviz",
    "click",
    "typer",
    "rich",
]
autodoc_typehints = "description"

# -- Project information -----------------------------------------------------

project = "Globus Automate Client"
copyright = "2020-2023, University of Chicago"
author = "Globus"

# The full version, including alpha/beta/rc tags
# release = "0.7.0"


# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    "sphinx.ext.autodoc",
    "sphinx_copybutton",
]

# Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"]

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ["cli_docs.rst"]

# The document containing the toctree directive
master_doc = "index"

# -- Options for HTML output -------------------------------------------------

html_title = "Globus Automate Client"
html_logo = "_static/images/globus-300x300-blue.png"
html_theme = "furo"

pygments_dark_style = "monokai"

html_static_path = ["_static"]


# -- Deprecation notice ------------------------------------------------------

rst_prolog = """
..  warning::

    The Globus Automate SDK and Globus Automate CLI are deprecated.

    The `Globus SDK`_ and `Globus CLI`_ have integrated their functionality
    and are able to interact with other Globus services, as well.

    It is strongly recommended that new projects use the Globus SDK and Globus CLI,
    and that existing projects begin migrating to the Globus SDK and Globus CLI.

..  _Globus SDK: https://globus-sdk-python.readthedocs.io/en/stable/
..  _Globus CLI: https://docs.globus.org/cli/

"""
