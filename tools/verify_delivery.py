"""Offline integrity, privacy and link checks for the repository deliverables."""
from pathlib import Path
import hashlib,json,re
ROOT=Path(__file__).resolve().parents[1]
manifest=json.loads((ROOT/'validation/SHA256.json').read_text())
for name,expected in manifest.items():
    path=(ROOT/name).resolve()
    assert path.is_relative_to(ROOT.resolve()) and path.is_file(),name
    assert hashlib.sha256(path.read_bytes()).hexdigest()==expected,name
model=ROOT/'models/InkPortrait'; data=json.loads((model/'InkPortrait.model3.json').read_text())['FileReferences']
refs=[data['Moc'],data['Physics'],data['DisplayInfo'],*data['Textures']]+[m['File'] for group in data['Motions'].values() for m in group]
for ref in refs:
    path=(model/ref).resolve(); assert path.is_relative_to(model.resolve()) and path.is_file(),ref
assert (model/data['Moc']).read_bytes()[:4]==b'MOC3'
report=json.loads((ROOT/'validation/v6/runtime.json').read_text())
assert report['pass'] and len(report['parameterTests'])==36 and report['v6']['pass']
assert report['drawables']==23 and report['vertices']==4585
for file in ROOT.rglob('*'):
    if not file.is_file() or any(p in file.relative_to(ROOT).parts for p in ['.git','vendor','workspace','node_modules']):continue
    assert file.stat().st_size<100_000_000,file
    if file.suffix not in ['.py','.js','.ts','.mjs','.md','.json','.txt','.html','.patch','.log']:continue
    text=file.read_text(encoding='utf-8-sig')
    assert not re.search(r'[A-Z]:[/\\]Users[/\\]',text),file
    assert not re.search(r'(?:gh[pousr]_|github_pat_)[A-Za-z0-9_]{25,}',text),file
    if file.suffix=='.md' and 'licenses' not in file.relative_to(ROOT).parts:
        for target in re.findall(r'!?\[[^\]]*\]\(([^)]+)\)',text):
            if '://' in target or target.startswith('#'):continue
            target=target.split('#')[0]
            assert (file.parent/target).exists(),(file,target)
print('PASS: checksums, model references, v6 QA evidence, relative links, privacy and file sizes')
