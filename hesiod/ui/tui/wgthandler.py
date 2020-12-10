from ast import literal_eval
from copy import deepcopy
from typing import Any, Dict
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
        try:
            value = literal_eval(widget.get_value())
        except (ValueError, SyntaxError):
            value = widget.get_value()

        return value

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


class BoolWidgetHandler(WidgetHandler):
    TRUE = "true"
    FALSE = "false"

    def __init__(self, cfg_key: str) -> None:
        WidgetHandler.__init__(self, cfg_key)

    def get_value(self, widget: CallableProxyType) -> Any:
        selected_value = widget.get_selected_objects()[0]
        return selected_value == BoolWidgetHandler.TRUE


class OptionsWidgetHandler(WidgetHandler):
    def __init__(self, cfg_key: str) -> None:
        WidgetHandler.__init__(self, cfg_key)

    def get_value(self, widget: CallableProxyType) -> Any:
        selected_value = widget.get_selected_objects()[0]
        return selected_value


class BaseWidgetHandler(WidgetHandler):
    def __init__(self, cfg_key: str, options: Dict[str, str]) -> None:
        WidgetHandler.__init__(self, cfg_key)
        self.options = options

    def get_value(self, widget: CallableProxyType) -> Any:
        selected_value = widget.get_selected_objects()[0]
        return {BASE_KEY: self.options[selected_value]}
