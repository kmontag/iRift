# This file defines the configuration schema and defaults for the
# control surface.
#
# To customize these settings, create a file called `user.py` in this
# directory, and export a custom `Configuration` instance named
# `configuration`, for example:
#
#   # user.py
#   from .configuration import Configuration
#
#   configuration = Configuration(
#       initial_data_encoder_mode = "scene",
#       # ...
#   )
import logging
import typing

logger = logging.getLogger(__name__)


class Configuration(typing.NamedTuple):
    # All MIDI channels are 0-indexed, i.e. between 0 and 15.
    global_midi_channel: int = 0

    # MIDI channels by pad function.
    transport_midi_channel: int = 1
    drum_group_midi_channel: int = 2
    clip_launch_midi_channel: int = 3
    track_select_midi_channel: int = 4
    mute_midi_channel: int = 5
    solo_midi_channel: int = 6
    arm_midi_channel: int = 7
    stop_track_clip_midi_channel: int = 8
    data_encoder_mode_midi_channel: int = 9

    # Encoder sensitivity factor. A larger value makes the encoders
    # more sensitive.
    continuous_parameter_sensitivity: float = 3.0

    # Valid values: selected_track, session_ring_scenes,
    # session_ring_tracks, send_index, device, device_bank,
    # drum_group.
    initial_data_encoder_mode: str = "selected_track"

    # MIDI PC message to be sent when the controller is connected.
    # For example, set this to 6 to select the U01 preset on startup.
    initial_program: typing.Optional[int] = None


def get_configuration() -> Configuration:
    # Load a local configuration if possible, or fall back to the default.
    local_configuration: typing.Optional[Configuration] = None
    try:
        from .user import (  # type: ignore
            configuration as local_configuration,  # type: ignore
        )

        logger.info("loaded local configuration")

    except (ImportError, ModuleNotFoundError):
        logger.info("loaded default configuration")

    return local_configuration or Configuration()
