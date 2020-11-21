from typing import Optional, cast, Callable, TypeVar, Type, Any

import hydra
from omegaconf import DictConfig


_CFG = None
T = TypeVar("T")
TaskFunction = Callable[[], Any]


def hesiod(task_function: Callable) -> Callable[[TaskFunction], Any]:
    """Decorator for a given function.

    The decorato saves the configuration loaded by hydra
    and run the task function inside the hydra environment.

    Args:
        task_function : task function to be run.

    Returns:
        Task function wrapped in hydra environment.
    """

    @hydra.main(config_path="conf", config_name="conf")
    def hydra_entry_point(cfg: DictConfig) -> Any:
        global _CFG
        _CFG = cfg
        task_function()

    return hydra_entry_point


def get_param(name: str, t: Optional[Type[T]] = None) -> T:
    """Get requested parameter from global configuration.

    Args:
        name : name of the parameter.
        t : type of the parameter.

    Raises:
        ValueError: if the requested parameter is not of the required type.

    Returns:
        The requested parameter.
    """
    value = _CFG
    for n in name.split("."):
        value = getattr(value, n)
    if t is not None and not isinstance(value, t):
        raise ValueError(f"{name} is {type(value)} but requested {t}")
    return cast(T, value)
