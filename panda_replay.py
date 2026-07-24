#!/usr/bin/env python3
"""
panda_replay.py — send a CAN frame with a comma panda (no SocketCAN needed).

Take the address / payload / bus straight from ford_can_debug.py's Events sheet
(the "panda (p.can_send)" column shows the exact call this reproduces).

  WARNING: this sets SAFETY_ALLOUTPUT, which disables the panda's transmit
  filtering so ANY frame can be injected. Use only on a bench or a stationary
  car you own. The panda must be free — stop openpilot/boardd first, or run
  this from a laptop with the panda plugged in.

Install:
    pip install pandacan     # the comma 'panda' python library

Examples:
    # send one frame:
    python panda_replay.py 0x3B3 0000000000000020 --bus 0

    # some ECUs ignore a single frame — resend at 10 Hz for 3 seconds:
    python panda_replay.py 0x3B3 0000000000000020 --bus 0 --rate 10 --duration 3
"""
import argparse
import time

from panda import Panda


def main():
    ap = argparse.ArgumentParser(description="Replay a CAN frame with a comma panda.")
    ap.add_argument("address", help="arbitration id, e.g. 0x3B3 or 947")
    ap.add_argument("data", help="payload hex, e.g. 0000000000000020")
    ap.add_argument("--bus", type=int, default=0, help="panda bus number (default 0)")
    ap.add_argument("--rate", type=float, default=0, help="Hz to resend (0 = send once)")
    ap.add_argument("--duration", type=float, default=0, help="seconds to keep sending")
    args = ap.parse_args()

    addr = int(args.address, 0)                       # accepts 0x.. or decimal
    data = bytes.fromhex(args.data.replace("0x", "").replace(" ", ""))

    p = Panda()
    p.set_safety_mode(Panda.SAFETY_ALLOUTPUT)         # DANGER: arbitrary transmit enabled
    print(f"Sending 0x{addr:X}#{data.hex().upper()} on bus {args.bus} ...")

    if args.rate <= 0:
        p.can_send(addr, data, args.bus)
        print("sent 1 frame")
    else:
        period = 1.0 / args.rate
        end = time.monotonic() + (args.duration or 1e9)
        n = 0
        try:
            while time.monotonic() < end:
                p.can_send(addr, data, args.bus)
                n += 1
                time.sleep(period)
        except KeyboardInterrupt:
            pass
        print(f"sent {n} frames")


if __name__ == "__main__":
    main()
