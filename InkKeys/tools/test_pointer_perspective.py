"""Check front-facing desk perspective against actual BongoCat framebuffer captures."""
from pathlib import Path
import argparse,json
import cv2,numpy as np
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser();p.add_argument('run',type=Path);a=p.parse_args()
def center(name):
    im=np.array(Image.open(a.run/'frames'/(name+'.png')).convert('RGBA'));h,w=im.shape[:2];yy,xx=np.mgrid[:h,:w];rgb=im[:,:,:3].astype(int)
    mask=(rgb[:,:,0]>215)&(rgb[:,:,1]>200)&(rgb[:,:,0]-rgb[:,:,1]>4)&(im[:,:,3]>200)&(yy>h*.67)&(xx<w*.43)
    n,labels,stats,c=cv2.connectedComponentsWithStats(mask.astype('uint8'),8)
    assert n>1,f'{name}: mouse palm missing'
    return c[1+np.argmax(stats[1:,cv2.CC_STAT_AREA])]
points={n:center(n) for n in ['mouse-left','mouse-right','mouse-top','mouse-bottom']}
dx=points['mouse-right'][0]-points['mouse-left'][0];dy=points['mouse-bottom'][1]-points['mouse-top'][1]
assert dx < -35, f'Physical right must move the character-right hand viewer-left, got delta {dx:.2f}px'
assert dy < -13, f'Physical forward must extend away from character toward viewer, got screen-down delta {dy:.2f}px'
print(json.dumps({'screen_right_to_hand_dx':dx,'screen_down_to_hand_dy':dy,'centroids':{k:v.tolist() for k,v in points.items()}},indent=2))
