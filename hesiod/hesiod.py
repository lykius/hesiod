from typing import cast, Callable, TypeVar, Type, Any

import hydra
from hydra.types import TaskFunction
from omegaconf import DictConfig


_CFG = None
T = TypeVar("T")


def hesiod(task_function: TaskFunction) -> Callable[[TaskFunction], Any]:
    """Save configuration loaded from hydra and run task_function.

    Args:
        task_function : task function to be run

    Returns:
        Task function wrapped in hydra environment.
    """

    @hydra.main(config_path="conf", config_name="run")
    def hydra_entry_point(cfg: DictConfig) -> Any:
        global _CFG
        _CFG = cfg
        task_function()

    return hydra_entry_point


def get_param(name: str, t: Type[T] = object) -> T:
    """Get requested parameter from global configuration.

    Args:
        name : name of the parameter
        t : type of the parameter

    Raises:
        ValueError: if the requested parameter is not of the required type

    Returns:
        The requested parameter
    """
    value = _CFG
    for n in name.split("."):
        value = getattr(value, n)
    if not isinstance(value, t):
        raise ValueError(f"{name} is {type(value)} but requested {t}")
    return cast(T, value)
