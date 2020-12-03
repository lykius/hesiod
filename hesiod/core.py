import functools
from copy import deepcopy
from pathlib import Path
from typing import Any, Callable, Optional, Type, TypeVar, cast

from hesiod.cfgparse import CFG_T, get_parser

_CFG: CFG_T = {}
T = TypeVar("T")
FUNCTION_T = Callable[..., Any]


def hmain(
    base_cfg_dir: Path, run_cfg_file: Optional[Path] = None
) -> Callable[[FUNCTION_T], FUNCTION_T]:
    """Decorator for a given function.

    The decorator loads the configuration with the right parser
    and runs the given function.

    Args:
        base_cfg_dir: the path to the directory with all the config files.
        run_cfg_file: the path to the config file created by the user for this run (optional).

    Returns:
        Function wrapped in the decorator.
    """

    def decorator(fn: FUNCTION_T) -> FUNCTION_T:
        @functools.wraps(fn)
        def decorated_fn(*args: Any, **kwargs: Any) -> Any:
            global _CFG

            if run_cfg_file is not None:
                ext = run_cfg_file.suffix
                parser = get_parser(ext)(run_cfg_file, base_cfg_dir)
                _CFG = parser.load_cfg()

            return fn(*args, **kwargs)

        return decorated_fn

    return decorator


def hcfg(name: str, t: Optional[Type[T]] = None) -> T:
    """Get requested parameter from global configuration.

    Args:
        name: name of the parameter.
        t: type of the parameter.

    Raises:
        ValueError: if the requested parameter is not of the required type.

    Returns:
        The requested parameter.
    """
    value = _CFG
    for n in name.split("."):
        value = value[n]
    if t is not None and not isinstance(value, t):
        raise ValueError(f"{name} is of type {type(value)} but requested {t}")
    return cast(T, value)


def get_cfg_copy() -> CFG_T:
    """Return a copy of the global configuration.

    Returns:
        A copy of the global configuration.
    """
    return deepcopy(_CFG)
