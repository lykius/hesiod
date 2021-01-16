import pkg_resources

from hesiod.core import get_cfg_copy, get_out_dir, get_run_name, hcfg, hmain

__version__ = pkg_resources.get_distribution("hesiod").version
__all__ = ["__version__", "hmain", "hcfg", "get_cfg_copy", "get_out_dir", "get_run_name"]
