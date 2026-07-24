# RZCA — Ford CAN Debug & Replay Tool

`ford_can_debug.py` decodes Ford CAN traffic with [opendbc](https://github.com/commaai/opendbc),
saves all raw frames, highlights what changed, and exports human-readable **events**
(door open, seatbelt, gear, reverse, locks, windows...) to a separate spreadsheet
with ready-to-use `cansend` commands so you can resend them to the car.

## Inputs

- **CSV file** — a previously captured dump (SavvyCAN / candump-export / generic layouts).
- **Live port(s)** — read straight off one or more CAN interfaces in real time
  (SocketCAN, Linux). Multiple interfaces are read together via a single `select()` loop.

## Output workbook (`ford_capture.xlsx`)

| Sheet | Contents |
|-------|----------|
| **Raw_Log** | Every frame: time / bus / ID / bytes / decoded signals. Changed bytes highlighted **yellow**; event frames highlighted **orange**. |
| **Changes** | Only the frames where a payload byte changed vs the prior same-ID frame (the reverse-engineering view). |
| **Events**  | Discrete state transitions (e.g. *Driver door OPENED*, *Seatbelt BUCKLED*, *Gear -> R*), each with the exact `cansend` line to replay it. |

A plain-text raw dump (`ford_capture.raw.txt`) with all frames is written alongside.

## Install

```bash
pip install opendbc openpyxl
sudo apt install can-utils   # provides cansend / candump
```

## Bring a live interface up (example, 500 kbit/s HS-CAN)

```bash
sudo ip link set can0 up type can bitrate 500000
sudo ip link set can1 up type can bitrate 500000
```

## Usage

```bash
# From a CSV dump:
python ford_can_debug.py --csv dump.csv

# Live from one port until Ctrl-C:
python ford_can_debug.py --live can0

# Live from two ports at once, for 30 seconds:
python ford_can_debug.py --live can0 can1 --duration 30

# Live, stop after 5000 frames, custom output:
python ford_can_debug.py --live can0 --max-frames 5000 --out door_test.xlsx
```

In live mode, events also print to the console as they happen, e.g.:

```
[  12.34s] can0  Driver door: CLOSED (0) -> OPEN (1)   ->  cansend can0 3B0#0100000000000000
```

## Resending an event

Open the workbook → **Events** sheet → copy the `cansend` cell for the row you want:

```bash
cansend can0 3B0#0100000000000000
```

## Notes / options

- `--dbc <name>` — defaults to `ford_lincoln_base_pt`; pass a different opendbc DBC if needed.
- Decoding is **always on**. One opendbc parser is built per captured bus so multi-bus
  captures decode correctly.
- Ford body messages (doors, belts, locks) are usually **not** on the powertrain bus —
  make sure you capture / point `--bus` at the right one, or the Events sheet may be empty.

## Safety

Only inject on a bus you own or are authorized to test, ideally with the vehicle
stationary. Replayed body frames can actuate locks and latches — don't test on a
moving car.
