from typing import Any, Callable, Dict, List, Tuple, Union
from npyscreen.wgwidget import Widget  # type: ignore
from npyscreen import TitleText  # type: ignore

from hesiod.cfgparse import CFGT

WIDGET_T = Tuple[Callable[..., Widget], Dict[str, Any]]
PARSER_CONDITION_T = Callable[[Any], bool]
PARSER_T = Callable[
    [str, str, Any],
    List[WIDGET_T],
]
PARSERS_T = List[Tuple[PARSER_CONDITION_T, PARSER_T]]


class WidgetFactory:
    SPECIAL_CHAR = "@"
    PREFIX = "    "

    @staticmethod
    def get_parsers() -> PARSERS_T:
        """Create a list of parsers, along with the conditions to trigger them.

        Important: conditions are checked in the same order in which they
        are inserted into the list.

        Returns:
            The list of parsers and their conditions.
        """
        parsers: PARSERS_T = []

        # special
        condition = (
            lambda x: isinstance(x, str) and len(x) > 0 and x[0] == WidgetFactory.SPECIAL_CHAR
        )
        parsers.append((condition, WidgetFactory.parse_special))

        # recursive
        condition = lambda x: isinstance(x, dict)
        parsers.append((condition, WidgetFactory.parse_recursive))

        # literal
        condition = lambda x: type(x) in [int, float, str, list]
        parsers.append((condition, WidgetFactory.parse_literal))
        return parsers

    @staticmethod
    def get_widgets(cfg: CFGT, prefix: str = "") -> List[WIDGET_T]:
        """Prepare widgets for a given config.

        Args:
            cfg: the config.
            prefix: prefix for the name of the returned widgets.

        Returns:
            The list of the widgets for the given config.
        """
        widgets: List[WIDGET_T] = []
        parsers = WidgetFactory.get_parsers()

        for k in cfg:
            for condition, parser in parsers:
                if condition(cfg[k]):
                    widgets.extend(parser(k, prefix, cfg[k]))
                    break

        return widgets

    @staticmethod
    def parse_literal(
        cfg_key: str, prefix: str, cfg_value: Union[int, float, str, list]
    ) -> List[WIDGET_T]:
        """Parse a literal config and return a TitleText widget.

        Args:
            cfg_key: name of the config.
            prefix: prefix for the name of the config.
            cfg_value: literal value of the config.

        Returns:
            A list with the TitleText widget for the given config.
        """
        widgets: List[WIDGET_T] = []

        name = f"{prefix}{cfg_key}:"
        begin_entry_at = len(name) + 1
        kwargs = {
            "name": name,
            "value": str(cfg_value),
            "begin_entry_at": begin_entry_at,
            "use_two_lines": False,
        }
        widgets.append((TitleText, kwargs))

        return widgets

    @staticmethod
    def parse_recursive(cfg_key: str, prefix: str, cfg_value: CFGT) -> List[WIDGET_T]:
        """Parse a recursive config and returns the list of widgets associated to it.

        Args:
            cfg_key: name of the config.
            prefix: prefix for the name of the config (used for recursive calls).
            cfg_value: a dictionary with the config associated to cfg_key.

        Returns:
            A list with the widgets associated to the given recursive config.
        """
        widgets: List[WIDGET_T] = []

        kwargs = {"name": f"{prefix}{cfg_key}:", "use_two_lines": False}
        widgets.append((TitleText, kwargs))

        children_prefix = f"{prefix}{WidgetFactory.PREFIX}"
        widgets.extend(WidgetFactory.get_widgets(cfg_value, prefix=children_prefix))

        return widgets

    @staticmethod
    def parse_special(cfg_key: str, prefix: str, cfg_value: str) -> List[WIDGET_T]:
        """Parse special config.

        A special config can be one of the following:
        - @FILE(dir) -> allows to choose a file from dir
        - @DATE -> allows to pick a date
        - @OPTIONS(base_cfg) -> allows to choose a config from base_cfg.

        Args:
            cfg_key: name of the config.
            prefix: prefix for the name of the config.
            cfg_value: the special config to be parsed.

        Returns:
            A list with the appropriate widget for the given config.
        """
        widgets: List[WIDGET_T] = []

        return widgets
