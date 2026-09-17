"""Download the pinned upstream PSD2Live portable tool, with SHA-256 verification."""
from pathlib import Path
import hashlib, json, urllib.request, zipfile
ROOT=Path(__file__).resolve().parents[1]
config=json.loads((ROOT/'tools/toolchain.json').read_text())['psd2live']
dest=ROOT/'workspace/tools'; dest.mkdir(parents=True,exist_ok=True)
archive=dest/'PSD2Live-0.7.1-portable.zip'
if not archive.exists():
    print('Downloading the upstream PSD2Live release (about 77 MB)...',flush=True)
    urllib.request.urlretrieve(config['archive'],archive)
if hashlib.sha256(archive.read_bytes()).hexdigest()!=config['sha256']:
    raise SystemExit('Archive checksum mismatch; remove the bad archive and retry.')
with zipfile.ZipFile(archive) as z:
    for entry in z.infolist():
        target=(dest/entry.filename).resolve()
        if not target.is_relative_to(dest.resolve()):
            raise ValueError('Unsafe archive path: '+entry.filename)
    z.extractall(dest)
print('Verified PSD2Live app:',dest/'PSD2Live/app')
