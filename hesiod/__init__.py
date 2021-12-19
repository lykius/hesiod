import pkg_resources
from pkg_resources import DistributionNotFound

from hesiod.core import get_cfg_copy, get_out_dir, get_run_name, hcfg, hmain, set_cfg

__all__ = ["__version__", "hmain", "hcfg", "get_cfg_copy", "get_out_dir", "get_run_name", "set_cfg"]

try:
    __version__ = pkg_resources.get_distribution("hesiod").version
except DistributionNotFound:
    pass
