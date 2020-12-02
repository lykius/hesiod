from pathlib import Path
from pprint import pprint

from hesiod.ui import TUI

template_file = Path("tests/templates/complex.yaml")
base_cfg_dir = Path("tests/cfg")

tui = TUI(template_file, base_cfg_dir)
run_cfg = tui.show()

pprint(run_cfg)
