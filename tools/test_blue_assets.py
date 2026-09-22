from pathlib import Path
import json
import numpy as np
from PIL import Image
root=Path(__file__).resolve().parents[1]
path=root/'source/key-highlights.json'
assert path.is_file(),'Independent held-key highlight geometry missing'
meta=json.loads(path.read_text());assert meta['version']==1
keys={x['name']:x['polygon'] for x in meta['keys']}
assert all(n in keys for n in ['ControlLeft','KeyA','ShiftRight','Kp1','Space'])
assert keys['ControlLeft']!=keys['KeyA']
areas=[]
for name in ['mouse-blue-left','mouse-blue-right']:
    im=np.asarray(Image.open(root/'source/input-parts'/(name+'.png')).convert('RGBA'))
    alpha=im[:,:,3];mask=alpha>20
    assert mask.sum()>300,'Empty mouse button highlight'
    assert (im[:,:,2][mask]>im[:,:,0][mask]).mean()>.9,'Mouse highlight is not blue'
    areas.append(mask)
assert not np.logical_and(*areas).any(),'Left/right mouse highlights overlap'
print('PASS independent keyboard map and separated blue mouse button layers')
