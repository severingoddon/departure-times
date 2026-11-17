# Documentation

## Hardware

### Components

| Part | Notes |
|---|---|
| Raspberry Pi | Runs Raspberry Pi OS with a desktop session. The app uses `vcgencmd` to switch the display. |
| Display | Wide-format screen, set into the front panel |
| 3 × momentary push buttons | Panel-mount, labeled *Zürich HB*, *Escherwyss* and *Bus 32* |
| PIR motion sensor | Mounted in the front panel, bottom right |
| Case | 3 mm plywood, laser-cut, labels engraved |

### Wiring

The pins use the physical numbering of the 40-pin header (`GPIO.BOARD`). All inputs use the internal **pull-down** resistor and trigger on the **rising edge**. Each button therefore connects its pin to **3.3 V** when pressed.

| Function | Physical pin | BCM GPIO | Connection |
|---|---|---|---|
| PIR motion sensor (signal) | 10 | GPIO 15 | Sensor `OUT`. Power and ground according to the sensor's datasheet. |
| Button *Zürich HB* | 16 | GPIO 23 | Button to 3.3 V |
| Button *Bus 32* | 18 | GPIO 24 | Button to 3.3 V |
| Button *Escherwyss* | 22 | GPIO 25 | Button to 3.3 V |

### Case

The case is made from **3 mm plywood**, cut on a CNC laser cutter:
- The front panel has a cutout for the display, holes for the three buttons and the motion sensor, and the engraved button labels.
- The board hangs flat on the wall, and the cables run down in a cable duct.

## Software

### Files

| File | Purpose |
|---|---|
| `gui_button_and_sensor.py` | Main app on the Pi. It creates the fullscreen Tkinter window, sets up GPIO, handles buttons and the motion sensor, and runs the refresh loop. |
| `load_data.py` | `DepartureBoardNew`: fetches the stationboard from search.ch, normalizes the departures and filters them by direction |
| `tkinterGUI_mac.py` | Simplified version of the UI without GPIO, for working on the layout on a Mac |
| `cancellation.svg` | Icon shown instead of the minutes for cancelled departures |

### Refresh loop

`update_departure_board()` runs every **30 seconds**:

1. **Night mode:** between 00:30 and 07:00 the screen is switched off and nothing is loaded.
2. **Presence:** if the PIR sensor reports no motion, the screen is switched off.
3. Otherwise the screen is switched on and the departures for the selected direction are loaded and drawn.

Pressing a button or a motion trigger cancels the scheduled refresh and updates immediately. Buttons are then locked for 2 seconds and the sensor for 30 seconds.

### Data and filtering

`load_data.py` calls the [search.ch stationboard API](https://search.ch/timetable/api/help):

```
GET https://search.ch/fahrplan/api/stationboard.json?stop=<stop>&limit=30&show_delays=1&show_subsequent_stops=1
```

For each departure it computes:
- the **minutes until departure**, i.e. the scheduled time minus now, plus `dep_delay`
- whether it **runs at all**: a delay containing `X` means cancelled
- the **line**, the **direction** (final stop) and the **next stop**

Only departures within the next 99 minutes are kept. Then a direction filter is applied, and at most 9 rows are shown, sorted by time:

| Button | `loadType` | Rule |
|---|---|---|
| Zürich HB | `hb` | next stop contains `Museum` |
| Escherwyss | `esch` | next stop contains `Quellenstrasse` |
| Bus 32 | `bus` | line is `32` or `N12` |

### Display

- **Font:** the board uses a custom dot-matrix font named `Goddonis Font`. It must be installed on the system and is not part of this repository. Without it, Tkinter falls back to a default font.
- **Colors:** orange text (`#fb7500`) on black. Columns are line, direction and minutes.
- **Departing now:** departures with 0 minutes or less show a special glyph of the font instead of a number.
- **Cancelled:** `cancellation.svg` is rendered with CairoSVG and scaled to 80 × 80 px.
- **Cursor:** the mouse cursor is hidden with `unclutter -idle 0`.
- **Window:** fullscreen. `Esc` closes the app.

## Setup on the Raspberry Pi

```bash
sudo apt install python3-tk unclutter libcairo2
pip install -r requirements.txt
```

1. Install the dot-matrix font, e.g. copy it to `~/.fonts/` and run `fc-cache -f`.
2. Start the app from the project folder, because `cancellation.svg` is loaded with a relative path:

   ```bash
   cd ~/departureBoard && python3 gui_button_and_sensor.py
   ```

3. To start it automatically, launch this command from the desktop session's autostart, e.g. a `.desktop` file in `~/.config/autostart/`.

Errors are written to `logfile.txt` in the project folder. The next refresh is scheduled even after an error, so a short network outage doesn't freeze the board.

## Adapting it to another stop

1. Set `stop` in `send_request()` in `load_data.py` to your stop's name as used by search.ch.
2. Adjust the rules in `filter_departure_direction()`. Check the `next_stop` and `line` values first with `python3 load_data.py`.
3. Label the buttons accordingly.

## Development on a Mac

`tkinterGUI_mac.py` shows the board without GPIO, motion sensor or night mode. It always shows the *Escherwyss* direction and is meant for working on layout and font sizes.
