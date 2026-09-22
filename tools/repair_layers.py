"""Repair semantic layers for the approved chibi; preserve inference separately."""
from pathlib import Path
import shutil
import cv2,numpy as np
from PIL import Image,ImageDraw
from psd_tools import PSDImage
from psd_tools.api.layers import PixelLayer
ROOT=Path(__file__).resolve().parents[1]; RAW=ROOT/'workspace/inference-output/inference-input'; OUT=ROOT/'source/layers';OUT.mkdir(exist_ok=True)
S=1280;src=Image.open(ROOT/'source/reference.png').convert('RGBA'); rgba=np.asarray(src)
layers=[]

def clean(name,box,minimum=35):
    a=np.array(Image.open(RAW/(name+'.png')).convert('RGBA'));alpha=a[:,:,3]
    count,labels,stats,_=cv2.connectedComponentsWithStats((alpha>30).astype('uint8'),8)
    keep=np.zeros(count,dtype=bool);keep[1:]=stats[1:,cv2.CC_STAT_AREA]>=minimum
    a[~keep[labels],3]=0
    x0,y0,x1,y1=box;a[:y0,:,3]=0;a[y1:,:,3]=0;a[:,:x0,3]=0;a[:,x1:,3]=0
    return Image.fromarray(a)

def add(name,im):
    assert im.mode=='RGBA' and im.size==(S,S) and im.getchannel('A').getbbox(),name
    im.save(OUT/(name+'.png'));layers.append((name,im))

def side(im,left):
    a=np.array(im);a[:,650 if left else 0:1280 if left else 650,3]=0
    return Image.fromarray(a)

# PSD append order is back-to-front. The desktop is static and contains no hands.
add('desktop',Image.open(ROOT/'source/input-parts/desktop.png').convert('RGBA'))
back=clean('back hair',(280,160,1060,885),150)
# The diffusion fill is too light and extends into the torso. Darken only hidden
# back-hair paint; the visible original hair contour is retained by front hair.
ba=np.array(back);ba[:,:,:3]=np.minimum(ba[:,:,:3],np.array([43,42,44],dtype=np.uint8));add('back hair',Image.fromarray(ba))
body=clean('topwear',(330,730,956,988),200)
# Original central torso is unoccluded, so retain its exact linework below chin.
b=np.array(body);visible=(b[:,:,3]>245)&(np.indices((S,S))[0]>850)&(np.indices((S,S))[1]>495)&(np.indices((S,S))[1]<770)
b[visible,:3]=rgba[visible,:3];add('topwear',Image.fromarray(b))
# Ears remain independent so head turns don't drag duplicate ears from the hair.
add('ears',clean('ears',(312,605,1015,823),120))
face=clean('face',(380,435,928,856),400);add('face',face)
for raw in ['eyewhite','irides','eyelash']:
    im=clean(raw,(407,640,911,770),60)
    # Character-left is screen-right; PSD2Live uses anatomical L/R IDs.
    add(raw+'-r',side(im,True));add(raw+'-l',side(im,False))
add('eyebrow',clean('eyebrow',(427,592,868,651),55))
add('mouth_close',clean('mouth',(641,785,689,815),8))
# A tiny enclosed dark mouth beneath the closed line enables real mouth opening
# without adding teeth or changing the approved neutral expression.
mouth=Image.new('RGBA',(S,S));ImageDraw.Draw(mouth).ellipse((653,796,672,804),fill=(53,45,49,255));add('mouth',mouth)
front=clean('front hair',(140,90,1145,829),200)
# Use original RGB where inferred hair lies over the original dark silhouette;
# avoid replacing inferred occlusion repairs with white background pixels.
f=np.array(front);dark=(rgba[:,:,:3].max(axis=2)<110)&(rgba[:,:,3]>200)&(f[:,:,3]>200)
f[dark,:3]=rgba[dark,:3];add('front hair',Image.fromarray(f))
add('eyewear',clean('eyewear',(392,650,930,793),90))
for name in ['mouse','hand mouse','hand keyboard']:
    add(name,Image.open(ROOT/'source/input-parts'/(name+'.png')).convert('RGBA'))
canvas=Image.new('RGBA',(S,S))
for name,im in layers:canvas.alpha_composite(im)
canvas.save(ROOT/'source/neutral-composite.png')
psd=PSDImage.new('RGBA',(S,S))
for name,im in layers:
    box=im.getbbox();PixelLayer.frompil(im.crop(box),psd,name=name,top=box[1],left=box[0])
psd.save(ROOT/'source/Ruotengwu.psd')
# Check actual PSD raster composite rather than assuming append semantics.
composite=psd.composite(force=True).convert('RGBA')
composite.save(ROOT/'validation/psd-composite.png')
a=np.array(composite).astype(float);b=np.array(canvas).astype(float)
assert np.abs(a[:,:,3]-b[:,:,3]).mean()<2,'PSD alpha diverged'
assert np.abs(a[:,:,:3]*a[:,:,3:4]/255-b[:,:,:3]*b[:,:,3:4]/255).mean()<2,'PSD visible composite diverged'
board=Image.new('RGB',(1200,((len(layers)+3)//4)*260),(228,232,237));d=ImageDraw.Draw(board)
for i,(name,im) in enumerate(layers):
    piece=im.crop(im.getbbox());piece.thumbnail((280,220));x=i%4*300+(300-piece.width)//2;y=i//4*260+30
    board.paste(piece,(x,y),piece);d.text((i%4*300+10,i//4*260+8),name,fill='black')
board.save(ROOT/'validation/repaired-layers-contact.png')
print('Saved',len(layers),'independent layers and editable PSD. Native pose inspection is still required.')


