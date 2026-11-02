from pathlib import Path
from huggingface_hub import HfApi, snapshot_download
import json
root=Path(r'E:\BongoCat\artifacts\ink-keys-live2d')
records=[]
for name in ('seethroughv0.0.2_layerdiff3d_nf4','seethroughv0.0.1_marigold_nf4'):
    repo='24yearsold/'+name
    info=HfApi().model_info(repo,files_metadata=True)
    size=sum(f.size or 0 for f in info.siblings)
    print(repo,info.sha,round(size/1024**3,2),'GiB',flush=True)
    records.append({'repo':repo,'revision':info.sha,'bytes':size})
    (root/'validation/weights.json').write_text(json.dumps(records,indent=2))
    snapshot_download(repo,revision=info.sha,local_dir=root/'workspace/weights'/name,max_workers=4)
    print('COMPLETE',name,flush=True)
