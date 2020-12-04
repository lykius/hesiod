import functools
from copy import deepcopy
from pathlib import Path
from typing import Any, Callable, Optional, Type, TypeVar, cast

from hesiod.cfgparse import CFG_T, RUN_NAME_KEY, get_parser
from hesiod.ui import TUI

T = TypeVar("T")
FUNCTION_T = Callable[..., Any]
_CFG: CFG_T = {}
RUN_FILE_NAME = "run.yaml"
OUT_DIR_KEY = "***hesiod_out_dir***"


def hmain(
    base_cfg_dir: Path,
    template_cfg_file: Optional[Path] = None,
    run_cfg_file: Optional[Path] = None,
    create_out_dir: bool = True,
    out_dir_root: str = "logs",
) -> Callable[[FUNCTION_T], FUNCTION_T]:
    """Decorator for a given function.

    The decorator loads the configuration with the right parser
    and runs the given function.

    Args:
        base_cfg_dir: the path to the directory with all the config files.
        template_cfg_file: the path to the template config file for this run (optional).
        run_cfg_file: the path to the config file created by the user for this run (optional).
        create_out_dir: flag that indicates whether hesiod should create an output directory or not.
        out_dir_root: root for output directories.

    Raises:
        ValueError: if both template_cfg_file and run_cfg_file are None.
        ValueError: if the run name is not specified in the run file.

    Returns:
        Function wrapped in the decorator.
    """

    def decorator(fn: FUNCTION_T) -> FUNCTION_T:
        @functools.wraps(fn)
        def decorated_fn(*args: Any, **kwargs: Any) -> Any:
            global _CFG

            if run_cfg_file is None and template_cfg_file is None:
                msg = "Either a valid run file or a template file must be passed to hesiod."
                raise ValueError(msg)

            if run_cfg_file is not None:
                parser = get_parser(run_cfg_file.suffix)
                _CFG = parser.load_cfg(run_cfg_file, base_cfg_dir)
            elif template_cfg_file is not None:
                parser = get_parser(template_cfg_file.suffix)
                template_cfg = parser.load_cfg(template_cfg_file, base_cfg_dir)
                tui = TUI(template_cfg, base_cfg_dir, parser)
                _CFG = tui.show()

            if create_out_dir:
                run_name = _CFG.get(RUN_NAME_KEY, "")
                if len(run_name) == 0:
                    msg = f"The run file must contain a valid name for the run ({RUN_NAME_KEY})."
                    raise ValueError(msg)

                run_dir = Path(out_dir_root) / Path(run_name)
                run_dir.mkdir(parents=True, exist_ok=False)
                _CFG[OUT_DIR_KEY] = str(run_dir.absolute())
                run_file = run_dir / RUN_FILE_NAME
                parser = get_parser(run_file.suffix)
                parser.save_cfg(_CFG, run_file)

            return fn(*args, **kwargs)

        return decorated_fn

    return decorator


def hcfg(name: str, t: Optional[Type[T]] = None) -> T:
    """Get the requested parameter from global configuration.

    Args:
        name: name of the parameter.
        t: type of the parameter.

    Raises:
        TypeError: if the requested parameter is not of the required type.

    Returns:
        The requested parameter.
    """
    value = _CFG
    for n in name.split("."):
        value = value[n]

    if t is not None and not isinstance(value, t):
        raise TypeError(f"{name} is of type {type(value)} but requested {t}")

    value = deepcopy(value)

    return cast(T, value)


def get_cfg_copy() -> CFG_T:
    """Return a copy of the global configuration.

    Returns:
        A copy of the global configuration.
    """
    return deepcopy(_CFG)


def get_out_dir() -> Path:
    """Get path to the output directory for the current run.

    Returns:
        Path to the output directory.
    """
    out_dir = deepcopy(_CFG[OUT_DIR_KEY])
    return Path(out_dir)
