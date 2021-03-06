from pathlib import Path
from pprint import pprint

from hesiod import get_cfg_copy, hmain

template_file = Path("tests/configs/templates/complex.yaml")
base_cfg_dir = Path("tests/configs/bases")


@hmain(base_cfg_dir, template_cfg_file=template_file)
def test() -> None:
    cfg = get_cfg_copy()
    pprint(cfg)


test()
