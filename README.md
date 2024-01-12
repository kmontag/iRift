# iRift

This is an Ableton Live 11 control surface script for [iRig Keys
I/O](https://www.ikmultimedia.com/products/irigkeysio/) keyboards. It
offers a lot more functionality than Live's built-in iRig script.

It's tested on the 49-key model, but should work on the 25-key model
as well - testers welcome.

## Installation

- Download or clone this repository and place it under `Remote
Scripts` in your Live User Library. (If you don't know your User
  Library location, you can find it under `Library` in Live's settings
  dialog.)
- Start or restart Live.
- In the Live settings dialog under `Link/Tempo/MIDI`, choose
  `iRift` as one of your control surfaces.
- Make sure your iRig device is plugged in, and select the
  appropriate ports for the control surface input/output.
- In the `MIDI Ports` section, make sure the iRig's input/output
  have `Track` and `Remote` checked.

## Hardware setup

Load the F02 factory preset (normally used for Logic Pro X/GarageBand
integration) onto the iRig. The smooth encoders should now be mapped
to Live's device parameters, and the DATA encoder should scroll the
selected track.

To get functionality from the pads, start from F02 and change the pad
channel (`EDIT` -> `PRE` -> `PAD` -> `CH`) to something from the table
below. You can save your changes to a user preset to allow for quick
recall. The available pad behaviors are:

<a id='pad-channels'></a>

| Pad channel                 | Pad behavior                                                                                 |
| --------------------------- | -------------------------------------------------------------------------------------------- |
| GLO (unmodified F02 preset) | Notes/no special functionality                                                               |
| 2                           | [Transport](#transport-pads)                                                                 |
| 3                           | Mute tracks                                                                                  |
| 4                           | Solo tracks                                                                                  |
| 5                           | Arm tracks                                                                                   |
| 6                           | Select tracks                                                                                |
| 7                           | Stop track clips                                                                             |
| 8                           | Drum pads                                                                                    |
| 9                           | Launch clips                                                                                 |
| 10                          | Set DATA encoder behavior ([also acessible](#data-encoder) via :fast_forward: on the I/O 49) |

The most natural setup is to save presets for pad channels 2-9 as
U01-U08, respectively - then you can quickly change pad behavior by
pressing `PRESET` followed by the corresponding pad. But you can of
course omit any of these presets or organize them differently,
depending on your workflow.

Note: if your global MIDI channel is set to something other than 1,
you'll need to specify this in your [configuration](#configuration),
and (if necessary) specify an alternate channel for the conflicting
pad behavior.

## Usage

### DATA encoder

At startup, the data encoder scrolls the selected track. The behavior
can be changed by loading a preset with pad channel 10, and pressing a
pad:

| Pad         | DATA encoder function          | DATA encoder push function |
| ----------- | ------------------------------ | -------------------------- |
| 1 (default) | Selected track                 | Arm selected track         |
| 2           | Track session ring ("red box") |                            |
| 3           | Scene session ring             | Play highlighted scene     |
| 4           | Controlled send                |                            |
| 5           | Selected device                | Lock to selected device    |
| 6           | Device bank                    | Lock to selected device    |
| 7           | Drum rack position             |                            |
| 8           | (unchanged)                    |                            |

If you have an I/O 49, you can also quickly set the DATA encoder
behavior by pressing :fast_forward: (i.e. `ALT` + `STOP`) followed by
one of the pads.

### Pads

Navigate through your configured [user presets](#pad-channels) to
change the pad function.

<h4 id='transport-pads'>Transport control via pads</h3>

When the pad channel is set to 2, the pads are mapped to transport
controls:

| Pad | Function                               |
| --- | -------------------------------------- |
| 1   | Play                                   |
| 2   | Stop                                   |
| 3   | Arrangement Record                     |
| 4   | Session Record                         |
| 5   | Metronome                              |
| 6   | Tap Tempo                              |
| 7   | Select new clip slot for current track |
| 8   | Stop All Clips                         |

### Smooth encoders and physical transport buttons

By default, the smooth encoders control the parameters of the current
device. You can change the behavior using the physical transport
buttons on the iRig.

The iRig's transport buttons have hardcoded LED/MIDI behavior and
can't receive feedback from Live, so they aren't a good fit for
controlling Live's transport (as they can easily get out of
sync). Instead, the LEDs indicate the current encoder behavior:

| Play LED :green_circle: | Record LED :red_circle: | Encoder 1-8 function                                                 |
| ----------------------- | ----------------------- | -------------------------------------------------------------------- |
| off                     | off                     | Device parameters                                                    |
| ON                      | off                     | Track volume                                                         |
| ON                      | ON                      | Track panning                                                        |
| off                     | ON                      | Track sends (DATA encoder can be used to select the controlled send) |

You'll probably want to mess around with the transport buttons a bit,
to get a sense for how to navigate through these states with the
onboard behavior:

- `STOP` always turns both LEDs off.
- `PLAY` turns on the Play LED **unless** the Record LED is already
  turned on, in which case it does nothing.
- `RECORD` turns on the Record LED **unless** the Play LED is
  already turned on, in which case it toggles the Record LED
  on/off state.

## Configuration

You can configure some aspects of the control surface behavior by
creating a file called `configuration_local.py` in this directory, and
adding something like the following:

```python
# configuration_local.py
from .configuration import Configuration

configuration = Configuration(
    initial_data_encoder_mode="session_ring_scenes",
    # ...
)
```

See [configuration.py](configuration.py) for the full list of options.
