from pathlib import Path
import hashlib,json,zipfile,shutil
r=Path(r'E:\BongoCat\artifacts\ruotengwu-live2d');e=r/'validation/final-evidence';d=r/'delivery'
# Update delivery model package after source/runtime changes.
# package_model.py is the single source of truth for model references and key assets.
files=[p for p in d.iterdir() if p.is_file() and p.name not in {'Ruotengwu-Source.zip','SHA256SUMS.txt'}]
# Source archive: current editable layers + source scripts + curated evidence only.
with zipfile.ZipFile(d/'Ruotengwu-Source.zip','w',zipfile.ZIP_DEFLATED) as z:
    for folder in [r/'source',r/'tools',r/'validation/final-evidence']:
        for p in folder.rglob('*'):
            if p.is_file() and '__pycache__' not in p.parts:z.write(p,Path('Ruotengwu-Source')/p.relative_to(r))
    for p in [r/'validation/input-v2-complete.json',r/'validation/pointer-perspective-preservation.json',r/'validation/orientation-v3-install/installation.json']:
        if p.is_file():z.write(p,Path('Ruotengwu-Source')/p.relative_to(r))
    for name in ['使用说明.md','VERIFICATION.md']:z.write(d/name,Path('Ruotengwu-Source')/name)
with zipfile.ZipFile(d/'Ruotengwu-Source.zip') as z:assert z.testzip() is None
for name in ['Ruotengwu-Live2D.zip','Ruotengwu-Source.zip']:
    with zipfile.ZipFile(d/name) as z:assert z.testzip() is None
files=[p for p in d.iterdir() if p.is_file() and p.name!='SHA256SUMS.txt']
(d/'SHA256SUMS.txt').write_text('\n'.join(hashlib.sha256(p.read_bytes()).hexdigest()+'  '+p.name for p in files)+'\n',encoding='utf-8')
print('Updated blue-highlight model/source ZIPs and checksums')
