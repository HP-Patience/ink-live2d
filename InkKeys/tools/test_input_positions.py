"""Regressions for distinct physical key landing positions and usable pointer travel."""
from pathlib import Path
import hashlib,json
from PIL import Image
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
folder=ROOT/'delivery/InkKeys/resources/left-keys'
names=['KeyA','KeyD','KeyJ','KeyZ','KeyP','Space','Return','UpArrow','Kp1']
textures=[folder/(n+'.png') for n in names]
assert all(p.is_file() for p in textures),'Missing named key resources'
assert len({hashlib.sha256(p.read_bytes()).hexdigest() for p in textures})==len(textures),'All physical keys still share the same pose'
for p in textures:
    im=Image.open(p).convert('RGBA');assert im.size==(1280,1280),'Overlay must share the model canvas'
    assert np.count_nonzero(np.array(im)[:,:,3]>200)>1500,'Per-key art is only an invisible trigger'
layout=json.loads((ROOT/'source/key-layout.json').read_text())
keys=layout['keys']
assert keys['KeyA']['hit'][0]>keys['KeyD']['hit'][0]>keys['KeyJ']['hit'][0]>keys['Return']['hit'][0], 'Keyboard faces spectator rather than character'
assert keys['Num1']['hit'][1]>keys['KeyQ']['hit'][1]>keys['KeyA']['hit'][1]>keys['KeyZ']['hit'][1]>keys['Space']['hit'][1], 'Space must be nearest the character, number row farther away'
assert keys['Kp1']['hit'][0]<keys['KeyA']['hit'][0], 'Numpad belongs on character-right / viewer-left'
for name,key in keys.items():
    assert abs(key.get('palm_rotation_degrees',999))<=1, f'{name}: palm twisted sideways'
    assert key['wrist'][1]<key['hit'][1], f'{name}: wrist must stay behind fingers'
    assert abs(key['wrist'][0]-key['hit'][0])<5, f'{name}: wrist/fingertip axis is crooked'
assert keys['ControlLeft']['hit']!=keys['ControlRight']['hit']
assert keys['ShiftLeft']['hit']!=keys['ShiftRight']['hit']
assert layout['pointer']['x_extent']>=80 and layout['pointer']['y_extent']>=35,'Mouse travel remains tiny'
print('PASS distinct-key assets, QWERTY rows, sided modifiers, and pointer extent spec. Native captures still required.')
