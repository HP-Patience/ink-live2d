"""Trim only the exposed straight upper-right neck edge; all other V3 pixels are retained."""
from pathlib import Path
import json
import numpy as np
from PIL import Image
from psd_tools import PSDImage
from psd_tools.api.layers import PixelLayer
W=Path(__file__).resolve().parents[1]/'workspace';O=W/'repaired-v5';O.mkdir(exist_ok=True)
names=[x['name'] for x in json.loads((W/'repaired/layers.json').read_text())]
psd=PSDImage.new('RGBA',(1280,1440))
for name in names:
 im=Image.open(W/'repaired-v3'/f'{name}.png').convert('RGBA')
 if name=='neck':
  a=np.array(im);before=a.copy();y,x=np.mgrid[:1440,:1280];y=y-160
  # ponytail: portrait-specific edge trim, not a general neck segmentation algorithm.
  edge=789+(y-620)*(19/220)
  keep=np.clip(edge-x,0,1);keep[y>=840]=1
  a[:,:,3]=np.minimum(a[:,:,3],np.round(keep*255).astype('uint8'))
  assert np.array_equal(a[:,:,:3],before[:,:,:3])
  assert np.array_equal(a[:,:760],before[:,:760])
  assert np.array_equal(a[1000:],before[1000:])
  assert np.any(a[:,:,3]!=before[:,:,3])
  rows=np.arange(780,1000)
  right=np.array([np.flatnonzero(a[row,:,3]>127)[-1] for row in rows])
  assert np.max(np.abs(right-(789+(rows-780)*(19/220)-0.5)))<=1
  im=Image.fromarray(a)
 im.save(O/f'{name}.png');box=im.getchannel('A').getbbox()
 layer=PixelLayer.frompil(im.crop(box),psd,name=name,top=box[1],left=box[0]);layer.remove_mask()
psd.save(O/'InkPortrait.psd');assert len(PSDImage.open(O/'InkPortrait.psd'))==19
print('Straight neck contour restored; only right-edge alpha changed')
