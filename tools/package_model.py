"""Package genuine PSD2Live exports with the native BongoCat input adapter."""
from pathlib import Path
import hashlib, json, shutil, zipfile
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
export=ROOT/'workspace/export'; out=ROOT/'delivery/Ruotengwu'
manifest=export/'Ruotengwu.model3.json'
assert manifest.is_file(), 'Export the real model before packaging'
data=json.loads(manifest.read_text(encoding='utf-8'));refs=data['FileReferences']
assets=[refs['Moc'],*refs['Textures'],refs['Physics'],refs['DisplayInfo']]
assets += [m['File'] for group in refs.get('Motions',{}).values() for m in group]
assets += [m['File'] for m in refs.get('Expressions',[])]
assert (export/refs['Moc']).read_bytes()[:4]==b'MOC3', 'Refusing to package a placeholder model'
out.mkdir(parents=True,exist_ok=True)
for name in set(assets+['Ruotengwu.model3.json']):
    src=(export/name).resolve(); dst=(out/name).resolve()
    assert src.is_relative_to(export.resolve()) and dst.is_relative_to(out.resolve()), f'Unsafe asset path: {name}'
    assert src.is_file(), f'Missing exported file: {name}'
    dst.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(src,dst)
shutil.copy2(export/'Ruotengwu.cmo3',ROOT/'source/Ruotengwu.cmo3')
(out/'.bongo-cat-mode').write_text('standard',encoding='utf-8')
# BongoCat chooses native overlays by the actual key name. Each contains that
# key's highlight plus a connected typing arm; Live2D hides its resting arm.
layout=json.loads((ROOT/'source/key-layout.json').read_text(encoding='utf-8'))
keydir=out/'resources/left-keys';keydir.mkdir(parents=True,exist_ok=True)
canonical=json.loads((ROOT/'source/key-order.json').read_text())
# Import groups sided modifiers by repeated VK code. Extra aliases would steal
# the right-side mapping, so ship exactly one file per physical key.
for stale in keydir.glob('*.png'):
    assert stale.resolve().parent==keydir.resolve()
    if stale.stem not in canonical:stale.unlink()
for key in canonical:
    src=ROOT/'source/key-poses'/(key+'.png')
    assert src.is_file(), f'Missing physical-key pose: {key}'
    shutil.copy2(src,keydir/src.name)
Image.open(ROOT/'source/neutral-composite.png').save(out/'resources/cover.png')
Image.new('RGBA',(1280,1280),(0,0,0,0)).save(out/'resources/background.png')
shutil.copy2(ROOT/'source/key-layout.json',out/'key-layout.json')
readme='''# 若腾武 / Ruotengwu Live2D 桌宠

将本文件夹或 ZIP 导入 BongoCat 1.11.0，选择 Ruotengwu。也可以把整个 Ruotengwu 文件夹放到用户模型目录，再重新扫描模型。

形象：黑发、方框眼镜、黑高领、薄键鼠台。文件包含真实 MOC3 网格及表情/物理相关参数，不是 GIF 或静态图片桌宠。

- 鼠标移动：头部、视线及鼠标手跟随。
- 鼠标左右键：鼠标手按压。
- 键盘：按实际 QWERTY 键位移动键盘手，并高亮对应键帽；松开归位。
- 空闲：眨眼、呼吸、头发轻微物理。

resources/left-keys 内是逐键绘制的手部落点和高亮，不再是通用透明触发图。头部、表情、呼吸、鼠标手仍由真正的 Live2D 网格驱动；键盘手使用 BongoCat 原生逐键覆盖层，与清宵这类皮肤的输入方式一致。不要删除该目录。

软件输入命名限制：BongoCat 1.11.0 把主 Enter 和数字小键盘 Enter 都报告为 Return，两侧 Windows 键都报告为 Meta，皮肤不能区分它们；F13–F24 使用功能行对应位置并显示独立标签。其他标准键按各自位置映射。

原画属于本次用户确认的生成形象；包内不包含用于风格对照的其他作者图片或模型。请勿据此推断任何第三方素材的商用授权。

运行验证记录随制作资料提供。此说明本身不代表已通过运行验证。
'''
(out/'README.md').write_text(readme,encoding='utf-8')
files={p.relative_to(out).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in out.rglob('*') if p.is_file()}
(ROOT/'validation/package-sha256.json').write_text(json.dumps(files,indent=2),encoding='utf-8')
zip_path=ROOT/'delivery/Ruotengwu-Live2D.zip'
with zipfile.ZipFile(zip_path,'w',zipfile.ZIP_DEFLATED) as z:
    for p in out.rglob('*'):
        if p.is_file():z.write(p,p.relative_to(out.parent))
print('Packaged:',zip_path,'(native tests still required)')

