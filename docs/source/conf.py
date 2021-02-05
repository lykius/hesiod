import sys
from pathlib import Path

hesiod_path = Path("../hesiod")
sys.path.append(str(hesiod_path.absolute()))

from hesiod import __version__

project = "Hesiod"
copyright = "2021, Luca De Luigi"
author = "Luca De Luigi"
release = __version__

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
]
napoleon_google_docstring = True

exclude_patterns = []

html_static_path = ["_static"]
templates_path = ["_templates"]
html_theme = "sphinx_rtd_theme"
