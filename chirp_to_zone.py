#!/usr/bin/env python3
"""
Convert a CHIRP CSV export to the ‘Zone/Channel’ CSV required by many
commercial radios.

Tone handling:
  Tone  → encode only
  TSQL  → encode + decode
  else  → both Off

Duplex handling:
  + / - → normal split using Offset
  off   → RX-only (TX Prohibit = On, TX freq = RX freq)
  blank → simplex
"""

import argparse
import csv
import pathlib

# ──────────────────────────────────────────────────────────── helpers ──
def tx_freq(rx: float, duplex: str, offset: float) -> float:
    """Return TX frequency derived from CHIRP duplex/offset rules."""
    d = (duplex or "").strip().lower()
    if d == "+":
        return rx + offset
    if d == "-":
        return rx - offset
    # 'off' or blank → same as RX
    return rx

def tx_prohibit(duplex: str) -> str:
    """Turn TX Prohibit On when CHIRP duplex == 'off' (case-insensitive)."""
    return "On" if (duplex or "").strip().lower() == "off" else "Off"

def power_level(chirp_power: str) -> str:
    try:
        watts = float(chirp_power.rstrip("Ww"))
        return "High" if watts >= 5 else "Low"
    except (ValueError, TypeError):
        return "High"

def tone_or_off(val: str) -> str:
    return val.strip() if val and val.strip() else "Off"

def split_tones(row: dict) -> tuple[str, str]:
    mode = (row["Tone"] or "").strip().upper()
    if mode == "TSQL":
        decode = tone_or_off(row["rToneFreq"])
        encode = tone_or_off(row["cToneFreq"])
    elif mode == "TONE":
        decode = "Off"
        encode = tone_or_off(row["cToneFreq"] or row["rToneFreq"])
    else:               # blank, DTCS, etc.
        decode = encode = "Off"
    return decode, encode

# ───────────────────────────────────────────────────────── conversion ──
def convert(in_path: pathlib.Path, out_path: pathlib.Path, zone: str) -> None:
    with in_path.open(newline="", encoding="utf-8-sig") as f_in, \
         out_path.open("w", newline="", encoding="utf-8") as f_out:

        chirp_reader = csv.DictReader(f_in)
        writer = csv.writer(f_out)

        writer.writerow([
            "Zone", "Channel Name", "Bandwidth", "Power",
            "RX Freq", "TX Freq", "CTCSS Decode", "CTCSS Encode", "TX Prohibit"
        ])

        for row in chirp_reader:
            rx = float(row["Frequency"])
            dup = row["Duplex"]
            tx = tx_freq(rx, dup, float(row["Offset"] or 0))
            decode, encode = split_tones(row)

            if encode != decode and decode != "Off":
                print(f"WARNING: {row['Name']} has possibly confused tones {encode=} {decode=}.")

            writer.writerow([
                zone,                       # Zone
                row["Name"].strip(),        # Channel Name
                "25K",                      # Bandwidth (fixed)
                power_level(row["Power"]),  # Power
                f"{rx:g}",                  # RX Freq
                f"{tx:g}",                  # TX Freq
                decode,                     # CTCSS Decode
                encode,                     # CTCSS Encode
                tx_prohibit(dup)            # TX Prohibit
            ])

# ──────────────────────────────────────────────────────────── main ──
if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="Convert CHIRP CSV to Zone/Channel CSV")
    ap.add_argument("--in",  required=True, dest="inp",  help="Input CHIRP CSV file")
    ap.add_argument("--out", required=True, dest="out",  help="Output CSV file")
    ap.add_argument("--zone", default="Analog-PHL",      help="Zone name for every row")
    args = ap.parse_args()

    convert(pathlib.Path(args.inp), pathlib.Path(args.out), args.zone)
