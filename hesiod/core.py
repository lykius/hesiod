import functools
import re
import sys
from ast import literal_eval
from copy import deepcopy
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, List, Optional, Type, TypeVar, Union, cast

from typeguard import check_type

from hesiod.cfg.cfghandler import CFG_T, RUN_NAME_KEY, ConfigHandler
from hesiod.ui import TUI

T = TypeVar("T")
FUNCTION_T = Callable[..., Any]
_CFG: CFG_T = {}
RUN_FILE_NAME = "run.yaml"
OUT_DIR_KEY = "***hesiod_out_dir***"
RUN_NAME_STRATEGY_DATE = "date"
RUN_NAME_DATE_FORMAT = "%Y-%m-%d-%H-%M-%S"


def _parse_args(args: List[str]) -> None:
    """Parse the given args and add them to the global config.

    Each arg is expected with the format "{prefix}{key}{sep}{value}".
    {prefix} is optional and can be any amount of the char "-".
    {sep} is mandatory and can be one of "=", ":".
    {key} cannot contain the chars "-", "=" and ":".
    {value} can contain everything.

    Args:
        args: The list of args to be parsed.

    Raises:
        ValueError: If one of the given args is a not supported format.
    """
    for arg in args:
        pattern = r"^-*(?P<key>[^-=:]+)[=:]{1}(?P<value>.+)$"
        match = re.match(pattern, arg)

        if match is None:
            raise ValueError(f"One of the arg is in a not supported format {arg}.")
        else:
            while arg[0] == "-":
                arg = arg[1:]

            key = match.group("key")
            value = match.group("value")

            try:
                value = literal_eval(value)
            except (ValueError, SyntaxError):
                pass

            key_splits = key.split(".")
            cfg = _CFG
            for key in key_splits[:-1]:
                if key not in cfg:
                    cfg[key] = {}
                cfg = cfg[key]

            last_key = key_splits[-1]
            if last_key not in cfg:
                cfg[last_key] = {}
            cfg[last_key] = value


def _get_cfg(
    base_cfg_path: Path,
    template_cfg_path: Optional[Path],
    run_cfg_path: Optional[Path],
) -> CFG_T:
    """Load config either from template file or from run file.

    Args:
        base_cfg_path: The path to the directory with all the config files.
        template_cfg_path: The path to the template config file for this run.
        run_cfg_path: The path to the config file created by the user for this run.

    Raises:
        ValueError: If both template_cfg_path and run_cfg_path are None.

    Returns:
        The loaded config.
    """
    if run_cfg_path is not None:
        return ConfigHandler.load_cfg(run_cfg_path, base_cfg_path)
    elif template_cfg_path is not None:
        template_cfg = ConfigHandler.load_cfg(template_cfg_path, base_cfg_path)
        tui = TUI(template_cfg, base_cfg_path)
        return tui.show()
    else:
        msg = "Either a valid run file or a template file must be passed to hesiod."
        raise ValueError(msg)


def _get_default_run_name(strategy: str) -> str:
    """Get a run name according the given strategy.

    Args:
        strategy: The strategy to use to create the run name.

    Returns:
        The created run name.
    """
    run_name = ""
    if strategy == RUN_NAME_STRATEGY_DATE:
        now = datetime.now()
        run_name = now.strftime(RUN_NAME_DATE_FORMAT)

    return run_name


def _create_out_dir_and_save_run_file(
    cfg: CFG_T,
    out_dir_root: str,
    run_cfg_path: Optional[Path],
) -> None:
    """Create output directory for the current run.

    A new directory is created for the current run
    and the run file is saved in it (if needed).

    Args:
        cfg: The loaded config.
        out_dir_root: The root for output directories.
        run_cfg_path: The path to the config file created by the user for this run.

    Raises:
        ValueError: If the run name is not specified in the given config.
    """
    run_name = cfg.get(RUN_NAME_KEY, "")
    if run_name == "":
        msg = f"The config must contain a valid name for the run (key={RUN_NAME_KEY})."
        raise ValueError(msg)

    run_dir = Path(out_dir_root) / Path(run_name)
    run_file = run_dir / RUN_FILE_NAME

    create_dir = True
    if run_cfg_path is not None:
        create_dir = run_file.absolute() != run_cfg_path.absolute()

    if create_dir:
        run_dir.mkdir(parents=True, exist_ok=False)
        cfg[OUT_DIR_KEY] = str(run_dir.absolute())
        ConfigHandler.save_cfg(cfg, run_file)


def hmain(
    base_cfg_dir: Union[str, Path],
    template_cfg_file: Optional[Union[str, Path]] = None,
    run_cfg_file: Optional[Union[str, Path]] = None,
    create_out_dir: bool = True,
    out_dir_root: str = "logs",
    run_name_strategy: Optional[str] = RUN_NAME_STRATEGY_DATE,
    parse_cmd_line: bool = True,
) -> Callable[[FUNCTION_T], FUNCTION_T]:
    """Decorator for a given function.

    The decorator loads the configuration with the right parser
    and runs the given function.

    Args:
        base_cfg_dir: The path to the directory with all the config files.
        template_cfg_file: The path to the template config file for this run.
        run_cfg_file: The path to the config file created by the user for this run.
        create_out_dir: A flag that indicates whether hesiod should create
            an output directory or not.
        out_dir_root: The root for output directories.
        run_name_strategy: The strategy to assign a default run name if this is
            not specified by user (available options: "date").
        parse_cmd_line: A flag that indicates whether hesiod should parse args
            from the command line or not.

    Raises:
        ValueError: If both template_cfg_file and run_cfg_file are None.
        ValueError: If hesiod is asked to parse the command line and one
            of the args is in a not supported format.
        ValueError: If the run name is not specified in the run file
            and no default strategy is specified.

    Returns:
        Function wrapped in the decorator.
    """

    def decorator(fn: FUNCTION_T) -> FUNCTION_T:
        @functools.wraps(fn)
        def decorated_fn(*args: Any, **kwargs: Any) -> Any:
            global _CFG

            bcfg_path = Path(base_cfg_dir)
            run_cfg_path = Path(run_cfg_file) if run_cfg_file else None
            template_cfg_path = Path(template_cfg_file) if template_cfg_file else None

            _CFG = _get_cfg(bcfg_path, template_cfg_path, run_cfg_path)

            if parse_cmd_line and len(sys.argv) > 1:
                _parse_args(sys.argv[1:])

            run_name = _CFG.get(RUN_NAME_KEY, "")
            if run_name == "" and run_name_strategy is not None:
                run_name = _get_default_run_name(run_name_strategy)
                _CFG[RUN_NAME_KEY] = run_name

            if run_name == "":
                msg = (
                    f"A valid name must be provided for the run. Provide one "
                    f"by setting a value for the key {RUN_NAME_KEY} or "
                    f'selecting a default strategy (e.g. "date")'
                )
                raise ValueError(msg)

            if create_out_dir:
                _create_out_dir_and_save_run_file(_CFG, out_dir_root, run_cfg_path)

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

    if t is not None:
        check_type(name, value, t)

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


def get_run_name() -> str:
    """Get the name of the current run.

    Raises:
        ValueError: if the current run has no name (it should never happen).

    Returns:
        The name of the current run.
    """
    run_name = _CFG.get(RUN_NAME_KEY, "")
    if run_name == "":
        raise ValueError("Something went wrong: current run has no name.")

    return run_name
