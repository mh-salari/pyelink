"""Sphinx configuration for PyeLink documentation."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent / "_ext"))

project = "PyeLink"
author = "Mohammadhossein Salari"
copyright = "2025, Mohammadhossein Salari"  # noqa: A001

# Author website: https://mh-salari.ir

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
    "sphinx.ext.intersphinx",
    "sphinx_autodoc_typehints",
    "myst_parser",
    "settings_table",
]

# MyST (markdown) settings
source_suffix = {
    ".rst": "restructuredtext",
    ".md": "markdown",
}

# Napoleon settings (Google-style docstrings)
napoleon_google_docstring = True
napoleon_numpy_docstring = False
napoleon_include_init_with_doc = True
napoleon_use_ivar = True  # prevents duplicate attribute warnings with dataclasses

# Autodoc settings
autodoc_member_order = "bysource"
autodoc_typehints = "description"
autodoc_default_options = {
    "members": True,
    "undoc-members": True,
    "show-inheritance": True,
}

# Autosummary
autosummary_generate = True

# Intersphinx links to external docs
intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
    "numpy": ("https://numpy.org/doc/stable/", None),
}

# Theme
html_theme = "sphinx_rtd_theme"
html_theme_options = {
    "navigation_depth": 4,
}

# Mock imports for packages not available during docs build
# Backends are mutually exclusive and pylink requires the native EyeLink SDK
autodoc_mock_imports = [
    "pylink",
    "pygame",
    "psychopy",
    "pyglet",
    "pyaudio",
    "fixation_target",
]

# Suppress warnings from sphinx_autodoc_typehints about forward references
# in pydantic-generated code and classmethod subscripting on older Python
suppress_warnings = [
    "sphinx_autodoc_typehints.forward_reference",
    "sphinx_autodoc_typehints.guarded_import",
]

# General
exclude_patterns = ["_build"]
