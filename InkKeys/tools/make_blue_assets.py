"""Independent keyboard polygons and mouse button tint masks; no new character art."""
from pathlib import Path
import json
import numpy as np
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[1];S=1280
layout=json.loads((ROOT/'source/key-layout.json').read_text());order=json.loads((ROOT/'source/key-order.json').read_text())
meta={'version':1,'canvas':[S,S],'keys':[{'name':n,'polygon':layout['keys'][n]['polygon']} for n in order]}
(ROOT/'source/key-highlights.json').write_text(json.dumps(meta,indent=2)+'\n',encoding='utf-8')
a=np.array(Image.open(ROOT/'source/input-parts/mouse.png').convert('RGBA'));yy,xx=np.mgrid[:S,:S]
# Front-facing mouse: user's left button is the visible right half. Keep the
# scroll wheel and dark perimeter original, with tinted grey panel shading.
inside=(a[:,:,3]>200)&(a[:,:,:3].mean(axis=2)>52)&(yy<1056)&(yy>958)
wheel=((xx-330)/15)**2+((yy-1020)/26)**2<1
split=334-(yy-1000)*.35
for name,side in [('mouse-blue-left',xx>split+2),('mouse-blue-right',xx<split-2)]:
    mask=inside&side&~wheel
    # Tight rounded shell constraint prevents highlighting the bottom casing/shadow.
    mask &= ((xx-362)/97)**2+((yy-1013)/65)**2<1
    out=a.copy();brightness=np.clip(a[:,:,:3].mean(axis=2)/80,.65,1.12)
    out[:,:,:3]=np.clip(brightness[:,:,None]*np.array([77,163,255]),0,255).astype('uint8')
    out[:,:,3]=np.where(mask,215,0).astype('uint8')
    Image.fromarray(out).save(ROOT/'source/input-parts'/(name+'.png'))
print('Wrote',len(order),'independent held-key polygons and two mouse tint layers')
