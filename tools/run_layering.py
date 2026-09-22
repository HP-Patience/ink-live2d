"""Run the saved upstream stages separately so depth download need not block body/head inference."""
from pathlib import Path
from types import SimpleNamespace
import argparse, importlib.util, json, time
ROOT=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser();p.add_argument('stage',choices=['layer','depth']);a=p.parse_args()
script=ROOT/'workspace/see-through/inference/scripts/inference_psd_quantized.py'
spec=importlib.util.spec_from_file_location('seethrough_quantized',script)
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
args=SimpleNamespace(quant_mode='nf4',cpu_offload=False,group_offload=True,
    repo_id_layerdiff=str(ROOT/'workspace/weights/seethroughv0.0.2_layerdiff3d_nf4'),
    repo_id_depth=str(ROOT/'workspace/weights/seethroughv0.0.1_marigold_nf4'))
source=str(ROOT/'source/inference-input.png'); output=str(ROOT/'workspace/inference-output')
saved=Path(output)/'inference-input'
m.seed_everything(42);m.torch.cuda.reset_peak_memory_stats();started=time.monotonic()
if a.stage=='layer':
    pipeline=m.build_layerdiff_pipeline(args)
    m.run_layerdiff(pipeline,source,output,42,30,1280)
    assert all((saved/(n+'.png')).is_file() for n in ['face','eyewear','irides','front hair','back hair','src_img']), 'Incomplete body/head pass'
else:
    assert (saved/'face.png').is_file(), 'Run body/head stage first'
    pipeline=m.build_marigold_pipeline(args)
    m.run_marigold(pipeline,source,output,42,resolution_depth=768)
    del pipeline;m.torch.cuda.empty_cache()
    m.further_extr(str(saved),rotate=False,save_to_psd=True,tblr_split=True)
    assert saved.with_suffix('.psd').is_file(), 'PSD assembly did not produce a PSD'
stats={'stage':a.stage,'seconds':time.monotonic()-started,'peak_cuda_bytes':m.torch.cuda.max_memory_allocated(),'seed':42}
(ROOT/f'validation/inference-{a.stage}-complete.json').write_text(json.dumps(stats,indent=2))
print('COMPLETE',stats,flush=True)

