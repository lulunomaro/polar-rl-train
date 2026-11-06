"""Pure tensor outputs and gradients against the pinned eager functions."""
from pathlib import Path
import json,sys,time,traceback
import torch
N=Path(__file__).resolve().parent;G=Path('C:/Users/lulu/Desktop/claude/mjcf/polar-rl-train')
sys.path.insert(0,str(G/'project/isaac'))
from mod4v2_scut.supermimic_newton import load_sources
load_sources(G/'project/isaac/mod4v2_scut/SUPERMIMIC_BINDINGS.json')
from supermimic_vendor_v2 import geometry
from mod4v2_scut.supermimic_speed import enable_scripted_geometry
out=dict(epoch=time.time(),passed=False,production_PT_reads=0,SSH=0,physics=0,rows=[])
try:
    torch.manual_seed(9201)
    for name in ('invariant_features','yaw_mat','so3_exp','so3_log'):
        fn=getattr(geometry,name);script=torch.jit.script(fn)
        for scale in (1e-6,.1,1.):
            rot=geometry.so3_exp(torch.randn(32,3,device='cuda:0')*scale).detach()
            state=(torch.randn(32,3,device='cuda:0'),rot,torch.randn(32,3,device='cuda:0'),
                torch.randn(32,3,device='cuda:0'),torch.randn(32,30,device='cuda:0'),torch.randn(32,30,device='cuda:0'))
            value=state if name=='invariant_features'else((rot,)if name in ('so3_log','yaw_mat')else(torch.randn(32,3,device='cuda:0')*scale,))
            a=tuple(x.detach().clone().requires_grad_()for x in value)
            b=tuple(x.detach().clone().requires_grad_()for x in value)
            left=fn(a)if name=='invariant_features'else fn(*a)
            right=script(b)if name=='invariant_features'else script(*b)
            weight=torch.randn_like(left)
            ga=torch.autograd.grad((left*weight).sum(),a,allow_unused=True)
            gb=torch.autograd.grad((right*weight).sum(),b,allow_unused=True)
            torch.testing.assert_close(left,right,atol=3e-6,rtol=3e-5)
            error=0.
            for x,y in zip(ga,gb):
                if x is None:assert y is None;continue
                assert bool(torch.isfinite(x).all())and bool(torch.isfinite(y).all())
                torch.testing.assert_close(x,y,atol=1e-5,rtol=3e-5)
                error=max(error,float((x-y).abs().max()))
            out['rows'].append(dict(function=name,scale=scale,
                max_output_error=float((left-right).abs().max()),max_gradient_error=error))
    out.update(passed=True,installation=enable_scripted_geometry(),RNG_draws_in_functions=0)
except BaseException:out['error']=traceback.format_exc()
with(N/'reports/SCRIPTED_GEOMETRY_OUTPUT_GRADIENT_PARITY.json').open('x',encoding='utf8')as stream:json.dump(out,stream,indent=2)
print(json.dumps(out))
if not out['passed']:raise SystemExit(1)
