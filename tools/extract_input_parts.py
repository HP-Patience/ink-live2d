"""Extract approved desk and input limbs. Hidden pixels are repaired, not new visible character art.
The paths are specific to the approved 1280px source; they are not a general segmenter.
"""
from pathlib import Path
import numpy as np
import cv2
from PIL import Image, ImageDraw, ImageFilter
ROOT=Path(__file__).resolve().parents[1]; OUT=ROOT/'source/input-parts';OUT.mkdir(exist_ok=True)
S=1280; src=Image.open(ROOT/'source/reference.png').convert('RGBA'); data=np.asarray(src); rgb=data[:,:,:3]

def path(start,segments):
    points=[start];p=np.array(start,dtype=float)
    for seg in segments:
        if len(seg)==2: p=np.array(seg,dtype=float);points.append(tuple(p));continue
        c1,c2,end=[np.array(t,dtype=float) for t in seg]
        for t in np.linspace(0,1,50)[1:]:points.append(tuple((1-t)**3*p+3*(1-t)**2*t*c1+3*(1-t)*t*t*c2+t**3*end))
        p=end
    im=Image.new('L',(S*3,S*3));ImageDraw.Draw(im).polygon([(round(x*3),round(y*3)) for x,y in points],fill=255)
    return im.resize((S,S),Image.Resampling.LANCZOS)

def extract(mask):
    im=src.copy();im.putalpha(Image.fromarray(np.minimum(data[:,:,3],np.asarray(mask))));return im

def save(name,im):
    assert im.mode=='RGBA' and im.size==(S,S) and im.getchannel('A').getbbox(), name
    im.save(OUT/(name+'.png'))

left=path((399,815),[
    ((362,836),(301,861),(291,901)),((287,919),(290,933),(279,951)),
    ((269,971),(280,987),(301,990)),((320,1001),(345,996),(354,998)),
    ((367,1004),(388,1002),(401,996)),((416,1000),(431,997),(440,988)),
    ((456,1004),(484,995),(495,974)),((512,942),(491,887),(471,862)),
    ((452,840),(420,824),(399,815))])
right=path((829,807),[
    ((857,806),(894,815),(914,839)),((931,862),(968,870),(980,890)),
    ((989,908),(982,925),(994,946)),((1003,962),(1008,979),(997,992)),
    ((985,1001),(943,1004),(908,1001)),((898,1012),(880,1011),(868,1006)),
    ((855,1015),(835,1011),(828,1007)),((810,1014),(791,1009),(785,1002)),
    ((773,1005),(765,990),(766,973)),((765,931),(787,881),(802,850)),
    ((812,834),(821,821),(829,807))])
mousemask=path((314,961),[
    ((346,953),(412,957),(439,975)),((453,988),(458,1000),(449,1018)),
    ((443,1042),(416,1067),(388,1072)),((350,1078),(294,1070),(280,1057)),
    ((263,1048),(268,1031),(277,1016)),((288,997),(300,976),(314,961))])
deskmask=path((219,979),[
    (1118,978),((1143,979),(1148,996),(1160,1015)),(1204,1099),
    ((1226,1134),(1214,1164),(1184,1166)),(146,1154),
    ((112,1154),(91,1143),(100,1119)),(181,1008),
    ((194,991),(199,984),(219,979))])
save('hand mouse',extract(left));save('hand keyboard',extract(right))
# Restore the mouse shell hidden under fingers. This region remains covered in neutral.
mouse=Image.new('RGBA',(S,S),(63,63,66,255));mouse.putalpha(mousemask)
visible_mouse=np.minimum(np.asarray(mousemask),255-np.asarray(left))
mouse.alpha_composite(extract(Image.fromarray(visible_mouse)))
save('mouse',mouse)
# Fill only hidden desktop pixels. The visible keyboard/mat are copied from the approved art.
hidden=np.maximum.reduce([np.asarray(left),np.asarray(right),np.asarray(mousemask)])
hidden=((hidden>8)&(np.asarray(deskmask)>0)).astype(np.uint8)*255
# Give the inpaint solver background context rather than the black RGB of transparent pixels.
white=Image.new('RGBA',(S,S),'white');white.alpha_composite(src)
clean=np.array(white.convert('RGB'))
# This mat is a plain grey surface. Generic inpaint pulls dark sleeves into it;
# reconstruct its occluded surface from nearby mat colors, not from the character.
yy,xx=np.mgrid[:S,:S]
surface=np.empty_like(clean)
for y in range(S):
    sample_y=min(1055,max(995,y))
    surface[y,:]=(234,232,233)
clean[hidden>0]=surface[hidden>0]
# Restore the top edge of the keyboard hidden by the right palm by reusing the
# adjacent keycap strip. Only occluded pixels are replaced; visible keys stay exact.
keyboard_patch=np.array(white.convert('RGB'))[978:1022,650:778].copy()
region=clean[978:1022,782:910];mask=hidden[978:1022,782:910]>0
region[mask]=keyboard_patch[mask]
# Remove the old stationary mouse shadow so it cannot remain after pointer travel.
shadow=((xx>246)&(xx<470)&(yy>996)&(yy<1086))
shadow &= (np.asarray(deskmask)>250)
clean[shadow]=surface[shadow]
desk=Image.fromarray(clean).convert('RGBA');desk.putalpha(deskmask);save('desktop',desk)
# Neutral input-only stack used for visual inspection. Head/body are handled separately.
stack=Image.new('RGBA',(S,S))
for n in ['desktop','mouse','hand mouse','hand keyboard']:stack.alpha_composite(Image.open(OUT/(n+'.png')))
stack.save(OUT/'input-stack.png')
# A labeled contact sheet preserves transparency against a neutral background.
board=Image.new('RGB',(1200,660),(230,233,239));draw=ImageDraw.Draw(board)
for i,n in enumerate(['hand mouse','hand keyboard','mouse','desktop']):
    im=Image.open(OUT/(n+'.png'));box=im.getbbox();part=im.crop(box);part.thumbnail((560,255))
    x=(i%2)*600+(600-part.width)//2;y=(i//2)*330+45
    board.paste(part,(x,y),part);draw.text(((i%2)*600+16,(i//2)*330+14),n,fill='black')
board.save(ROOT/'validation/input-parts-contact.png')
print('Extracted four independent input parts; inspect the contact sheet and moved poses before export.')


