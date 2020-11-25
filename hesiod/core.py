from typing import Dict, Optional, cast, Callable, TypeVar, Type, Any
import functools
from pathlib import Path

from hesiod.cfgparse import get_parser


_CFG: Dict[str, Any] = {}
T = TypeVar("T")
Function = Callable[..., Any]


def main(base_cfg_dir: Path, run_cfg_file: Optional[Path] = None) -> Callable[[Function], Function]:
    """Decorator for a given function.

    The decorator loads the configuration with the right parser
    and runs the given function.

    Args:
        base_cfg_dir: the path to the directory with all the config files.
        run_cfg_file: the path to the config file created by the user for this run (optional).

    Returns:
        Function wrapped in the decorator.
    """

    def decorator(fn: Function) -> Function:
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


def get_param(name: str, t: Optional[Type[T]] = None) -> T:
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
