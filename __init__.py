from __future__ import annotations

import logging
import typing

from ableton.v3.base import const, depends, inject
from ableton.v3.control_surface import (
    DEFAULT_CONTINUOUS_PARAMETER_SENSITIVITY,
    ControlSurface,
    ControlSurfaceSpecification,
)
from ableton.v3.control_surface.capabilities import (
    CONTROLLER_ID_KEY,
    NOTES_CC,
    PORTS_KEY,
    REMOTE,
    SCRIPT,
    controller_id,
    inport,
    outport,
)
from ableton.v3.control_surface.components import DeviceComponent

from .configuration import get_configuration
from .device_bank_navigation import DeviceBankNavigationComponent
from .elements import NUM_TRACKS, Elements
from .mappings import create_mappings
from .mixer import MixerComponent
from .view_control import ViewControlComponent

logger = logging.getLogger(__name__)

_configuration = get_configuration()


def get_capabilities():
    return {
        CONTROLLER_ID_KEY: controller_id(
            vendor_id=0x1963,
            # 49-key and 25-key versions, respectively.
            product_ids=(0x002D, 0x002E),
            model_name=("iRig Keys IO 49", "iRig Keys IO 25"),
        ),
        PORTS_KEY: [
            inport(props=[NOTES_CC]),
            inport(props=[NOTES_CC, SCRIPT, REMOTE]),
            outport(props=[SCRIPT]),
        ],
    }


def create_instance(c_instance):
    return iRift(c_instance=c_instance)


@depends(specification=None)
def _create_device_component(
    specification: typing.Optional[typing.Type[Specification]], **k
):
    assert specification
    # The device component gets some special initialization in the
    # default component map, which we want to preserve. We don't have
    # any easy access to the default factory, so we need to replicate
    # it from scratch scratch in order to add our own customizations.
    return DeviceComponent(
        # Default arguments.
        bank_definitions=(specification.parameter_bank_definitions),
        bank_size=(specification.parameter_bank_size),
        continuous_parameter_sensitivity=(
            specification.continuous_parameter_sensitivity
        ),
        quantized_parameter_sensitivity=(specification.quantized_parameter_sensitivity),
        # Customizations.
        bank_navigation_component_type=DeviceBankNavigationComponent,
        **k,
    )


class Specification(ControlSurfaceSpecification):
    identity_response_id_bytes = (0x00, 0x21, 0x1A)
    elements_type = Elements
    num_tracks = NUM_TRACKS
    num_scenes = 1

    include_master = False
    include_returns = False

    hello_messages = (
        # 0xC0 is the base status byte for PC messages.
        [(0xC0 + _configuration.global_midi_channel, _configuration.initial_program)]
        if _configuration.initial_program is not None
        else None
    )

    continuous_parameter_sensitivity = (
        DEFAULT_CONTINUOUS_PARAMETER_SENSITIVITY
        * _configuration.continuous_parameter_sensitivity
    )

    create_mappings_function = create_mappings
    component_map = {
        "Device": _create_device_component,
        "Mixer": MixerComponent,
        "View_Control": ViewControlComponent,
    }


class iRift(ControlSurface):
    def __init__(self, *a, **k):
        super().__init__(*a, specification=Specification, **k)

    def setup(self):
        super().setup()
        logger.info(f"{self.__class__.__name__} setup complete")

    def on_identified(self, response_bytes):
        super().on_identified(response_bytes)
        logger.info("identified iRig Keys I/O device")

    # Dependencies to be injected throughout the application.
    #
    # We need the `Any` return type because otherwise the type checker
    # infers `None` as the only valid return type.
    def _get_additional_dependencies(self) -> typing.Any:
        deps: typing.Dict[str, typing.Any] = (
            super()._get_additional_dependencies() or {}
        )

        deps["configuration"] = const(_configuration)
        deps["specification"] = const(self.specification)

        return deps

    @staticmethod
    def _create_elements(specification: ControlSurfaceSpecification):
        # Element creation happens before the main dependency injector
        # is built, so we need to explicitly inject any necessary
        # dependencies for this stage.
        with inject(configuration=const(_configuration)).everywhere():
            return super(iRift, iRift)._create_elements(specification)

    def _do_send_midi(self, midi_event_bytes):
        # The iRig only handles program changes (0xC*) messages
        # (0xF*). Everything else is ignored by the controller, except
        # that it sometimes seems to freeze when flooded with
        # messages - so we suppress all non-sysex/PC messages.
        #
        # This unfortunately means we can't control the transport LEDs
        # or pad colors - see
        # https://cgi.ikmultimedia.com/ikforum/viewtopic.php?f=19&t=19716&p=85216&hilit=io+led+control#p85216.
        status_byte = midi_event_bytes[0]
        if status_byte < 0xC0 or 0xD0 <= status_byte < 0xF0:
            return False

        return super()._do_send_midi(midi_event_bytes)
