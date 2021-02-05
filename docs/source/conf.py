import sys
from pathlib import Path

from hesiod import __version__

hesiod_path = Path("/home/ldeluigi/dev/hesiod/hesiod")
sys.path.append(str(hesiod_path.absolute()))

project = "Hesiod"
copyright = "2021, Luca De Luigi"
author = "Luca De Luigi"
release = __version__

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
]
napoleon_google_docstring = True

templates_path = ["_templates"]

exclude_patterns = []

html_theme = "alabaster"
html_static_path = ["_static"]
