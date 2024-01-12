import typing

from ableton.v3.base import depends
from ableton.v3.control_surface.components import (
    MixerComponent as MixerComponentBase,
)
from ableton.v3.control_surface.components import (
    Scrollable,
    ScrollComponent,
    SendIndexManager,
)


class SendIndexScrollable(Scrollable):
    def __init__(self, send_index_manager: SendIndexManager):
        super().__init__()
        self._send_index_manager = send_index_manager

    def can_scroll_up(self):
        return self._can_scroll(-1)

    def can_scroll_down(self):
        return self._can_scroll(1)

    def scroll_up(self):
        self._do_scroll(-1)

    def scroll_down(self):
        self._do_scroll(1)

    def _can_scroll(self, delta):
        num_sends = self._send_index_manager.num_sends
        current_index = self._send_index_manager.send_index

        def is_in_range(index):
            return index >= 0 and index < num_sends

        # Always allow scrolling if we're out of bounds, e.g. if sends
        # were removed.
        if not is_in_range(current_index):
            return True

        target_index = current_index + delta
        return is_in_range(target_index)

    def _do_scroll(self, delta):
        self._send_index_manager.send_index = (
            self._send_index_manager.send_index + delta
        )


class MixerComponent(MixerComponentBase):
    @depends(show_message=None)
    def __init__(
        self, *a, show_message: typing.Optional[typing.Callable[[str], typing.Any]], **k
    ):
        super().__init__(*a, **k)
        assert show_message
        self._show_message = show_message

        send_index_scrollable = SendIndexScrollable(self._send_index_manager)
        self._send_index_scroll = ScrollComponent(
            parent=self, scrollable=send_index_scrollable
        )

    def set_selected_track_arm_button(self, button):
        self._target_strip.arm_button.set_control_element(button)
        self._target_strip.update()

    def set_send_index_encoder(self, encoder):
        self._send_index_scroll.scroll_encoder.set_control_element(encoder)

    def _on_send_index_changed(self):
        self._show_message(f"Controlling Send {self.send_index+ 1}")
        return super()._on_send_index_changed()
