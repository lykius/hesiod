from typing import Any, Callable, Dict, List, Tuple, Union
from npyscreen.wgwidget import Widget  # type: ignore
from npyscreen import TitleText, TitleDateCombo, TitleFilename, TitleSelectOne  # type: ignore
import re

from hesiod.cfgparse import CFGT

WIDGET_T = Tuple[Callable[..., Widget], Dict[str, Any]]
PARSER_CONDITION_T = Callable[[Any], bool]
PARSER_T = Callable[[str, str, Any], List[WIDGET_T]]
PARSERS_T = List[Tuple[PARSER_CONDITION_T, PARSER_T]]


class WidgetFactory:
    PREFIX = "    "
    DATE_PATTERN = "@DATE"
    FILE_PATTERN = "@FILE"
    OPTIONS_PATTERN = "@OPTION([0-9A-Za-z_]+)"

    @staticmethod
    def match(s: str, pattern: str) -> bool:
        """Check if a given string matches a pattern.

        Args:
            s: the string to be checked.
            pattern: the pattern to check.

        Returns:
            True if the given string matches the patter, False otherwise.
        """
        return bool(re.match(pattern, s))

    @staticmethod
    def get_parsers() -> PARSERS_T:
        """Create a list of parsers, along with the conditions to trigger them.

        Important: conditions are checked in the same order in which they
        are inserted into the list.

        Returns:
            The list of parsers and their conditions.
        """
        parsers: PARSERS_T = []

        # specials
        condition = lambda x: (
            isinstance(x, str) and WidgetFactory.match(x, WidgetFactory.DATE_PATTERN)
        )
        parsers.append((condition, WidgetFactory.parse_date))

        condition = lambda x: (
            isinstance(x, str) and WidgetFactory.match(x, WidgetFactory.FILE_PATTERN)
        )
        parsers.append((condition, WidgetFactory.parse_file))

        condition = lambda x: (
            isinstance(x, str) and WidgetFactory.match(x, WidgetFactory.OPTIONS_PATTERN)
        )
        parsers.append((condition, WidgetFactory.parse_options))

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
    def get_literal_widget(name: str, value: Union[int, float, str, list]) -> WIDGET_T:
        """Get a TitleText widget for a literal config.

        Args:
            name: name of the config.
            value: value for the config.

        Returns:
            The TitleText widget for the given config.
        """
        begin_entry_at = len(name) + 1
        kwargs = {
            "name": name,
            "value": str(value),
            "begin_entry_at": begin_entry_at,
            "use_two_lines": False,
        }
        return (TitleText, kwargs)

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
        widgets.append(WidgetFactory.get_literal_widget(name, cfg_value))

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

        kwargs = {"name": f"{prefix}{cfg_key}:", "use_two_lines": False, "editable": False}
        widgets.append((TitleText, kwargs))

        children_prefix = f"{prefix}{WidgetFactory.PREFIX}"
        widgets.extend(WidgetFactory.get_widgets(cfg_value, prefix=children_prefix))

        return widgets

    @staticmethod
    def parse_date(cfg_key: str, prefix: str, cfg_value: str) -> List[WIDGET_T]:
        """Parse date config and returns a TitleDateCombo widget.

        Args:
            cfg_key: name of the config.
            prefix: prefix for the name of the config.
            cfg_value: the date config to be parsed.

        Returns:
            A list with the TitleDateCombo widget for the given config.
        """
        widgets: List[WIDGET_T] = []

        name = f"{prefix}{cfg_key} (ENTER to select one):"
        begin_entry_at = len(name) + 1
        kwargs = {
            "name": name,
            "begin_entry_at": begin_entry_at,
            "use_two_lines": False,
        }
        widgets.append((TitleDateCombo, kwargs))

        return widgets

    @staticmethod
    def parse_file(cfg_key: str, prefix: str, cfg_value: str) -> List[WIDGET_T]:
        """Parse file config and returns a TitleDateCombo widget.

        Args:
            cfg_key: name of the config.
            prefix: prefix for the name of the config.
            cfg_value: the date config to be parsed.

        Returns:
            A list with the TitleDateCombo widget for the given config.
        """
        widgets: List[WIDGET_T] = []

        name = f"{prefix}{cfg_key} (TAB for autocompletion):"
        begin_entry_at = len(name) + 1
        kwargs = {
            "name": name,
            "begin_entry_at": begin_entry_at,
            "use_two_lines": False,
        }
        widgets.append((TitleFilename, kwargs))

        return widgets

    @staticmethod
    def parse_options(cfg_key: str, prefix: str, cfg_value: str) -> List[WIDGET_T]:
        """Parse options config and returns a TitleSelectOne widget.

        Args:
            cfg_key: name of the config.
            prefix: prefix for the name of the config.
            cfg_value: the options config to be parsed.

        Returns:
            A list with the TitleSelectOne widget for the given config.
        """
        widgets: List[WIDGET_T] = []

        name = f"{prefix}{cfg_key}:"
        values = ["option1", "option2", "option3"]
        kwargs = {
            "name": name,
            "values": values,
            "value": [0],
            "max_height": len(values),
            "begin_entry_at": len(name) + 1,
            "use_two_lines": False,
            "scroll_exit": True,
        }
        widgets.append((TitleSelectOne, kwargs))

        return widgets
