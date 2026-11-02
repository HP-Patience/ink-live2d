"""Portrait-specific tapered straight neck and an independently occluded rear collar."""
from pathlib import Path
import json
import numpy as np
from PIL import Image, ImageDraw
from psd_tools import PSDImage
from psd_tools.api.layers import PixelLayer
W=Path(__file__).resolve().parents[1]/'workspace'; O=W/'repaired-v6'; O.mkdir(exist_ok=True)
names=[x['name'] for x in json.loads((W/'repaired/layers.json').read_text())]
ims={n:Image.open(W/'repaired-v3'/f'{n}.png').convert('RGBA') for n in names}
a=np.array(ims['neck']); before=a.copy(); y,x=np.mgrid[:1440,:1280]; y=y-160
# ponytail: measured for this portrait; a different drawing needs different contour anchors.
edge=789-(y-620)*(11/220)
keep=np.clip(edge-x,0,1); keep[y>=900]=1
# The return to the old lower silhouette is hidden well inside the front collar.
a[:,:,3]=np.minimum(a[:,:,3],np.round(keep*255).astype('uint8'))
assert np.array_equal(a[:,:,:3],before[:,:,:3])
assert np.array_equal(a[:,:750],before[:,:750])
rows=np.arange(780,1050)
right=np.array([np.flatnonzero(a[row,:,3]>127)[-1] for row in rows])
assert np.max(np.abs(right-(789-(rows-780)*(11/220)-.5)))<=1
assert right[-1]<right[0]
ims['neck']=Image.fromarray(a)
# Complete the rear collar BEHIND the neck, not as a patch painted over moving skin.
# Keep its bounds within existing topwear so shoulder/body anchors remain unchanged.
scale=4; mask=Image.new('L',(1280*scale,1440*scale)); d=ImageDraw.Draw(mask)
xx=np.arange(470,821); t=(xx-470)/350
upper=743*(1-t)**2+2*733*t*(1-t)+738*t*t
points=[(int(px*scale),int((py+160)*scale)) for px,py in zip(xx,upper)]
points += [(838*scale,990*scale),(812*scale,1090*scale),(478*scale,1090*scale),(450*scale,965*scale)]
d.polygon(points,fill=255)
mask=mask.resize((1280,1440),Image.Resampling.LANCZOS)
cloth=np.array(ims['topwear'].crop((540,1080,740,1220)).resize((1280,1440),Image.Resampling.BICUBIC))
cloth[:,:,:3]=np.clip(cloth[:,:,:3].astype(float)*.2+2,2,14).astype('uint8')
cloth[:,:,3]=np.array(mask)
rear=Image.fromarray(cloth)
rim=Image.new('RGBA',rear.size); dr=ImageDraw.Draw(rim)
dr.line([(int(px),int(py+161)) for px,py in zip(xx,upper)],fill=(15,15,15,190),width=1)
rear=Image.alpha_composite(rear,rim)
rear.putalpha(mask)
ims['topwear back']=rear
names.insert(names.index('neck'),'topwear back')
psd=PSDImage.new('RGBA',(1280,1440))
for name in names:
 im=ims[name]; im.save(O/f'{name}.png'); box=im.getchannel('A').getbbox()
 layer=PixelLayer.frompil(im.crop(box),psd,name=name,top=box[1],left=box[0]); layer.remove_mask()
psd.save(O/'InkPortrait.psd'); assert len(PSDImage.open(O/'InkPortrait.psd'))==20
assert np.all(np.array(rear)[920:1010,785:817,3]==255), 'Rear collar must fill newly exposed gap'
for name in names:
 if name not in ('neck','topwear back'):
  assert np.array_equal(np.array(ims[name]),np.array(Image.open(W/'repaired-v3'/f'{name}.png')))
print('Straight upper-wide/lower-narrow neck; rear collar below neck; all existing non-neck layers unchanged')
