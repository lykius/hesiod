from typing import Optional, cast, Callable, TypeVar, Type, Any
import functools

from omegaconf import OmegaConf


_CFG = None
T = TypeVar("T")
Function = Callable[..., Any]


def main(cfg_path: Optional[str] = None) -> Callable[[Function], Function]:
    """Decorator for a given function.

    The decorator loads the configuration with OmegaConf
    and runs the given function.

    Args:
        cfg_path: the path to the cfg file created by the user (optional).

    Returns:
        Function wrapped in the decorator.
    """

    def decorator(fn: Function) -> Function:
        @functools.wraps(fn)
        def decorated_fn(*args: Any, **kwargs: Any) -> Any:
            global _CFG
            if cfg_path is not None:
                _CFG = OmegaConf.load(cfg_path)
            return fn(*args, **kwargs)

        return decorated_fn

    return decorator


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
