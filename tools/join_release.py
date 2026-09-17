"""Verify and merge the six release parts. Usage: python join_release.py [download_dir]"""
from pathlib import Path
import hashlib
import os
import shutil
import sys


def merge(folder):
    folder = Path(folder)
    name = "InkPortrait-Production-v6.zip"
    checks = dict(line.split("  ", 1)[::-1] for line in
                  (folder / "SHA256SUMS.txt").read_text(encoding="utf-8").splitlines() if line.strip())
    parts = [folder / f"{name}.{n:03d}" for n in range(1, 7)]
    for part in parts:
        with part.open("rb") as stream:
            if hashlib.file_digest(stream, "sha256").hexdigest() != checks[part.name]:
                raise ValueError(f"Checksum mismatch: {part.name}")
    target = folder / name
    temp = folder / (name + ".merging")
    try:
        with temp.open("wb") as output:
            for part in parts:
                with part.open("rb") as source:
                    shutil.copyfileobj(source, output)
        with temp.open("rb") as stream:
            if hashlib.file_digest(stream, "sha256").hexdigest() != checks[name]:
                raise ValueError("Merged archive checksum mismatch")
        os.replace(temp, target)
    finally:
        temp.unlink(missing_ok=True)
    print(f"Verified: {target}")


if __name__ == "__main__":
    merge(sys.argv[1] if len(sys.argv) > 1 else Path(__file__).resolve().parent)
