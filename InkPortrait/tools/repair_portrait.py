"""Repair this portrait's layers; masks are deliberately image-specific, not an auto-segmentation tool."""
from pathlib import Path
import json
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageOps
from psd_tools import PSDImage
from psd_tools.api.layers import PixelLayer

W=Path(__file__).resolve().parents[1]/'workspace'; R=W/'layered/InkPortrait'; O=W/'repaired'; O.mkdir(exist_ok=True)
S=1280
src=Image.open(R/'src_img.png').convert('RGB'); rgb=np.asarray(src); yy,xx=np.mgrid[:S,:S]
layers=[]

def pathmask(start,segments):
    points=[start]; p=np.array(start,dtype=float)
    for seg in segments:
        if len(seg)==2: p=np.array(seg,dtype=float);points.append(tuple(p));continue
        c1,c2,p1=[np.array(t,dtype=float) for t in seg]
        for t in np.linspace(0,1,45)[1:]: points.append(tuple((1-t)**3*p+3*(1-t)**2*t*c1+3*(1-t)*t*t*c2+t**3*p1))
        p=p1
    im=Image.new('L',(S*2,S*2));ImageDraw.Draw(im).polygon([(int(x*2),int(y*2)) for x,y in points],fill=255)
    return im.resize((S,S),Image.Resampling.LANCZOS)

def clean(name,box=None):
    a=np.array(Image.open(R/(name+'.png')).convert('RGBA'))
    # Remove the diffusion decoder's low-alpha noise, retaining antialiased component edges.
    a[:,:,3]=np.clip((a[:,:,3].astype(float)-12)*255/243,0,255).astype('uint8')
    gray=cv2.cvtColor(a[:,:,:3],cv2.COLOR_RGB2GRAY);a[:,:,:3]=gray[:,:,None]
    count,labels,stats,_=cv2.connectedComponentsWithStats((a[:,:,3]>0).astype('uint8'),8)
    keep=np.zeros(count,dtype=bool);keep[1:]=stats[1:,cv2.CC_STAT_AREA]>=10
    a[~keep[labels],3]=0
    if box:
        x0,y0,x1,y1=box;a[:y0,:,3]=0;a[y1:,:,3]=0;a[:,:x0,3]=0;a[:,x1:,3]=0
    return Image.fromarray(a)

def add(name,im):
    assert im.size==(S,S)
    assert im.getchannel('A').getbbox(),name
    im.save(O/(name+'.png'));layers.append((name,im))

def masked(image,alpha):
    out=image.convert('RGBA');out.putalpha(alpha);return out

# Back hair: recover original black ink instead of the incorrectly inferred pale crown.
back=clean('back hair',(260,300,1030,770)); ba=np.array(back.getchannel('A'));ba[yy<300]=0
add('back hair',masked(src,Image.fromarray(ba)))

# Extend hidden neck above the visible V so modest head turns cannot reveal a hole.
neck=clean('neck',(440,585,845,935))
neckmask=pathmask((472,593),[((520,574),(759,574),(812,603)),((827,704),(805,837),(800,908)),((689,947),(535,937),(480,896)),((489,793),(465,671),(472,593))])
texture=np.full_like(rgb,158)
# Hidden under-jaw fill uses neck texture only, never adjacent black background/clothing.
for y in range(580,820):
    row=rgb[785+(y%25):786+(y%25),510:790]
    texture[y,455:830]=cv2.resize(row,(375,1))[0]
nb=masked(Image.fromarray(texture),neckmask);nb.alpha_composite(neck);add('neck',nb)

# Original turtleneck and shoulders, not the model's misclassified glasses layer.
bodymask=pathmask((0,1037),[((126,963),(264,936),(357,880)),(389,874),(408,842),(416,790),(423,770),(471,743),(477,819),((527,850),(592,875),(646,880)),((715,873),(773,851),(809,826)),(814,734),(858,759),(866,774),(874,836),(890,869),(936,884),((1029,969),(1174,982),(1280,1050)),(1280,1280),(0,1280)])
add('topwear',masked(src,bodymask))

# Keep ears, discard the hallucinated central scalp blob.
ears=clean('ears',(310,365,985,565)); ea=np.array(ears);ea[(xx>462)&(xx<840),3]=0
add('ears',Image.fromarray(ea))

# Underpainting: original lower-face tone and hatching, with independently animated features removed.
face_mask=pathmask((405,420),[((379,310),(471,190),(639,184)),((809,176),(912,298),(897,423)),((884,512),(866,574),(823,623)),((786,677),(713,735),(671,771)),((651,782),(615,781),(595,770)),((551,730),(485,679),(455,631)),((421,578),(412,524),(405,420))])
# Source lower face is preserved; inpaint only detached facial features/eyeglass lines.
remove=np.zeros((S,S),np.uint8)
for name in ['eyewear','nose','mouth']:
    a=np.array(clean(name).getchannel('A'));remove=np.maximum(remove,(a>20).astype('uint8')*255)
remove=cv2.dilate(remove,np.ones((13,13),np.uint8))
remove[xx<415]=0;remove[xx>880]=0
cleanrgb=cv2.inpaint(rgb,remove,9,cv2.INPAINT_TELEA)
# Hair and eyes obscure the upper face in the input: reconstruct a neutral skin surface underneath.
base=np.full_like(rgb,236)
# Small original paper variation, sampled from the unobstructed cheek, avoids a flat synthetic white.
patch=cv2.GaussianBlur(rgb[560:615,680:780],(0,0),4)
base[:]=cv2.resize(patch,(S,S))
w=np.clip((yy-490)/65,0,1)[:,:,None]
face=(base*(1-w)+cleanrgb*w).astype('uint8')
# Preserve the visible forehead without copying eyebrow or hair roots onto the skin.
forehead=pathmask((474,258),[((494,239),(546,233),(578,255)),(556,341),((517,334),(473,335),(446,345)),(454,301)])
fw=np.array(forehead.filter(ImageFilter.GaussianBlur(7)))[:,:,None]/255
face=(face*(1-fw)+rgb*fw).astype('uint8')
add('face',masked(Image.fromarray(face),face_mask))

# Eye components, explicitly sided so pupils clip only to their own eye-white.
for side,box in [('r',(390,375,618,470)),('l',(670,375,890,470))]:
    add('eyewhite-'+side,clean('eyewhite',box))
    add('irides-'+side,clean('irides',box))
    lash=np.array(clean('eyelash',box));x0,y0,x1,y1=box
    # The split follows the upper edge, excluding the separate lower eyelid.
    anchors=([(406,410),(441,414),(490,422),(534,426),(585,427),(617,438)] if side=='r'
             else [(670,436),(711,428),(761,422),(804,417),(850,412),(890,414)])
    cutoff=np.interp(xx,[p[0] for p in anchors],[p[1] for p in anchors])
    upper=lash.copy();upper[yy>cutoff,3]=0
    lower=lash.copy();lower[yy<=cutoff,3]=0
    add('facedetail-'+side,Image.fromarray(lower))
    add('eyelash-'+side,Image.fromarray(upper))
add('eyebrow',clean('eyebrow',(395,330,895,390)))
add('nose',clean('nose',(580,450,680,605)))

# Maximum speaking mouth in the same monochrome ink style; original closed lips stay a separate layer.
mouthshape=pathmask((575,651),[((597,638),(614,631),(636,633)),((654,631),(686,640),(705,652)),((684,665),(665,677),(638,678)),((614,679),(590,664),(575,651))])
mouth=Image.new('RGBA',(S,S),(22,22,22,0));mouth.putalpha(mouthshape)
teethmask=pathmask((586,649),[((615,646),(658,645),(694,650)),((662,651),(615,652),(586,649))])
tonguemask=pathmask((602,667),[((618,659),(651,661),(671,668)),((652,676),(621,678),(602,667))])
mouth.alpha_composite(masked(Image.new('RGB',(S,S),(210,210,210)),teethmask))
mouth.alpha_composite(masked(Image.new('RGB',(S,S),(49,49,49)),tonguemask))
add('mouth',mouth)
add('mouth_close',clean('mouth',(555,620,722,698)))
add('eyewear',clean('eyewear',(360,375,915,545)))
add('front hair',clean('front hair',(220,0,1120,590)))

psd=PSDImage.new('RGBA',(S,S))
for name,im in layers:
    bbox=im.getchannel('A').getbbox();crop=im.crop(bbox)
    layer=PixelLayer.frompil(crop,psd,name=name,top=bbox[1],left=bbox[0])
    layer.remove_mask()
psd.save(O/'InkPortrait.psd')
# Neutral assembly excludes the maximum-open mouth, which is closed by the rig in the runtime.
comp=Image.new('RGBA',(S,S))
for name,im in layers:
    if name!='mouth':comp.alpha_composite(im)
comp.save(O/'neutral.png')
bg=Image.new('RGBA',(S,S),(33,36,42,255));bg.alpha_composite(comp);bg.convert('RGB').save(O/'neutral-preview.jpg',quality=95)
check=PSDImage.open(O/'InkPortrait.psd')
assert len(check)==len(layers)
assert check[-1].topil().getchannel('A').getextrema()==(0,255),'PSD lost native alpha'
assert np.asarray(comp)[1000,640,3]==255,'Missing clothing'
assert np.asarray(comp)[580,700,3]==255,'Transparent cheek'
assert len([n for n,_ in layers if n.startswith('eyewhite-')])==2
(O/'layers.json').write_text(json.dumps([{'name':n,'bbox':im.getbbox()} for n,im in layers],indent=2))
print('Repaired PSD:',O/'InkPortrait.psd','layers:',len(layers))
