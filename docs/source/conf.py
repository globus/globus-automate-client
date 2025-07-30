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
autodoc_typehints = "description"

# -- Project information -----------------------------------------------------

project = "Globus Automate Client"
copyright = "2020-2025, University of Chicago"
author = "Globus"

# -- General configuration ---------------------------------------------------

# Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"]

# The document containing the toctree directive
master_doc = "index"

# -- Options for HTML output -------------------------------------------------

html_title = "Globus Automate Client"
html_logo = "_static/images/globus-300x300-blue.png"
html_theme = "furo"

pygments_dark_style = "monokai"

html_static_path = ["_static"]
