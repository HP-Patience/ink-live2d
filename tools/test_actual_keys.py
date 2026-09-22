"""Regression: actual Windows keyboard input into an owned blank sink, observed in BongoCat.
Never inject into another application: check foreground identity before every key event.
The test model/storage are isolated; restore pointer/focus and release owned keys on exit.
"""
from pathlib import Path
import ctypes as C
from ctypes import wintypes as W
import os,json,shutil,subprocess,time,hashlib
import numpy as np,cv2
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[1]
U=C.WinDLL('user32',use_last_error=True);K=C.WinDLL('kernel32',use_last_error=True)
class MOUSEINPUT(C.Structure): _fields_=[('dx',W.LONG),('dy',W.LONG),('mouseData',W.DWORD),('dwFlags',W.DWORD),('time',W.DWORD),('dwExtraInfo',C.c_size_t)]
class KEYBDINPUT(C.Structure): _fields_=[('wVk',W.WORD),('wScan',W.WORD),('dwFlags',W.DWORD),('time',W.DWORD),('dwExtraInfo',C.c_size_t)]
class HARDWAREINPUT(C.Structure): _fields_=[('uMsg',W.DWORD),('wParamL',W.WORD),('wParamH',W.WORD)]
class UNION(C.Union): _fields_=[('mi',MOUSEINPUT),('ki',KEYBDINPUT),('hi',HARDWAREINPUT)]
class INPUT(C.Structure): _anonymous_=('u',);_fields_=[('type',W.DWORD),('u',UNION)]
assert C.sizeof(INPUT)==40,'Expected x64 INPUT layout'
U.GetForegroundWindow.restype=W.HWND
U.CreateWindowExW.argtypes=[W.DWORD,W.LPCWSTR,W.LPCWSTR,W.DWORD,C.c_int,C.c_int,C.c_int,C.c_int,W.HWND,W.HMENU,W.HINSTANCE,W.LPVOID];U.CreateWindowExW.restype=W.HWND
U.SetForegroundWindow.argtypes=[W.HWND];U.DestroyWindow.argtypes=[W.HWND];U.ShowWindow.argtypes=[W.HWND,C.c_int]
U.GetWindowThreadProcessId.argtypes=[W.HWND,C.POINTER(W.DWORD)];U.GetWindowThreadProcessId.restype=W.DWORD
U.AttachThreadInput.argtypes=[W.DWORD,W.DWORD,W.BOOL];U.BringWindowToTop.argtypes=[W.HWND];U.SetActiveWindow.argtypes=[W.HWND]
U.SendInput.argtypes=[W.UINT,C.POINTER(INPUT),C.c_int];U.SendInput.restype=W.UINT
U.PostMessageW.argtypes=[W.HWND,W.UINT,W.WPARAM,W.LPARAM];U.PeekMessageW.argtypes=[C.POINTER(W.MSG),W.HWND,W.UINT,W.UINT,W.UINT]
oldfocus=U.GetForegroundWindow();oldpoint=W.POINT();U.GetCursorPos(C.byref(oldpoint))
run=ROOT/'validation/input-position-native'/time.strftime('%Y%m%d-%H%M%S');run.mkdir(parents=True);store=run/'storage';(store/'models').mkdir(parents=True);(run/'empty').mkdir()
model=ROOT/'delivery/Ruotengwu'
(store/'config').mkdir();(store/'config/settings.json').write_text(json.dumps({'format':'bongocat/settings','schemaVersion':1,'window':{'clickThrough':True,'alwaysOnTop':False},'rendering':{'centerPointerTracking':False}}))
layout=json.loads((ROOT/'source/key-layout.json').read_text());frames=run/'frames';frames.mkdir();held=set();sink=None;proc=None
info=subprocess.STARTUPINFO();info.dwFlags|=subprocess.STARTF_USESHOWWINDOW;info.wShowWindow=0
env=os.environ.copy();env['BONGO_CAT_TEST_INSTANCE_ID']='keys-'+str(os.getpid())
args=[r'C:\Users\wjx\AppData\Local\Programs\BongoCat\BongoCat.exe','--ci-smoke','--ci-exit-ms=35000',f'--storage-root={store}',f'--nearby-root={run/"empty"}',f'--ci-import={model}','--ci-live2d-scenario=idle']
log=(run/'runtime.log').open('w');out=(run/'stdout.log').open('w')
def pump(seconds):
    end=time.monotonic()+seconds;msg=W.MSG()
    while time.monotonic()<end:
        while U.PeekMessageW(C.byref(msg),None,0,0,1):U.TranslateMessage(C.byref(msg));U.DispatchMessageW(C.byref(msg))
        time.sleep(.015)
def send(vk,down=True,extended=False,cleanup=False):
    if not cleanup:assert U.GetForegroundWindow()==sink,'Focus left our test sink; refusing to type into another app'
    i=INPUT(type=1)
    if vk in (160,161):i.ki=KEYBDINPUT(0,0x2a if vk==160 else 0x36,8|(0 if down else 2),0,0)
    else:i.ki=KEYBDINPUT(vk,0,(0 if down else 2)|(1 if extended else 0),0,0)
    assert U.SendInput(1,C.byref(i),C.sizeof(i))==1,'SendInput failed'
    if down:held.add((vk,extended))
    else:held.discard((vk,extended))
def capture(name):
    path=store/'state/frame.bmp'
    for _ in range(20):
        try:
            with Image.open(path) as im:a=np.array(im.convert('RGBA'))
            alpha=a[:,:,3:4].astype(float);a[:,:,:3]=np.clip(a[:,:,:3]*255./np.maximum(alpha,1),0,255).astype('uint8')
            Image.fromarray(a).save(frames/(name+'.png'));return a
        except (OSError,ValueError):pump(.04)
    raise AssertionError('No stable framebuffer')
try:
    proc=subprocess.Popen(args,cwd=run,env=env,startupinfo=info,stdout=out,stderr=log)
    (run/'process.json').write_text(json.dumps({'pid':proc.pid,'args':args},indent=2))
    start=time.monotonic()
    while not (store/'state/live2d-audit.txt').exists():
        assert proc.poll() is None,'BongoCat exited before loading';assert time.monotonic()-start<15,'Startup timed out';pump(.1)
    # A blank, off-screen STATIC window safely receives our synthetic keys.
    sink=U.CreateWindowExW(0,'STATIC','Ruotengwu input regression sink',0x80000000,-1600,-1600,120,70,None,None,None,None)
    assert sink,'Could not create owned input sink'
    U.ShowWindow(sink,5)
    foreground_thread=U.GetWindowThreadProcessId(U.GetForegroundWindow(),None);own_thread=K.GetCurrentThreadId()
    attached=bool(U.AttachThreadInput(own_thread,foreground_thread,True)) if own_thread!=foreground_thread else False
    try:U.BringWindowToTop(sink);U.SetForegroundWindow(sink);U.SetActiveWindow(sink)
    finally:
        if attached:U.AttachThreadInput(own_thread,foreground_thread,False)
    pump(.25)
    assert U.GetForegroundWindow()==sink,'Cannot acquire test focus safely'
    U.SetCursorPos(960,540);pump(.3);capture('released')
    cases=[('KeyA',65,False),('KeyD',68,False),('KeyJ',74,False),('KeyP',80,False),('KeyZ',90,False),('Space',32,False),('Return',13,False),('UpArrow',38,True),('Kp1',97,False),('ShiftLeft',160,False),('ShiftRight',161,False),('ControlLeft',162,False),('ControlRight',163,True)]
    for name,vk,extended in cases:
        send(vk,True,extended);pump(.24);capture(name);send(vk,False,extended);pump(.18);capture(name+'-up')
    send(65);pump(.2);capture('chord-A');send(68);pump(.2);capture('chord-A-D');send(68,False);pump(.2);capture('chord-back-to-A');send(65,False);pump(.2);capture('chord-released')
    w=U.GetSystemMetrics(0);h=U.GetSystemMetrics(1)
    for name,x,y in [('mouse-left',1,h//2),('mouse-right',w-2,h//2),('mouse-top',w//2,1),('mouse-bottom',w//2,h-2)]:
        U.SetCursorPos(x,y);pump(.5);capture(name)
    # Clean test-owned sink promptly; allow the native process to finish normally.
    U.DestroyWindow(sink);sink=None
    U.SetCursorPos(oldpoint.x,oldpoint.y)
    if oldfocus:U.SetForegroundWindow(oldfocus)
    proc.wait(timeout=40);assert proc.returncode==0,proc.returncode
finally:
    for vk,ext in list(held):send(vk,False,ext,cleanup=True)
    if sink:U.DestroyWindow(sink)
    U.SetCursorPos(oldpoint.x,oldpoint.y)
    if oldfocus:U.SetForegroundWindow(oldfocus)
    if proc and proc.poll() is None:proc.terminate();proc.wait(timeout=10)
    log.close();out.close()
# Hand skin makes the actual landing position measurable without trusting a key label.
def skin_centroid(a):
    hh,ww=a.shape[:2];yy,xx=np.mgrid[:hh,:ww];rgb=a[:,:,:3].astype(int)
    mask=(rgb[:,:,0]>218)&(rgb[:,:,1]>205)&(rgb[:,:,0]-rgb[:,:,1]>4)&(a[:,:,3]>200)&(yy>hh*.68)&(xx>ww*.37)
    y,x=np.where(mask);assert len(x)>12,'Typing hand absent from native render'
    return [float(x.mean()),float(y.mean())]
centers={name:skin_centroid(np.array(Image.open(frames/(name+'.png')).convert('RGBA'))) for name,_,_ in cases}
assert centers['KeyA'][0]-3>centers['KeyD'][0]>centers['KeyJ'][0]+3,centers
assert centers['KeyP'][0]>centers['Return'][0],centers
assert centers['KeyZ'][1]>centers['Space'][1]+3,centers
assert abs(centers['ControlLeft'][0]-centers['ControlRight'][0])>30,centers
assert abs(centers['ShiftLeft'][0]-centers['ShiftRight'][0])>30,centers
for suffix in ['KeyA-up','KeyD-up','KeyJ-up','chord-released']:
    rest=skin_centroid(np.array(Image.open(frames/(suffix+'.png')).convert('RGBA')))
    assert 200<rest[0]<285 and rest[1]<290, ('Resting hand did not return',suffix,rest)
a=skin_centroid(np.array(Image.open(frames/'chord-A.png')));b=skin_centroid(np.array(Image.open(frames/'chord-A-D.png')))
assert b[0]<a[0]-8,'Latest pressed key did not take priority on character-facing keyboard'
# Stock 1.11.0 keeps one pose per keyboard hand; releasing the newest key
# returns to rest even if an older key remains held. Record, do not fake a pass
# for a skin-level feature the native runtime cannot express.
rest=skin_centroid(np.array(Image.open(frames/'chord-released.png')))
released=skin_centroid(np.array(Image.open(frames/'chord-back-to-A.png')))
assert np.linalg.norm(np.array(rest)-released)<2,'Latest-key release left a stuck overlay'
def mouse_center(name):
    a=np.array(Image.open(frames/(name+'.png')).convert('RGBA'));hh,ww=a.shape[:2];yy,xx=np.mgrid[:hh,:ww];rgb=a[:,:,:3].astype(int)
    mask=(rgb[:,:,0]>215)&(rgb[:,:,1]>200)&(rgb[:,:,0]-rgb[:,:,1]>4)&(a[:,:,3]>200)&(yy>hh*.67)&(xx<ww*.43)
    n,labels,stats,centroids=cv2.connectedComponentsWithStats(mask.astype('uint8'),8)
    assert n>1,'Mouse palm missing';index=1+np.argmax(stats[1:,cv2.CC_STAT_AREA]);return centroids[index].tolist()
mouse={n:mouse_center(n) for n in ['mouse-left','mouse-right','mouse-top','mouse-bottom']}
travel_x=mouse['mouse-right'][0]-mouse['mouse-left'][0];travel_y=mouse['mouse-bottom'][1]-mouse['mouse-top'][1]
assert travel_x < -35 and travel_y < -13,('Facing-character mouse perspective/range is wrong',travel_x,travel_y)

summary={'actual_input':'Win32 SendInput directed only to owned blank window; BongoCat Raw Input','centroids':centers,'native_run':str(run),'mouse_centroids':mouse,'mouse_travel_pixels':[travel_x,travel_y],'chord_behavior':'Most recent key wins; releasing it returns to rest (stock BongoCat 1.11.0)' }
(run/'summary.json').write_text(json.dumps(summary,indent=2));(ROOT/'validation/latest-input-native.txt').write_text(str(run));print(json.dumps(summary,indent=2))
board=Image.new('RGB',(1440,960),(234,237,242));draw=ImageDraw.Draw(board)
for i,name in enumerate(['KeyA','KeyD','KeyJ','KeyP','Space','Return','ShiftLeft','ShiftRight','UpArrow']):
    im=Image.open(frames/(name+'.png')).convert('RGBA');im.thumbnail((450,300));x=i%3*480;y=i//3*320+18;board.paste(im,(x,y),im);draw.text((x+10,y-15),name,fill='black')
board.save(run/'native-key-contact.png')
