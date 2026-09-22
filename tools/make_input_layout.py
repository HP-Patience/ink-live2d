"""Draw a compact physical keyboard and native per-key hand poses on the model canvas.
Keep the approved character untouched; only replace its previously generic key blocks.
"""
from pathlib import Path
import json,math
import cv2,numpy as np
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[1];S=1280;OUT=ROOT/'source/key-poses';OUT.mkdir(exist_ok=True)
U=50.;PW,PH=1240,366
keys={}
def key(name,label,x,y,w=1,h=1,code=None):
    assert name not in keys
    keys[name]={'label':label,'rect':[x*U+12,y*U+12,(x+w)*U+12-5,(y+h)*U+12-5],'vk':code}
# Main typing block: standard staggered ANSI/QWERTY physical arrangement.
key('Escape','Esc',0,0,code=27)
for n in range(1,13): key(f'F{n}',f'F{n}',1.5+n-1+(n-1)//4*.5,0,code=111+n)
y=1.4;x=0
for name,label,w,code in [('BackQuote','`',1,192)]+[(f'Num{n}',str(n),1,48+n) for n in [1,2,3,4,5,6,7,8,9,0]]+[('Minus','-',1,189),('Equal','=',1,187),('Backspace','Bksp',2,8)]:
    key(name,label,x,y,w,code=code);x+=w
y=2.4;x=0
for name,label,w,code in [('Tab','Tab',1.5,9)]+[(f'Key{n}',n,1,ord(n)) for n in 'QWERTYUIOP']+[('BracketLeft','[',1,219),('BracketRight',']',1,221),('Backslash','\\',1.5,220)]:
    key(name,label,x,y,w,code=code);x+=w
y=3.4;x=0
for name,label,w,code in [('CapsLock','Caps',1.75,20)]+[(f'Key{n}',n,1,ord(n)) for n in 'ASDFGHJKL']+[('Semicolon',';',1,186),('Quote',"'",1,222),('Return','Enter',2.25,13)]:
    key(name,label,x,y,w,code=code);x+=w
y=4.4;x=0
for name,label,w,code in [('ShiftLeft','Shift',2.25,16)]+[(f'Key{n}',n,1,ord(n)) for n in 'ZXCVBNM']+[('Comma',',',1,188),('Period','.',1,190),('Slash','/',1,191),('ShiftRight','Shift',2.75,16)]:
    key(name,label,x,y,w,code=code);x+=w
y=5.4;x=0
for name,label,w,code in [('ControlLeft','Ctrl',1.25,17),('Meta','Win',1.25,91),('Alt','Alt',1.25,18),('Space','Space',6.25,32),('AltGr','Alt',1.25,18),('Apps','Menu',1.25,93),('ControlRight','Ctrl',2.5,17)]:
    key(name,label,x,y,w,code=code);x+=w
# Navigation and numeric keypad. Each visible key has its own pose, not one area trigger.
for name,label,x,y,code in [('PrintScreen','Prt',15.7,0,44),('ScrollLock','Scr',16.7,0,145),('Pause','Pau',17.7,0,19),('Insert','Ins',15.7,1.4,45),('Home','Home',16.7,1.4,36),('PageUp','PgUp',17.7,1.4,33),('Delete','Del',15.7,2.4,46),('End','End',16.7,2.4,35),('PageDown','PgDn',17.7,2.4,34),('UpArrow','^',16.7,4.4,38),('LeftArrow','<',15.7,5.4,37),('DownArrow','v',16.7,5.4,40),('RightArrow','>',17.7,5.4,39)]: key(name,label,x,y,code=code)
for name,label,x,y,w,h,code in [('NumLock','Num',19.4,1.4,1,1,144),('KpDivide','/',20.4,1.4,1,1,111),('KpMultiply','*',21.4,1.4,1,1,106),('KpMinus','-',22.4,1.4,1,1,109),('KpPlus','+',22.4,2.4,1,2,107),('Kp0','0',19.4,5.4,2,1,96),('KpDecimal','.',21.4,5.4,1,1,110)]: key(name,label,x,y,w,h,code)
for row,nums in enumerate(['789','456','123']):
    for col,n in enumerate(nums):key('Kp'+n,n,19.4+col,2.4+row,code=96+int(n))
# BongoCat 1.11 names main Enter and numpad Enter both Return. It cannot disambiguate
# their physical scancodes at the model layer; only the main Enter is an active target.
key('_numpad_enter','Enter',22.4,4.4,1,2,None)
# Existing runtime also merges both OS keys; one Win cap is used deliberately.
# F13-F24 are genuine inputs without caps on a standard keyboard: shown as an
# alternate function-row target and an explicit active-key label, not silently discarded.
aliases={'Control':'ControlLeft','Shift':'ShiftLeft','Up':'UpArrow','Down':'DownArrow','Left':'LeftArrow','Right':'RightArrow','LeftBracket':'BracketLeft','RightBracket':'BracketRight','BackSlash':'Backslash','SemiColon':'Semicolon','Dot':'Period','Fn':'F1'}
for n in range(13,25):aliases[f'F{n}']=f'F{n-12}'
font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',18)
plane=Image.new('RGBA',(PW,PH),(0,0,0,0));d=ImageDraw.Draw(plane)
d.rounded_rectangle((0,0,PW-1,PH-1),radius=22,fill=(56,55,59),outline=(25,24,28),width=9)
d.rounded_rectangle((8,5,PW-9,PH-13),radius=16,fill=(88,87,92),outline=(130,129,134),width=3)
for item in keys.values():
    x0,y0,x1,y1=item['rect'];d.rounded_rectangle((x0,y0,x1,y1),radius=6,fill=(55,54,57),outline=(26,25,28),width=3)
    color=(159,158,163) if len(item['label'])>1 else (126,125,131)
    d.rounded_rectangle((x0+2,y0+1,x1-2,y1-6),radius=4,fill=color)
    d.text(((x0+x1)/2,(y0+y1)/2-3),item['label'],font=font,anchor='mm',fill=(242,241,245))
quad=np.float32([[548,978],[1116,979],[1171,1136],[490,1123]])
# Rotate the physical plane 180 degrees BEFORE projection: space faces the
# character, numpad is on character-right (viewer-left), and legends rotate too.
H=cv2.getPerspectiveTransform(np.float32([[0,0],[PW,0],[PW,PH],[0,PH]]),quad)
H=H@np.array([[-1.,0.,PW-1],[0.,-1.,PH-1],[0.,0.,1.]])
def project(x,y):
    p=H@np.array([x,y,1.]);return (float(p[0]/p[2]),float(p[1]/p[2]))
keyboard=Image.fromarray(cv2.warpPerspective(np.array(plane),H,(S,S),flags=cv2.INTER_CUBIC))
# Expand the far edge of the existing thin pad just enough for meaningful mouse travel.
scale=3;pad=Image.new('RGBA',(S*scale,S*scale));pdraw=ImageDraw.Draw(pad)
poly=[(218,935),(1126,935),(1218,1112),(1228,1141),(1210,1161),(1180,1169),(139,1158),(102,1149),(94,1132),(103,1107),(190,963)]
pdraw.polygon([(x*scale,y*scale) for x,y in poly],fill=(234,232,233,255));pdraw.line([(x*scale,y*scale) for x,y in poly+[poly[0]]],fill=(48,47,51,255),width=4*scale,joint='curve')
for pts in [[(124,1080),(260,1155),(353,1158),(145,1052)],[(162,1031),(410,1159),(448,1159),(179,1015)],[(1145,986),(1214,1114),(1217,1131),(1204,1148),(1115,1158)],[(1159,1031),(1103,1158),(1067,1158),(1149,1010)]]:
    pdraw.polygon([(x*scale,y*scale) for x,y in pts],fill=(80,79,84,255))
pad=pad.resize((S,S),Image.Resampling.LANCZOS);pad.alpha_composite(keyboard);pad.save(ROOT/'source/input-parts/desktop.png')
# Reuse only the approved palm/cuff. The sleeve connects it to the existing shoulder.
hand=Image.open(ROOT/'source/input-parts/hand keyboard.png').convert('RGBA')
a=np.array(hand)
# Extract the actual rounded palm plus its outline, never a rectangular sleeve
# crop. A cut-off rectangle looked like a square cuff in the previous overlays.
seed=((a[:,:,0]>180)&(a[:,:,1]>165)&(a[:,:,3]>180)).astype('uint8')
seed[:915]=0;seed[1015:]=0;seed[:,:755]=0;seed[:,915:]=0
contours,_=cv2.findContours(seed,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
assert contours,'Palm segmentation failed'
mask=np.zeros(seed.shape,dtype='uint8');cv2.drawContours(mask,[max(contours,key=cv2.contourArea)],-1,255,cv2.FILLED)
mask=cv2.dilate(mask,cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(11,11)))
a[:,:,3]=np.minimum(a[:,:,3],mask);palm=Image.fromarray(a)
# Smooth the hidden cuff crop; the drawn connecting sleeve covers this join.
shoulder=np.array([885.,875.]);palm_anchor=np.array([840.,995.]);palm_wrist=np.array([838.,923.])
layout={}
for name,item in list(keys.items()):
    if name.startswith('_'):continue
    x0,y0,x1,y1=item['rect'];hit=np.array(project((x0+x1)/2,(y0+y1)/2))
    # Move the hand across keys without rotating its wrist/fingers sideways.
    angle=0.0
    M=cv2.getRotationMatrix2D(tuple(palm_anchor),angle,.82);M[:,2]+=hit-palm_anchor
    wrist=M@np.r_[palm_wrist,1.]
    overlay=Image.new('RGBA',(S*scale,S*scale));od=ImageDraw.Draw(overlay)
    corners=[project(x0,y0),project(x1,y0),project(x1,y1),project(x0,y1)]
    od.polygon([(round(x*scale),round(y*scale)) for x,y in corners],fill=(237,234,224,255),outline=(62,61,66,255),width=2*scale)
    # Bend the sleeve, not the palm. The cubic ends vertically at the cuff so
    # the wrist joins without a kink; rounded shoulders replace the old rigid bar.
    c1=shoulder+np.array([0.,55.])
    c2=wrist-np.array([0.,42.])
    tt=np.linspace(0.,1.,65)[:,None]
    curve=(1-tt)**3*shoulder+3*(1-tt)**2*tt*c1+3*(1-tt)*tt**2*c2+tt**3*wrist
    tangent=3*(1-tt)**2*(c1-shoulder)+6*(1-tt)*tt*(c2-c1)+3*tt**2*(wrist-c2)
    normal=np.column_stack([-tangent[:,1],tangent[:,0]])/np.maximum(np.linalg.norm(tangent,axis=1)[:,None],.01)
    widths=47*(1-tt[:,0])+34*tt[:,0]
    edge1=curve+normal*widths[:,None];edge2=curve-normal*widths[:,None]
    outline=np.vstack([edge1,edge2[::-1]])
    od.polygon([tuple(np.rint(point*scale).astype(int)) for point in outline],fill=(36,35,39,255))
    for edge in [edge1,edge2]:
        od.line([tuple(np.rint(point*scale).astype(int)) for point in edge],fill=(19,18,22,255),width=4*scale,joint='curve')
    od.ellipse(((shoulder[0]-47)*scale,(shoulder[1]-45)*scale,(shoulder[0]+47)*scale,(shoulder[1]+45)*scale),fill=(36,35,39,255))
    crease=curve[39];n=normal[39]
    od.line([tuple((crease-n*24)*scale),tuple((crease+n*15+np.array([0.,6.]))*scale)],fill=(62,60,66,255),width=4*scale)
    od.ellipse(((wrist[0]-36)*scale,(wrist[1]-8)*scale,(wrist[0]+36)*scale,(wrist[1]+26)*scale),fill=(29,28,32,255))
    overlay=overlay.resize((S,S),Image.Resampling.LANCZOS)
    transformed=Image.fromarray(cv2.warpAffine(np.array(palm),M,(S,S),flags=cv2.INTER_CUBIC))
    overlay.alpha_composite(transformed);overlay.save(OUT/(name+'.png'))
    layout[name]={'hit':hit.tolist(),'polygon':corners,'vk':item['vk'],'label':item['label'],'palm_rotation_degrees':angle,'wrist':wrist.tolist(),'palm_affine':M.tolist()}
for alias,name in aliases.items():
    im=Image.open(OUT/(name+'.png')).convert('RGBA')
    if alias.startswith('F') and alias not in ['Fn']:
        d=ImageDraw.Draw(im);d.rounded_rectangle((920,900,1000,937),8,fill=(240,239,242),outline=(50,49,55),width=2);d.text((960,918),alias,font=font,anchor='mm',fill=(35,34,39))
    im.save(OUT/(alias+'.png'));layout[alias]={**layout[name],'alias_of':name,'vk':111+int(alias[1:]) if alias.startswith('F') and alias!='Fn' else layout[name]['vk']}
manifest={'orientation':'character-facing-180','canvas':[S,S],'keys':layout,'pointer':{'x_extent':90,'y_extent':36},'runtime_limitations':['Main and numpad Enter share Return in BongoCat 1.11.0.','Both Windows keys share Meta.','F13-F24 use the function-row alternative with an explicit label.']}
(ROOT/'source/key-layout.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
# Native Mver ordering retains left/right Shift/Ctrl/Alt rather than multiple aliases overwriting them.
order=[n for n in keys if not n.startswith('_')]+[f'F{n}' for n in range(13,25)]
(ROOT/'source/key-order.json').write_text(json.dumps(order),encoding='utf-8')
base=Image.new('RGBA',(S,S))
for name in ['desktop','back hair','topwear','ears','face','eyewhite-r','eyewhite-l','irides-r','irides-l','eyelash-r','eyelash-l','eyebrow','mouth_close','mouth','front hair','eyewear','mouse','hand mouse']:
    path=(ROOT/'source/input-parts' if name in ['desktop','mouse','hand mouse'] else ROOT/'source/layers')/(name+'.png');base.alpha_composite(Image.open(path).convert('RGBA'))
board=Image.new('RGB',(1440,960),(233,236,241));draw=ImageDraw.Draw(board)
for i,n in enumerate(['KeyA','KeyD','KeyJ','KeyP','Space','Return','UpArrow','Kp1','F1']):
    im=base.copy();im.alpha_composite(Image.open(OUT/(n+'.png')).convert('RGBA'));im=im.crop((80,730,1240,1190));im.thumbnail((475,270));x=i%3*480;y=i//3*320+28
    board.paste(im,(x,y),im);draw.text((x+10,y-19),n,fill='black')
board.save(ROOT/'validation/key-positions-design.png');print('Prepared',len(layout),'named key poses and a physical key layout.')
