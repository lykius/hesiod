from pathlib import Path

from hesiod.ui.tui.widgets.wgtfactory import BaseWidgetParser, BoolWidgetParser
from hesiod.ui.tui.widgets.wgtfactory import LiteralWidgetParser, OptionsWidgetParser
from hesiod.ui.tui.widgets.wgthandler import BaseWidgetHandler


def test_widget_handler() -> None:
    cfgs = [
        ["test_int", 1],
        ["test_float_1", 1.2345],
        ["test_float_2", 1e-5],
        ["test_str", "some string"],
        ["test_bool", False],
        ["test_list", [1, "test", [1, 2, 3], {4, 5, 6}]],
        ["test_tuple", (2.3, True, (7, 8, 9), 1e-6)],
        ["test_set", {"a", "b", "c", "d"}],
    ]

    for cfg in cfgs:
        handler, widget = LiteralWidgetParser.parse(cfg[0], "", cfg[1], Path())[0]
        result = handler.update_cfg({}, widget)
        assert result[cfg[0]] == cfg[1]


def test_bool_widget_handler() -> None:
    cfgs = [["test_1", "@BOOL(true)", True], ["test_2", "@BOOL(false)", False]]

    for cfg in cfgs:
        handler, widget = BoolWidgetParser.parse(cfg[0], "", cfg[1], Path())[0]
        result = handler.update_cfg({}, widget)
        assert result[cfg[0]] == cfg[2]


def test_options_widget_handler() -> None:
    cfgs = [
        ["test_1", "@OPTIONS(1; 2; 3)", 1],
        ["test_2", "@OPTIONS(1.2; 2.3)", 1.2],
        ["test_3", "@OPTIONS(1e-4; 1e-5)", 1e-4],
        ["test_4", '@OPTIONS("op1"; "op2")', "op1"],
        ["test_5", "@OPTIONS(True; False)", True],
        ["test_6", "@OPTIONS([1, 2, 3]; [4, 5, 6])", [1, 2, 3]],
        ["test_7", "@OPTIONS((7, 8, 9); (3, 2, 1))", (7, 8, 9)],
        ["test_8", '@OPTIONS({"a", "b"}; {"c", "d"})', {"a", "b"}],
    ]

    for cfg in cfgs:
        handler, widget = OptionsWidgetParser.parse(cfg[0], "", cfg[1], Path())[0]
        result = handler.update_cfg({}, widget)
        assert result[cfg[0]] == cfg[2]


def test_base_widget_handler(base_cfg_dir: Path) -> None:
    handler, widget = BaseWidgetParser.parse("test", "", "@BASE(params)", base_cfg_dir)[0]
    result = handler.update_cfg({}, widget)
    assert isinstance(result["test"], dict)
    assert result["test"][BaseWidgetHandler.BASE_KEY] == "params.default"
