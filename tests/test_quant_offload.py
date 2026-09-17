import sys
from pathlib import Path
import torch,bitsandbytes as b
sys.path.insert(0,str((Path(__file__).resolve().parents[1]/'vendor/see-through/inference/scripts')))
from inference_psd_quantized import sync_quant_state
m=b.nn.Linear4bit(128,128,compute_dtype=torch.bfloat16,quant_type='nf4').cuda()
x=torch.randn(2,128,device='cuda',dtype=torch.bfloat16)
y=m(x)
m.weight.quant_state.to('cpu')
assert m.weight.quant_state.absmax.device.type=='cpu'
m.register_forward_pre_hook(sync_quant_state)
y2=m(x)
assert m.weight.quant_state.absmax.device.type=='cuda'
assert torch.allclose(y,y2), (y-y2).abs().max()
print('Quantized offload state synchronization: PASS')
