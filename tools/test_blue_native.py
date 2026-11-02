"""Regression: actual Windows keyboard input into an owned blank sink, observed in BongoCat.
Never inject into another application: check foreground identity before every key event.
The test model/storage are isolated; restore pointer/focus and release owned keys on exit.
"""
from pathlib import Path
import ctypes as C
from ctypes import wintypes as W
import os,json,shutil,subprocess,time,hashlib,argparse
import numpy as np,cv2
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[1]
parser=argparse.ArgumentParser();parser.add_argument("--app",default=r"C:\Users\wjx\AppData\Local\Programs\BongoCat\BongoCat.exe");args_cli=parser.parse_args()
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
run=Path('E:/BongoCat/build-hl-tests')/time.strftime('%Y%m%d-%H%M%S');run.mkdir(parents=True);store=run/'storage';(store/'models').mkdir(parents=True);(run/'empty').mkdir()
model=ROOT/'delivery/InkKeys'
shutil.copytree(model,store/'models/InkKeys')

(store/'config').mkdir();(store/'config/settings.json').write_text(json.dumps({'format':'bongocat/settings','schemaVersion':1,'window':{'clickThrough':True,'alwaysOnTop':False},'rendering':{'centerPointerTracking':False}}))
layout=json.loads((ROOT/'source/key-layout.json').read_text());frames=run/'frames';frames.mkdir();held=set();sink=None;proc=None
info=subprocess.STARTUPINFO();info.dwFlags|=subprocess.STARTF_USESHOWWINDOW;info.wShowWindow=0
env=os.environ.copy();env['BONGO_CAT_TEST_INSTANCE_ID']='keys-'+str(os.getpid())
args=[args_cli.app,'--ci-smoke','--ci-exit-ms=16000',f'--storage-root={store}',f'--nearby-root={run/"empty"}','--ci-model=InkKeys','--ci-live2d-scenario=idle']
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
    audit=(store/'state/live2d-audit.txt').read_text()
    assert 'model=InkKeys\n' in audit and 'renderer=cubism-native' in audit, 'Wrong runtime/model loaded'
    # A blank, off-screen STATIC window safely receives our synthetic keys.
    sink=U.CreateWindowExW(0,'STATIC','InkKeys input regression sink',0x80000000,-1600,-1600,120,70,None,None,None,None)
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
    send(162);pump(.25);capture('ctrl')
    send(65);pump(.25);capture('ctrl-a')
    send(65,False);pump(.25);capture('ctrl-after-a-release')
    send(162,False);pump(.25);capture('released-both')
    send(65);send(68);pump(.25);capture('a-d')
    send(65,False);pump(.25);capture('d-after-a-release')
    send(68,False);pump(.25);capture('released-again')
    # Mouse down/up are delivered only over the owned blank popup, never another app.
    U.SetWindowPos.argtypes=[W.HWND,W.HWND,C.c_int,C.c_int,C.c_int,C.c_int,W.UINT]
    U.SetWindowPos(sink,None,50,50,180,130,0x0014)
    U.SetCursorPos(130,115);pump(.25)
    def button(flag):
        assert U.GetForegroundWindow()==sink,'Lost owned mouse test focus'
        event=INPUT(type=0);event.mi=MOUSEINPUT(0,0,0,flag,0,0)
        assert U.SendInput(1,C.byref(event),C.sizeof(event))==1
    button(2);pump(.25);capture('left-down')
    button(8);pump(.25);capture('both-down')
    button(4);pump(.25);capture('right-only')
    button(16);pump(.25);capture('mouse-released')
    # Clean test-owned sink promptly; allow the native process to finish normally.
    U.DestroyWindow(sink);sink=None
    U.SetCursorPos(oldpoint.x,oldpoint.y)
    if oldfocus:U.SetForegroundWindow(oldfocus)
    proc.wait(timeout=40);assert proc.returncode==0,proc.returncode
finally:
    release=INPUT(type=0);release.mi=MOUSEINPUT(0,0,0,4|16,0,0);U.SendInput(1,C.byref(release),C.sizeof(release))
    for vk,ext in list(held):send(vk,False,ext,cleanup=True)
    if sink:U.DestroyWindow(sink)
    U.SetCursorPos(oldpoint.x,oldpoint.y)
    if oldfocus:U.SetForegroundWindow(oldfocus)
    if proc and proc.poll() is None:proc.terminate();proc.wait(timeout=10)
    log.close();out.close()

# Check actual blue pixels, not merely parameter/state declarations.
def blue(name):
    a=np.array(Image.open(frames/(name+'.png')).convert('RGBA'));rgb=a[:,:,:3].astype(int)
    return (rgb[:,:,2]>rgb[:,:,0]+30)&(rgb[:,:,2]>rgb[:,:,1]+15)&(rgb[:,:,2]>140)&(a[:,:,3]>100)
masks={n:blue(n) for n in ['released','ctrl','ctrl-a','ctrl-after-a-release','released-both','a-d','d-after-a-release','released-again','left-down','both-down','right-only','mouse-released']}
assert not masks['released'].any() and not masks['released-both'].any() and not masks['released-again'].any(),'Keyboard blue stuck after release'
assert masks['ctrl'].sum()>15,'Ctrl did not highlight'
assert (masks['ctrl-a']&masks['ctrl']).sum()>10,'Ctrl lost blue while A held'
assert (masks['ctrl-a']&~masks['ctrl']).sum()>5,'A did not independently highlight'
assert np.logical_xor(masks['ctrl'],masks['ctrl-after-a-release']).sum()<6,'Releasing A did not leave only Ctrl'
assert masks['a-d'].sum()>masks['d-after-a-release'].sum()+5,'A and D did not retain independent states'
assert masks['left-down'].sum()>60 and masks['right-only'].sum()>60,'Mouse button highlight missing'
assert (masks['both-down']&masks['left-down']).sum()>40 and (masks['both-down']&masks['right-only']).sum()>40,'Both mouse buttons must remain blue together'
assert not masks['mouse-released'].any(),'Mouse blue stuck after release'
result={'app':args_cli.app,'app_sha256':hashlib.sha256(Path(args_cli.app).read_bytes()).hexdigest(),'model_sha256':hashlib.sha256((model/'InkKeys.moc3').read_bytes()).hexdigest(),'blue_pixels':{n:int(m.sum()) for n,m in masks.items()},'ctrl_a_partial_release':True,'mouse_independent_release':True,'run':str(run)}
(run/'summary.json').write_text(json.dumps(result,indent=2));(ROOT/'validation/latest-blue-native.txt').write_text(str(run));print(json.dumps(result,indent=2))
board=Image.new('RGB',(1100,780),(235,238,244));d=ImageDraw.Draw(board)
for i,n in enumerate(['ctrl','ctrl-a','ctrl-after-a-release','left-down','both-down','right-only']):
    im=Image.open(frames/(n+'.png')).convert('RGBA');im.thumbnail((355,335));x=i%3*365;y=i//3*390+25
    board.paste(im,(x,y),im);d.text((x+8,y-18),n,fill='black')
board.save(run/'blue-contact.png')



