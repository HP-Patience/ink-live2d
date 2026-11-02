"""Focused asset checks. A passing stage proves only that stage, not runtime behavior."""
from pathlib import Path
import argparse, hashlib, json
import numpy as np
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser();p.add_argument('stage',choices=['source','inputs','layers','model']);a=p.parse_args()
if a.stage=='source':
    ref=ROOT/'source/reference.png'
    assert ref.is_file(), 'Prepared reference.png is missing'
    im=Image.open(ref); assert im.mode=='RGBA' and im.size==(1280,1280),(im.mode,im.size)
    alpha=np.asarray(im)[:,:,3]
    assert alpha[0,0]==0 and np.count_nonzero(alpha>240)>300000, 'Broken source alpha'
    inp=Image.open(ROOT/'source/inference-input.png')
    assert inp.mode=='RGB' and inp.size==im.size, 'Inference input must be a white RGB composite'
    expected=Image.new('RGBA',im.size,'white');expected.alpha_composite(im)
    assert np.array_equal(np.asarray(inp),np.asarray(expected.convert('RGB'))), 'Inference input changed identity pixels'
    approved=ROOT.parents[0]/'ink-keys-v3/ink-keys-chibi-v3.png'
    assert hashlib.sha256(approved.read_bytes()).digest()==hashlib.sha256((ROOT/'source/approved.png').read_bytes()).digest(), 'Approved original was modified'
elif a.stage=='inputs':
    for name in ['hand keyboard','hand mouse','mouse','desktop']:
        path=ROOT/'source/input-parts'/f'{name}.png'
        assert path.is_file(), f'Missing input part: {name}'
        im=Image.open(path)
        assert im.size==(1280,1280) and im.mode=='RGBA' and im.getchannel('A').getbbox(),name
    desk=np.asarray(Image.open(ROOT/'source/input-parts/desktop.png'))
    # The revised pad extends to y=933 (including antialiasing) for larger mouse travel.
    assert not desk[:930,:,3].any(), 'Desktop must not contain face or body'
    assert desk[1000:1050,300:410,:3].mean()>185, 'Old mouse/hand colors contaminate repaired desk'
    assert desk[990:1040,300:420,:3].std()<18, 'Inpaint streaks remain beneath the movable mouse'
    mask=np.asarray(Image.open(ROOT/'source/input-parts/hand mouse.png'))[:,:,3]
    assert not mask[:,550:].any() and not mask[:760,:].any(), 'Mouse hand extraction leaked into face/keyboard'
elif a.stage=='layers':
    names=['face','eyewear','front hair','back hair','eyewhite-l','eyewhite-r','irides-l','irides-r','eyelash-l','eyelash-r','topwear','hand keyboard','hand mouse','mouse','desktop']
    for name in names:
        path=ROOT/'source/layers'/f'{name}.png'
        assert path.is_file(), f'Missing independently riggable layer: {name}'
        im=Image.open(path)
        assert im.mode=='RGBA' and im.size==(1280,1280), (name,im.mode,im.size)
        assert im.getchannel('A').getbbox(), f'Empty layer: {name}'
    assert (ROOT/'source/InkKeys.psd').is_file(), 'Editable PSD is missing'
    from psd_tools import PSDImage
    actual={layer.name for layer in PSDImage.open(ROOT/'source/InkKeys.psd')}
    assert set(names)<=actual, f'PSD semantic layer names missing: {set(names)-actual}'
else:
    folder=ROOT/'delivery/InkKeys'; manifest=folder/'InkKeys.model3.json'
    assert manifest.is_file(),'Exported model manifest missing'
    data=json.loads(manifest.read_text(encoding='utf-8')); refs=data['FileReferences']
    assets=[refs['Moc'],*refs['Textures'],refs['Physics'],refs['DisplayInfo']]
    assets += [m['File'] for group in refs.get('Motions',{}).values() for m in group]
    for name in assets:
        path=(folder/name).resolve()
        assert path.is_relative_to(folder.resolve()) and path.is_file(), f'Invalid model reference: {name}'
    assert (folder/refs['Moc']).read_bytes()[:4]==b'MOC3','Not a genuine MOC3 model'
    ids={item['Id'] for item in json.loads((folder/refs['DisplayInfo']).read_text(encoding='utf-8'))['Parameters']}
    required={'ParamAngleX','ParamAngleY','ParamEyeLOpen','ParamEyeROpen','ParamEyeBallX','ParamEyeBallY','ParamBreath','CatParamLeftHandDown','ParamMouseX','ParamMouseY','ParamMouseLeftDown','ParamMouseRightDown'}
    assert required<=ids, f'Missing required rig parameters: {sorted(required-ids)}'
    assert (ROOT/'source/InkKeys.cmo3').is_file(),'Editable CMO3 missing'
    required_keys=['UpArrow','DownArrow','LeftArrow','RightArrow','Kp0','Kp9','NumLock','F1','F24','BracketLeft','BracketRight','Backslash','Semicolon','Period']
    assert all((folder/'resources/left-keys'/(key+'.png')).is_file() for key in required_keys),'Native key aliases missing'
print(f'PASS {a.stage}: structural asset checks only; native visual/input validation is separate.')





