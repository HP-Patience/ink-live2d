"""Run directly with Python 3.11+."""
import hashlib
import importlib.util
from pathlib import Path
from tempfile import TemporaryDirectory

spec = importlib.util.spec_from_file_location("join_release", Path(__file__).resolve().parents[1] / "tools/join_release.py")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
with TemporaryDirectory() as directory:
    folder = Path(directory)
    name = "InkPortrait-Production-v6.zip"
    content = b"complete archive"
    files = {f"{name}.{n:03d}": bytes([n]) for n in range(1, 7)}
    content = b"".join(files.values())
    for filename, data in files.items():
        (folder / filename).write_bytes(data)
    files[name] = content
    (folder / "SHA256SUMS.txt").write_text("".join(f"{hashlib.sha256(data).hexdigest()}  {filename}\n" for filename, data in files.items()), encoding="utf-8")
    module.merge(folder)
    assert (folder / name).read_bytes() == content
    (folder / f"{name}.003").write_bytes(b"corrupt")
    try:
        module.merge(folder)
        raise AssertionError("Corruption was accepted")
    except ValueError:
        pass
    assert (folder / name).read_bytes() == content
    (folder / f"{name}.003").unlink()
    try:
        module.merge(folder)
        raise AssertionError("Missing part was accepted")
    except FileNotFoundError:
        pass
    assert (folder / name).read_bytes() == content
print("PASS: merge, corruption and missing-part protection")
