"""Portrait-specific source repair: eliminate ear/cheek copies from the back-hair texture."""
from pathlib import Path
import numpy as np
import cv2
from PIL import Image,ImageDraw,ImageFilter
from psd_tools import PSDImage
from psd_tools.api.layers import PixelLayer
W=Path(__file__).resolve().parents[1]/'workspace';O=W/'repaired-v2';O.mkdir(exist_ok=True)
names=[x['name'] for x in __import__('json').loads((W/'repaired/layers.json').read_text())]
images={n:Image.open(W/'repaired'/f'{n}.png').convert('RGBA') for n in names}
back=images['back hair'];a=np.array(back);h,w=a.shape[:2]
# ponytail: masks target this portrait only; another illustration needs its own segmentation.
mask=Image.new('L',(w,h));d=ImageDraw.Draw(mask)
d.polygon([(315,377),(374,360),(438,422),(493,629),(521,754),(435,693),(392,575),(326,491)],fill=255)
d.polygon([(879,354),(987,363),(1003,499),(925,592),(860,714),(791,769),(819,619),(859,473)],fill=255)
# The same contaminated back layer also copied the white jaw/neck edges below each ear.
d.rectangle((260,550,530,770),fill=255)
d.rectangle((750,550,1040,770),fill=255)
# Continue existing dark hair into the old ear/skin area, without retaining any anatomical lines.
gray=cv2.cvtColor(a[:,:,:3],cv2.COLOR_RGB2GRAY)
fill=cv2.resize(gray[317:372,345:401],(w,h),interpolation=cv2.INTER_LINEAR)
fill=np.minimum(fill,42).astype('uint8')
weight=np.asarray(mask.filter(ImageFilter.GaussianBlur(5)),dtype=float)/255
for c in range(3):a[:,:,c]=(a[:,:,c]*(1-weight)+fill*weight).astype('uint8')
images['back hair']=Image.fromarray(a)
# Assert the masked ear cores cannot still contain white ear/cheek fragments.
core=np.asarray(mask)==255
assert np.percentile(a[:,:,0][core & (a[:,:,3]>30)],99)<65
psd=PSDImage.new('RGBA',(w,h))
for name in names:
 im=images[name];im.save(O/f'{name}.png');box=im.getchannel('A').getbbox()
 layer=PixelLayer.frompil(im.crop(box),psd,name=name,top=box[1],left=box[0]);layer.remove_mask()
psd.save(O/'InkPortrait.psd')
check=PSDImage.open(O/'InkPortrait.psd');assert len(check)==19
assert check[0].topil().getchannel('A').getextrema()==(0,255)
print('Repaired duplicate ears:',O/'InkPortrait.psd')
