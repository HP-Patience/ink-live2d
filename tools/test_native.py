"""Exercise the installed BongoCat, isolated from the user's model/config directory.
The built-in audits prove input routing; captured images still require visual inspection.
"""
from pathlib import Path
import argparse, hashlib, json, os, shutil, subprocess, time
import numpy as np
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser();p.add_argument('--scenario',default='all');p.add_argument('--pose',choices=['neutral','blink','halfblink','left','right','up','down','tilt-left','tilt-right','mouth']);p.add_argument('--import-model',action='store_true');p.add_argument('--import-zip',action='store_true');p.add_argument('--app',type=Path,default=Path(r'C:\Users\wjx\AppData\Local\Programs\BongoCat\BongoCat.exe'));a=p.parse_args()
model=ROOT/'delivery/Ruotengwu';assert (model/'Ruotengwu.model3.json').is_file(),'Package the actual model first'
assert a.app.is_file(),a.app
scenarios=['idle','key-left','key-tab-left','key-left-release','mouse-left','mouse-right','mouse-move','mouse-move-mirror','mouse-reverse','mouse-hand-screen'] if a.scenario=='all' else [a.scenario]
if a.pose:scenarios=['motion-0']
run=ROOT/'validation/native'/time.strftime('%Y%m%d-%H%M%S');run.mkdir(parents=True,exist_ok=False)
(ROOT/'validation/latest-native-run.txt').write_text(str(run))
reports=[]

def png_frame(bmp,dest):
    with Image.open(bmp) as im: rgba=np.array(im.convert('RGBA'))
    alpha=rgba[:,:,3:4].astype(np.float32)
    rgba[:,:,:3]=np.clip(rgba[:,:,:3].astype(np.float32)*255/np.maximum(alpha,1),0,255).astype(np.uint8)
    out=Image.fromarray(rgba);out.save(dest)
    return rgba

# mouse-screen also fails on the shipped standard model: it assumes zero
# head breathing/idle at center. Keep its baseline evidence separately; use
# pointer reverse, hand bounds and rendered poses for this model's follow checks.
for index,scenario in enumerate(scenarios):
    case=run/(a.pose or scenario);case.mkdir();store=case/'storage';empty=case/'empty';empty.mkdir()
    # Click-through prevents unrelated real desktop clicks from starting a test-window drag.
    config=store/'config';config.mkdir(parents=True)
    settings={'format':'bongocat/settings','schemaVersion':1,'window':{'clickThrough':True,'alwaysOnTop':False},'rendering':{'ignorePointerInput':bool(a.pose)}}
    (config/'settings.json').write_text(json.dumps(settings))
    env=os.environ.copy();env['BONGO_CAT_TEST_INSTANCE_ID']=f'rtw-{os.getpid()}-{index}'
    args=[str(a.app),'--ci-smoke','--ci-ignore-global-input',f'--storage-root={store}',f'--nearby-root={empty}',f'--ci-live2d-scenario={scenario}',f'--ci-exit-ms={10000 if scenario=="idle" else 1600}']
    if (a.import_model or a.import_zip) and index==0:
        args.append('--ci-import='+str(ROOT/'delivery/Ruotengwu-Live2D.zip' if a.import_zip else model))
    else:
        shutil.copytree(model,store/'models'/model.name)
        args.append(f'--ci-model={model.name}')
    if a.pose:
        local=store/'models'/model.name
        mf=local/'Ruotengwu.model3.json';data=json.loads(mf.read_text())
        values={'ParamAngleX':0,'ParamAngleY':0,'ParamAngleZ':0,'ParamBodyAngleX':0,'ParamBodyAngleY':0,'ParamBodyAngleZ':0,'ParamEyeBallX':0,'ParamEyeBallY':0,'ParamEyeLOpen':1,'ParamEyeROpen':1,'ParamMouthOpenY':0,'ParamBreath':0,'ParamMouseX':0,'ParamMouseY':0,'CatParamLeftHandDown':0,'ParamMouseLeftDown':0,'ParamMouseRightDown':0}
        poses={'neutral':{},'blink':{'ParamEyeLOpen':0,'ParamEyeROpen':0},'halfblink':{'ParamEyeLOpen':.5,'ParamEyeROpen':.5},'left':{'ParamAngleX':-30,'ParamEyeBallX':-1},'right':{'ParamAngleX':30,'ParamEyeBallX':1},'up':{'ParamAngleY':30,'ParamEyeBallY':1},'down':{'ParamAngleY':-30,'ParamEyeBallY':-1},'tilt-left':{'ParamAngleZ':-12},'tilt-right':{'ParamAngleZ':12},'mouth':{'ParamMouthOpenY':1}}
        values.update(poses[a.pose]);curves=[{'Target':'Parameter','Id':k,'Segments':[0,v,0,2,v]} for k,v in values.items()]
        motion={'Version':3,'Meta':{'Duration':2,'Fps':30,'Loop':True,'AreBeziersRestricted':True,'CurveCount':len(curves),'TotalSegmentCount':len(curves),'TotalPointCount':len(curves)*2,'UserDataCount':0,'TotalUserDataSize':0},'Curves':curves}
        (local/'audit-pose.motion3.json').write_text(json.dumps(motion,indent=2)+'\n',encoding='utf-8')
        data['FileReferences']['Motions']={'CAT_motion':[{'File':'audit-pose.motion3.json','FadeInTime':0,'FadeOutTime':0}]}
        mf.write_text(json.dumps(data,indent=2)+'\n',encoding='utf-8');(case/'pose-fixture.json').write_text(json.dumps(values,indent=2))
    if scenario!='idle' and not a.pose:args.append('--ci-freeze-model')
    start=time.monotonic();seq=case/'frames';seq.mkdir();last=None;count=0
    info=subprocess.STARTUPINFO();info.dwFlags|=subprocess.STARTF_USESHOWWINDOW;info.wShowWindow=0
    with (case/'stdout.log').open('w') as stdout,(case/'stderr.log').open('w') as stderr:
        proc=subprocess.Popen(args,cwd=case,env=env,stdout=stdout,stderr=stderr,startupinfo=info)
        (case/'process.json').write_text(json.dumps({'pid':proc.pid,'args':args,'instance':env['BONGO_CAT_TEST_INSTANCE_ID']},indent=2))
        while proc.poll() is None:
            if time.monotonic()-start>60:
                proc.terminate();proc.wait(timeout=10)
                raise TimeoutError(f'Only isolated test process {proc.pid} was stopped; inspect {case}')
            frame=store/'state/frame.bmp'
            if scenario=='idle' and frame.is_file():
                try:
                    raw=frame.read_bytes();digest=hashlib.sha256(raw).digest()
                    if digest!=last:
                        png_frame(frame,seq/f'{count:03}.png');count+=1;last=digest
                except (OSError,ValueError):pass  # The app is writing its next framebuffer.
            time.sleep(.12)
    assert proc.returncode==0, f'{scenario}: native app exited {proc.returncode}; {case}'
    audit=store/'state/live2d-audit.txt';assert audit.is_file(),f'{scenario}: no native audit (single-instance exit is not success)'
    text=audit.read_text();fields=dict(line.split('=',1) for line in text.splitlines() if '=' in line)
    assert fields.get('renderer')=='cubism-native',fields
    expected='ruotengwu-live2d' if a.import_zip and index==0 else 'ruotengwu'
    assert fields.get('model','').lower()==expected,f'Wrong model loaded: {fields}'
    expected_moc=hashlib.sha256((model/'Ruotengwu.moc3').read_bytes()).digest()
    actual_mocs=list((store/'models'/fields['model']).rglob('*.moc3'))
    assert any(hashlib.sha256(p.read_bytes()).digest()==expected_moc for p in actual_mocs),'Runtime installed a different MOC3'
    assert fields.get('assertions')=='passed' and fields.get('operation')=='accepted',fields
    image=png_frame(store/'state/frame.bmp',case/'frame.png')
    assert np.count_nonzero(image[:,:,3]>0)>20000,f'{scenario}: blank or tiny model'
    reports.append({'scenario':scenario,'exit':proc.returncode,'renderer':fields['renderer'],'model':fields['model'],'audit':str(audit),'frame':str(case/'frame.png'),'idle_frames':count})
    (run/'summary.json').write_text(json.dumps(reports,indent=2))
    print('PASS native routing:',scenario,'frames',count,flush=True)
print('Inspect captures before claiming visual correctness:',run,flush=True)




