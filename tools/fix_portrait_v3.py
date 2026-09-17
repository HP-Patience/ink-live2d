"""V3 portrait-only repairs: low-profile crown; preserve the V2 neck unchanged."""
from pathlib import Path
import json
import numpy as np
import cv2
from PIL import Image
from psd_tools import PSDImage
from psd_tools.api.layers import PixelLayer
W=Path(__file__).resolve().parents[1]/'workspace';O=W/'repaired-v3';O.mkdir(exist_ok=True)
names=[x['name'] for x in json.loads((W/'repaired/layers.json').read_text())]
ims={n:Image.open(W/'repaired-v2'/f'{n}.png').convert('RGBA') for n in names}
pad=160; width=1280;height=1280+pad
y,x=np.mgrid[:height,:width].astype(np.float32);y-=pad
# ponytail: extend this cropped crown with its own ink texture; a new portrait needs its own silhouette.
ext=35*np.maximum(0,1-((x-657)/236)**2)
ext+=np.maximum(0,1-((x-657)/236)**2)*(3*np.sin(x/19)+2*np.sin(x/8))
sy=np.where(y<160,160-(160-y)*160/(160+ext),y).astype(np.float32)
hair=cv2.remap(np.array(ims['front hair']),x,sy,cv2.INTER_CUBIC,borderMode=cv2.BORDER_CONSTANT)
# Keep the V2 neck pixels and silhouette unchanged, as requested.
psd=PSDImage.new('RGBA',(width,height));composite=Image.new('RGBA',(width,height),(32,35,40,255))
for n in names:
 im=Image.fromarray(hair) if n=='front hair' else Image.new('RGBA',(width,height))
 if n!='front hair':im.alpha_composite(ims[n],(0,pad))
 im.save(O/f'{n}.png');box=im.getchannel('A').getbbox();layer=PixelLayer.frompil(im.crop(box),psd,name=n,top=box[1],left=box[0]);layer.remove_mask();composite.alpha_composite(im)
psd.save(O/'InkPortrait.psd');composite.convert('RGB').save(W/'v3-source.jpg')
assert 118 <= Image.fromarray(hair[:,:,3]).getbbox()[1] <= 130
restored=np.array(Image.open(O/'neck.png'))[pad:]
old=np.array(ims['neck'])
assert np.array_equal(restored[:,:,3],old[:,:,3])
assert np.array_equal(restored[old[:,:,3]>0],old[old[:,:,3]>0])
assert len(PSDImage.open(O/'InkPortrait.psd'))==19
print('V3 source:',O/'InkPortrait.psd')
