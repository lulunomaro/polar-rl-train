"""Synthetic frozen quantized linear/latent gradient proof, no actual model read."""
from pathlib import Path
import hashlib,json,time,traceback
import numpy as np
import torch
import torch.nn.functional as F
from q8_frozen_linear_candidate_v1 import FrozenQ8Linear,dequantize_q8_0
Q=Path(__file__).resolve().parent;R=Q/'reports';torch.set_num_threads(2)
def put(n,v):
 with (R/n).open('x',encoding='utf8') as f:json.dump(v,f,indent=2)
try:
    gen=np.random.default_rng(20261025);shape=(48,64)
    w=gen.standard_normal(shape).astype('<f4').reshape(-1,32)*.1
    scales=(np.max(abs(w),axis=1)/127).astype('<f2')
    values=np.clip(np.round(w/scales.astype(np.float32)[:,None]),-127,127).astype(np.int8)
    packed=np.concatenate([scales.view(np.uint8).reshape(-1,2),values.view(np.uint8)],axis=1)
    blocks=torch.from_numpy(packed.copy());module=FrozenQ8Linear(blocks,shape)
    dense=dequantize_q8_0(blocks,shape,torch.float32)
    cases=[]
    for dims in [(2,64),(1,7,64)]:
        x=torch.from_numpy(gen.standard_normal(dims).astype(np.float32)).requires_grad_();reference=x.detach().clone().requires_grad_()
        y=module(x);r=F.linear(reference,dense)
        target=torch.from_numpy(gen.standard_normal(tuple(y.shape)).astype(np.float32));loss=((y-target)**2).mean();ref_loss=((r-target)**2).mean()
        loss.backward();ref_loss.backward();assert torch.equal(y,r) and torch.equal(x.grad,reference.grad)
        cases.append(dict(shape=dims,forward_and_input_gradient_equal_to_dense_dequant=True))
    z=torch.zeros((1,32),requires_grad=True);projection=torch.from_numpy(gen.standard_normal((32,64)).astype(np.float32)*.1)
    target=torch.ones((1,48))*.1;optimizer=torch.optim.SGD([z],lr=.2);losses=[]
    original=hashlib.sha256(module.q8_blocks.numpy().tobytes()).hexdigest()
    for _ in range(12):
        optimizer.zero_grad();prediction=module(torch.tanh(z@projection));loss=((prediction-target)**2).mean();loss.backward();assert torch.isfinite(z.grad).all() and z.grad.abs().sum()>0;optimizer.step();losses.append(float(loss.detach()))
    assert losses[-1]<losses[0] and not list(module.parameters()) and hashlib.sha256(module.q8_blocks.numpy().tobytes()).hexdigest()==original
    assert not torch.cuda.is_initialized()
    result=dict(epoch=time.time(),passed=True,device='CPU',synthetic_fixture_only=True,no_actual_Wan_BWM_model_or_GUI_policy_or_physics=True,cases=cases,latent_z_dim=32,latent_loss_first=losses[0],latent_loss_last=losses[-1],quantized_backbone_buffers_unchanged=True,no_dense_weight_saved_for_backward=True,weights_gradient_not_supported_by_design=True,scope='Q8_0 mathematics can preserve input/latent gradients through a frozen linear layer. Does not prove full model integration, single4090 memory fit, action conditioning, adaptation quality or complete paper replication.',native_T2z_DiffSynth_GGUF_loader_pending=True,no_subagents_used=True)
    put('Q8_0_FROZEN_LINEAR_LATENT_AUTOGRAD_SYNTHETIC_CPU_ACTUAL.json',result);print(json.dumps(result))
except BaseException:
    put('Q8_0_SYNTHETIC_CPU_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(epoch=time.time(),error=traceback.format_exc(),no_real_model_read_or_GPU=True));raise
