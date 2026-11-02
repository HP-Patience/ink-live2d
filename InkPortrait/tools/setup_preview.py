"""Prepare an ignored local SDK copy; no proprietary Cubism Core is committed."""
from pathlib import Path
import argparse, shutil
ROOT=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--sdk',type=Path,required=True,help='Extracted official CubismSdkForWeb-5-r.5 directory')
p.add_argument('--model',type=Path,default=ROOT/'models/InkPortrait')
a=p.parse_args(); src=a.sdk.resolve(); dst=ROOT/'workspace/sdk'
for required in ['Core/live2dcubismcore.js','Framework/src/live2dcubismframework.ts','Samples/TypeScript/Demo/package.json']:
    if not (src/required).is_file():p.error('Not a complete official SDK directory: '+required)
if src==dst.resolve() or dst.resolve().is_relative_to(src):p.error('Use a separate extracted SDK directory.')
if not (a.model/'InkPortrait.model3.json').is_file():p.error('Model manifest not found.')
shutil.copytree(src,dst,dirs_exist_ok=True,ignore=shutil.ignore_patterns('.git','node_modules','dist','public','.vscode'))
shutil.copytree(ROOT/'preview/overrides',dst,dirs_exist_ok=True)
demo=dst/'Samples/TypeScript/Demo'
for origin,target in [(dst/'Core',demo/'public/Core'),(dst/'Framework/Shaders',demo/'public/Framework/Shaders'),(dst/'Samples/Resources',demo/'public/Resources')]:
    shutil.copytree(origin,target,dirs_exist_ok=True)
# Copy the portrait last. npm start/build intentionally do NOT run the upstream resource overwrite.
shutil.copytree(a.model,demo/'public/Resources/InkPortrait',dirs_exist_ok=True)
print('Next:\n  cd "'+str(demo)+'"\n  npm ci\n  npm test\n  npm start')
print('Preview: http://127.0.0.1:4174/ ; keep the server running for browser tests.')
