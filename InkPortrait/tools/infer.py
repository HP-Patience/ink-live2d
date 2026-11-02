"""Optional GPU re-inference. Not required to rebuild the delivered v6 model."""
from pathlib import Path
import argparse, subprocess, sys
ROOT=Path(__file__).resolve().parents[1]; repo=ROOT/'vendor/see-through'
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--input',type=Path,default=ROOT/'source/original.png')
a=p.parse_args()
if not a.input.is_file():p.error('Input image does not exist.')
patch=ROOT/'patches/see-through-nf4.patch'
if subprocess.run(['git','-C',str(repo),'apply','--reverse','--check',str(patch)],capture_output=True).returncode:
    subprocess.run(['git','-C',str(repo),'apply','--check',str(patch)],check=True)
    subprocess.run(['git','-C',str(repo),'apply',str(patch)],check=True)
from huggingface_hub import snapshot_download
models=[]
for name in ['seethroughv0.0.2_layerdiff3d_nf4','seethroughv0.0.1_marigold_nf4']:
    models.append(snapshot_download('24yearsold/'+name,local_dir=ROOT/'workspace/weights'/name))
subprocess.run([sys.executable,'inference/scripts/inference_psd_quantized.py','--srcp',str(a.input.resolve()),'--save_dir',str(ROOT/'workspace/new-inference'),'--resolution','1280','--resolution_depth','768','--save_to_psd','--tblr_split','--repo_id_layerdiff',models[0],'--repo_id_depth',models[1]],cwd=repo,check=True)
print('New output: workspace/new-inference. Existing committed source layers were not overwritten.')
