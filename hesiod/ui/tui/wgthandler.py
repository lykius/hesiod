from copy import deepcopy
from typing import Any, Dict, Type, Union
from weakref import CallableProxyType

from hesiod.cfgparse import BASE_KEY, CFG_T


class WidgetHandler:
    def __init__(self, cfg_key: str) -> None:
        """Create a handler for a widget.

        Args:
            cfg_key: the key of the handled config.
        """
        self.cfg_key = cfg_key

    def get_value(self, widget: CallableProxyType) -> Any:
        """Extract the value from the given widget.

        Args:
            widget: the widget with the value of interest.

        Returns:
            The value extracted from the given widget.
        """
        return widget.get_value()

    def update_cfg(self, cfg: CFG_T, widget: CallableProxyType) -> CFG_T:
        """Update the given config by adding the value extracted
        from the given widget in the right place.

        Args:
            cfg: the config to be updated.
            widget: the widget with the value of interest.

        Returns:
            The updated config.
        """
        updated_cfg = deepcopy(cfg)

        keys = self.cfg_key.split(".")
        curr_cfg = updated_cfg
        for key in keys[:-1]:
            if key not in curr_cfg:
                curr_cfg[key] = {}
            curr_cfg = curr_cfg[key]

        value = self.get_value(widget)
        curr_cfg[keys[-1]] = value

        return updated_cfg


class LiteralWidgetHandler(WidgetHandler):
    def __init__(self, cfg_key: str, t: Type[Union[int, float, str]]) -> None:
        WidgetHandler.__init__(self, cfg_key)
        self.t = t

    def get_value(self, widget: CallableProxyType) -> Any:
        return self.t(widget.get_value())


class OptionsWidgetHandler(WidgetHandler):
    def __init__(self, cfg_key: str, options: Dict[str, str]) -> None:
        WidgetHandler.__init__(self, cfg_key)
        self.options = options

    def get_value(self, widget: CallableProxyType) -> Any:
        selected_value = widget.get_selected_objects()[0]
        return {BASE_KEY: self.options[selected_value]}
