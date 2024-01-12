import typing

from ableton.v3.base import depends
from ableton.v3.control_surface import ControlSurface
from ableton.v3.control_surface.mode import CallFunctionMode, Mode

from .configuration import Configuration
from .elements import NUM_TRACKS


@depends(configuration=None, show_message=None)
def create_mappings(
    control_surface: ControlSurface,
    configuration: typing.Optional[Configuration] = None,
    show_message: typing.Optional[typing.Callable[[str], typing.Any]] = None,
):
    assert configuration
    assert show_message

    mappings = {}

    # Build a mode that just selects another mode.
    def set_selected_mode_mode(component_name: str, selected_mode: str):
        def on_enter():
            control_surface.component_map[component_name].selected_mode = selected_mode

        return CallFunctionMode(on_enter_fn=on_enter)

    def show_message_mode(message: str):
        def on_enter():
            show_message(message)

        return CallFunctionMode(on_enter_fn=on_enter)

    # Get modes assigning buttons to select the data encoder mode. The
    # parameter is a list of element names for the 8 pads (in order).
    def data_encoder_pad_modes(buttons: typing.List[str]):
        return [
            dict(
                component="Data_Encoder_Modes",
                enable_selected_track_button=buttons[0],
                enable_session_ring_tracks_button=buttons[1],
                enable_session_ring_scenes_button=buttons[2],
                enable_send_index_button=buttons[3],
                enable_device_button=buttons[4],
                enable_device_bank_button=buttons[5],
                enable_drum_group_button=buttons[6],
            ),
            dict(
                component="Pad_Modes",
                default_button=buttons[7],
            ),
        ]

    # Modes for pad functions.
    default_pad_modes = [
        dict(
            component="Drum_Group",
            matrix="drum_group_buttons",
        ),
        dict(
            component="Mixer",
            mute_buttons="mute_buttons",
            solo_buttons="solo_buttons",
            arm_buttons="arm_buttons",
            track_select_buttons="track_select_buttons",
        ),
        dict(
            component="Recording",
            arrangement_record_button="transport_buttons_raw[2]",
            session_record_button="transport_buttons_raw[3]",
            new_button="transport_buttons_raw[6]",
        ),
        dict(
            component="Session",
            clip_launch_buttons="clip_launch_buttons",
            stop_all_clips_button="transport_buttons_raw[7]",
            stop_track_clip_buttons="stop_track_clip_buttons",
        ),
        dict(
            component="Transport",
            play_button="transport_buttons_raw[0]",
            stop_button="transport_buttons_raw[1]",
            metronome_button="transport_buttons_raw[4]",
            tap_tempo_button="transport_buttons_raw[5]",
        ),
        *data_encoder_pad_modes(
            [f"data_encoder_mode_buttons_raw[{i}]" for i in range(NUM_TRACKS)]
        ),
    ]
    mappings["Pad_Modes"] = dict(
        data_encoder_mode_button="fast_forward_button",
        # Main mode, all normal functions enabled.
        default=dict(modes=default_pad_modes),
        # Momentary encoder function selection mode.
        data_encoder_mode=dict(
            modes=data_encoder_pad_modes([f"pad_{i}_button" for i in range(NUM_TRACKS)])
        ),
    )

    data_encoder_modes: typing.Dict[
        str, typing.List[typing.Union[typing.Dict, Mode]]
    ] = dict(
        initial=[
            set_selected_mode_mode(
                "Data_Encoder_Modes",
                configuration.initial_data_encoder_mode,
            )
        ],
        device=[
            dict(component="Device", device_lock_button="data_button"),
            dict(component="Device_Navigation", scroll_encoder="data_encoder"),
        ],
        device_bank=[
            dict(
                component="Device",
                device_lock_button="data_button",
                bank_scroll_encoder="data_encoder",
            ),
        ],
        drum_group=[
            dict(component="Drum_Group", scroll_encoder="data_encoder"),
        ],
        selected_track=[
            dict(component="Mixer", selected_track_arm_button="data_button"),
            dict(component="View_Control", track_encoder="data_encoder"),
        ],
        send_index=[
            dict(component="Mixer", send_index_encoder="data_encoder"),
        ],
        session_ring_scenes=[
            dict(component="Session", scene_launch_buttons="data_button_matrix"),
            dict(component="Session_Navigation", vertical_encoder="data_encoder"),
        ],
        session_ring_tracks=[
            dict(component="Session_Navigation", horizontal_encoder="data_encoder"),
        ],
    )
    data_encoder_mode_names = list(data_encoder_modes.keys())
    data_encoder_mode_names.remove("initial")
    for mode_name in data_encoder_mode_names:
        # Add transient modes with steps that should always fire when
        # selecting a data encoder mode via a button (even if the mode
        # is already active).
        data_encoder_modes[f"enable_{mode_name}"] = [
            show_message_mode(
                f"DATA controlling {mode_name.replace('_', ' ').title()}"
            ),
            set_selected_mode_mode("Data_Encoder_Modes", mode_name),
            # Always make sure the pads return to default mode after
            # selecting a data encoder mode. This will be a no-op when
            # the selection is performed from the dedicated user
            # preset.
            set_selected_mode_mode("Pad_Modes", "default"),
        ]

    data_encoder_modes_mapping: typing.Dict[str, typing.Union[str, typing.Dict]] = {
        name: dict(modes=modes) for name, modes in data_encoder_modes.items()
    }
    mappings["Data_Encoder_Modes"] = data_encoder_modes_mapping

    # Modes to switch main encoder behavior.
    mappings["Encoder_Modes"] = dict(
        device_parameters_button="stop_button",
        volume_button="play_button",
        sends_button="record_button",
        device_parameters=dict(
            modes=[dict(component="Device", parameter_controls="encoders")]
        ),
        volume=dict(
            modes=[
                dict(component="Mixer", volume_controls="encoders"),
                dict(component="Encoder_Modes", pan_button="record_button"),
            ]
        ),
        pan=dict(modes=[dict(component="Mixer", pan_controls="encoders")]),
        sends=dict(modes=[dict(component="Mixer", send_controls="encoders")]),
        # The reset button is just the stop button when no other
        # parameters are active. In most cases this is a no-op, since
        # the device parameters mode should already be active whenever
        # we see this button, but we keep it here to deal with
        # out-of-sync state if e.g. the controller is reconnected.
        reset=set_selected_mode_mode("Encoder_Modes", "device_parameters"),
        reset_button="reset_button",
        # The record-disarm message only shows up when toggling record
        # while play is active, so it always triggers volume mode.
        record_disarm=set_selected_mode_mode("Encoder_Modes", "volume"),
        record_disarm_button="record_disarm_button",
    )

    return mappings
