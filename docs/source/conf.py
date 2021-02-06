import sys
from pathlib import Path

sys.path.append(str(Path("../..").absolute()))

project = "Hesiod"
copyright = "2021, Luca De Luigi"
author = "Luca De Luigi"

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
]
napoleon_google_docstring = True

exclude_patterns = []

html_static_path = ["_static"]
templates_path = ["_templates"]
html_theme = "sphinx_rtd_theme"

release = "0.3.1"
