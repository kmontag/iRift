from functools import partial

from ableton.v3.control_surface.components import (
    ViewControlComponent as ViewControlComponentBase,
)
from ableton.v3.live import track_index


class ViewControlComponent(ViewControlComponentBase):
    def __init__(self, *a, **k):
        super().__init__(*a, **k)

        # Override the track scroller logic to prevent scrolling into
        # returns/master.
        for scrollable in [
            self._scroll_tracks._scrollable,
            self._page_tracks._scrollable,
        ]:
            scrollable.can_scroll_up = partial(self._can_scroll_tracks, -1)
            scrollable.can_scroll_down = partial(self._can_scroll_tracks, 1)

    def _can_scroll_tracks(self, delta):
        assert self._session_ring
        # Only use tracks that are actually available to the session
        # ring.
        tracks = self._session_ring.tracks_to_use()
        current_index = track_index(track_list=tracks)

        # Always allow scrolling if we're outside the list of allowed
        # tracks, e.g. if a send or master has been selected in the UI.
        if current_index is None:
            return True

        new_index = track_index(track_list=tracks) + delta
        return new_index >= 0 and new_index < len(tracks)
