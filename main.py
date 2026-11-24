#!/usr/bin/env python3
"""make.fun entry: Sum up 23 November 2026's world news in one image.

The front page lives next to this program as entry.png. Running the
program validates it (PNG magic, 1024x1024 cap, 1 MiB cap) and copies
it byte for byte to /output/entry.png. No network, no randomness, no
arguments: two runs always write the same bytes.
"""
import hashlib
import struct
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SOURCE = HERE / "entry.png"
DEST = Path("/output/entry.png")
LIMIT_BYTES = 1_048_576
LIMIT_PX = 1024


def png_dimensions(data):
    """Return (width, height) from the IHDR chunk of a PNG byte string."""
    if data[:8] != b"\x89PNG\r\n\x1a\n":
        raise ValueError("not a PNG file")
    width, height = struct.unpack(">II", data[16:24])
    return width, height


def sha256_hex(data):
    return hashlib.sha256(data).hexdigest()


def publish():
    data = SOURCE.read_bytes()
    width, height = png_dimensions(data)
    if width > LIMIT_PX or height > LIMIT_PX:
        print(f"entry.png is {width}x{height}, over the {LIMIT_PX}x{LIMIT_PX} cap",
              file=sys.stderr)
        return 1
    if len(data) > LIMIT_BYTES:
        print(f"entry.png is {len(data)} bytes, over the 1 MiB cap",
              file=sys.stderr)
        return 1
    DEST.parent.mkdir(parents=True, exist_ok=True)
    DEST.write_bytes(data)
    written = DEST.read_bytes()
    if written != data:
        print("verification failed: /output/entry.png differs from entry.png",
              file=sys.stderr)
        return 1
    print(f"wrote {DEST} ({len(data)} bytes, sha256 {sha256_hex(data)[:16]}, "
          f"verified identical)")
    return 0


if __name__ == "__main__":
    sys.exit(publish())
