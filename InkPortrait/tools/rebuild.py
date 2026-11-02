"""Reproduce v6 from the committed inference layers, without a GPU or new inference."""
from pathlib import Path
import argparse, hashlib, shutil, subprocess, sys
ROOT=Path(__file__).resolve().parents[1]; W=ROOT/'workspace'
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--psd2live-app',type=Path,default=W/'tools/PSD2Live/app')
p.add_argument('--source-only',action='store_true')
a=p.parse_args()
if not a.source_only and not list(a.psd2live_app.glob('*.jar')):
    p.error('PSD2Live JARs not found. Run tools/setup_tools.py or pass --psd2live-app.')
shutil.copytree(ROOT/'source/auto-layered/layers',W/'layered/InkPortrait',dirs_exist_ok=True)
for script in ['repair_portrait.py','fix_portrait_layers.py','fix_portrait_v3.py','fix_portrait_v6.py']:
    subprocess.run([sys.executable,str(ROOT/'tools'/script)],cwd=ROOT,check=True)
# PNG byte encoding may vary across Pillow versions; compare decoded source pixels.
from PIL import Image
import numpy as np
for source in (ROOT/'source/layers').glob('*.png'):
    assert np.array_equal(np.array(Image.open(source)),np.array(Image.open(W/'repaired-v6'/source.name))),source.name
print('All 20 final layer images reproduce exactly at the pixel level.',flush=True)
if not a.source_only:
    with (W/'rebuild.log').open('w',encoding='utf-8') as log:
        subprocess.run(['java','-Dfile.encoding=UTF-8','--class-path',str(a.psd2live_app.resolve()/'*'),str(ROOT/'tools/BuildPortrait.java'),str(W/'repaired-v6/InkPortrait.psd'),str(W/'repaired-model-v6')],cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,check=True)
    model=W/'repaired-model-v6/InkPortrait.moc3'
    assert model.read_bytes()[:4]==b'MOC3'
    print('Model:',model)
    print('Export log:',W/'rebuild.log')
