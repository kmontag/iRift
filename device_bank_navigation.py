from ableton.v3.control_surface.components import (
    DeviceBankNavigationComponent as DeviceBankNavigationComponentBase,
)


class DeviceBankNavigationComponent(DeviceBankNavigationComponentBase):
    # The scroll direction in the standard component feels reversed
    # compared to other scrollers, i.e. the next bank is selected by
    # turning the encoder CCW. Swap the logic to get a more natural
    # UI.
    def can_scroll_down(self):
        return super().can_scroll_up()

    def can_scroll_up(self):
        return super().can_scroll_down()

    def scroll_down(self):
        return super().scroll_up()

    def scroll_up(self):
        return super().scroll_down()
