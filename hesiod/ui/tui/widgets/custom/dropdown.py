from asciimatics.widgets import DropdownList  # type: ignore


class CustomDropdownList(DropdownList):
    def update(self, frame_no: int) -> None:
        self._draw_label()
        text = "" if self._line is None else self._options[self._line][0]
        (colour, attr, background) = self._pick_colours("field", selected=self._has_focus)
        self._frame.canvas.print_at(text, self._x + self._offset, self._y, colour, attr, background)
