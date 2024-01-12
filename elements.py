import Live
import typing

# currently no v3 equivalent
from ableton.v2.control_surface.elements import (
    MultiElement,
)
from ableton.v3.base import depends
from ableton.v3.control_surface import (
    DEFAULT_CONTINUOUS_PARAMETER_SENSITIVITY,
    MIDI_NOTE_TYPE,
    ElementsBase,
)
from ableton.v3.control_surface.elements import ButtonElement, ButtonMatrixElement

from .configuration import Configuration

NUM_TRACKS = 8

# Regardless of the global MIDI channel, transport buttons always fire
# on channel 1.
TRANSPORT_MIDI_CHANNEL = 0

## CC IDs for transport buttons.

# Sent when the stop/prev-track button is pressed while the record
# and/or play LEDs are on.
STOP_ID = 117
# Sent when the stop/prev-track button is pressed while the record and
# play LEDs are both off.
RESET_ID = 111
# Sent when the play button is pressed, except if the record LED is
# on.
PLAY_ID = 118
# Sent when the record LED is turned on. Specifically:
# - record is pressed while all LEDs are off, or
# - record is pressed while the play LED is on and the record LED is off.
RECORD_ID = 119
# Sent when the record LED is turned off while the play LED is turned
# on, i.e. toggled off.
RECORD_DISARM_ID = 116
# Sent whenever the fast forward button (i.e. alt + stop) is pressed.
FAST_FORWARD_ID = 114

## CC IDs for encoders.

# Clicky-knob data encoder.
DATA_ENCODER_ID = 22
# Sent when the data encoder is pressed.
DATA_BUTTON_ID = 23
# Numbered encoders.
ENCODER_IDS = (12, 13, 14, 15, 16, 17, 18, 19)

## Note IDs for pads.
PAD_IDS = (36, 38, 40, 42, 46, 43, 47, 49)
##


class Elements(ElementsBase):
    @depends(configuration=None)
    def __init__(self, *a, configuration: typing.Optional[Configuration] = None, **k):
        assert configuration

        # The global MIDI channel will be used as a default for
        # buttons and encoders.
        super().__init__(configuration.global_midi_channel, *a, **k)

        self._configuration = configuration

        self._add_transport()
        self._add_encoders()

        # For the type checker.
        self.data_button: ButtonElement

        self._add_pads()

    def _add_transport(self):
        for name, identifier in {
            "stop": STOP_ID,
            "reset": RESET_ID,
            "play": PLAY_ID,
            "record": RECORD_ID,
            "record_disarm": RECORD_DISARM_ID,
            "fast_forward": FAST_FORWARD_ID,
        }.items():
            self.add_button(
                identifier,
                f"{name}_button",
                channel=TRANSPORT_MIDI_CHANNEL,
                is_momentary=False,
            )

    def _add_encoders(self):
        self.add_encoder(
            DATA_ENCODER_ID,
            "data_encoder",
            map_mode=Live.MidiMap.MapMode.relative_smooth_two_compliment,
        )
        self.add_button(DATA_BUTTON_ID, "data_button")
        self.add_encoder_matrix(
            [ENCODER_IDS],
            "encoders",
            map_mode=Live.MidiMap.MapMode.relative_smooth_two_compliment,
            mapping_sensitivity=(
                DEFAULT_CONTINUOUS_PARAMETER_SENSITIVITY
                * self._configuration.continuous_parameter_sensitivity
            ),
        )

        # Create a single-button matrix so we can use the data button
        # in places that require a list, e.g. scene launch buttons.
        self.add_element(
            "data_button_matrix", ButtonMatrixElement, rows=[[self.data_button]]
        )

    def _add_pads(self):
        pad_behaviors = [
            "arm",
            "clip_launch",
            "data_encoder_mode",
            "drum_group",
            "mute",
            "solo",
            "stop_track_clip",
            "track_select",
            "transport",
        ]

        def add_behavior_matrix(behavior_name):
            base_name = f"{behavior_name}_buttons"
            channel = getattr(self._configuration, f"{behavior_name}_midi_channel")
            self.add_button_matrix(
                [PAD_IDS], base_name, channels=channel, msg_type=MIDI_NOTE_TYPE
            )
            return getattr(self, f"{base_name}_raw")

        # Create named 8x1 matrices for each behavior.
        button_rows = [add_behavior_matrix(behavior) for behavior in pad_behaviors]

        # Create combo buttons to represent each pad being pressed in any mode.
        for index in range(NUM_TRACKS):
            buttons = [button_row[index] for button_row in button_rows]
            self.add_element(f"pad_{index}_button", MultiElement, *buttons)
