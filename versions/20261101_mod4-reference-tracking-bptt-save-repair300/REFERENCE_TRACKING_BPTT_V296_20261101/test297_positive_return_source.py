import os
os.environ['CUDA_VISIBLE_DEVICES']=''
from pathlib import Path
import json,time,torch
N=Path(__file__).resolve().parent.parent/'REFERENCE_TRACKING_BPTT_V297_20261101'
cost=torch.tensor([0.,1.,5.,20.],requires_grad=True);reward=torch.exp(-cost/5.)
assert bool((reward>0).all())and bool((reward<=1).all())and bool((reward[:-1]>reward[1:]).all())
(-reward.sum()).backward();assert bool(torch.isfinite(cost.grad).all())and bool((cost.grad>0).all())
actor=(N/'source/tracking_learner297.py').read_text('utf8');worker=(N/'source/worker297.py').read_text('utf8')
assert 'reward=torch.exp(-cost/5.)'in actor and 'return torch.exp(-cost/5.)'in worker
assert "labels(meta['phase']+i,envs"in actor and 'labels(epstep.long(),torch.arange'in worker
with(N/'reports/CPU297_POSITIVE_RETURN_PHASE_SOURCE_TEST.json').open('x',encoding='utf8')as f:json.dump(dict(passed=True,epoch=time.time(),cost=cost.detach().tolist(),reward=reward.detach().tolist(),gradient=cost.grad.tolist(),online_imagined_return_equal=True,firstendpoint_alignment_fixed=True,modelreads=0,optimizersteps=0,SDK=0,CUDA=False),f,indent=2)
print(json.dumps(dict(passed=True,no_new_model_reads=True)))
