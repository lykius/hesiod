from ast import literal_eval
from copy import deepcopy
from typing import Any, List

from asciimatics.widgets import Widget  # type: ignore

from hesiod.cfgparse import BASE_KEY, CFG_T


class WidgetHandler:
    def __init__(self, cfg_key: str) -> None:
        """Create a handler for a widget.

        Args:
            cfg_key: the key of the handled config.
        """
        self.cfg_key = cfg_key

    def get_value(self, widget: Widget) -> Any:
        """Extract the value from the given widget.

        Args:
            widget: the widget with the value of interest.

        Returns:
            The value extracted from the given widget.
        """
        try:
            value = literal_eval(widget.value)
        except (ValueError, SyntaxError):
            value = widget.value

        return value

    def update_cfg(self, cfg: CFG_T, widget: Widget) -> CFG_T:
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

    def get_value(self, widget: Widget) -> Any:
        selected_value = [BoolWidgetHandler.TRUE, BoolWidgetHandler.FALSE][widget.value]
        return selected_value == BoolWidgetHandler.TRUE


class OptionsWidgetHandler(WidgetHandler):
    def __init__(self, cfg_key: str, options: List[Any]) -> None:
        WidgetHandler.__init__(self, cfg_key)
        self.options = options

    def get_value(self, widget: Widget) -> Any:
        selected_value = widget.value
        return self.options[selected_value]


class BaseWidgetHandler(WidgetHandler):
    def __init__(self, cfg_key: str, options: List[str]) -> None:
        WidgetHandler.__init__(self, cfg_key)
        self.options = options

    def get_value(self, widget: Widget) -> Any:
        selected_value = widget.value
        return {BASE_KEY: self.options[selected_value]}
