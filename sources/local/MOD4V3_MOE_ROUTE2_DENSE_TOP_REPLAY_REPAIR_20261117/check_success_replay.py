from pathlib import Path
import copy,hashlib,importlib.util,json,argparse
import numpy as np
import torch
T=Path(__file__).resolve().parent;S=T/'support/mod4v3_ppo_v1'
def module(name):
 spec=importlib.util.spec_from_file_location(name,S/(name+'.py'));m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
common=module('route2_common');replay=module('success_replay')
p=argparse.ArgumentParser();p.add_argument('--label',default='combined');args=p.parse_args();out=T/'evidence'/('replay_check_'+args.label);out.mkdir(exist_ok=True)
pool=replay.SuccessReplayPool();paths=[];all_frames=[];all_phases=[];source_index=[]
for job in ['native_dense_probe_v1_r3','native_dense_probe_010m']:
 folder=T/'evidence'/job/'success_replay'
 for f in sorted(folder.glob('episode_*.npz')):
  with np.load(f,allow_pickle=False)as a:
   frames=a['frames'];phases=a['phases'];meta=json.loads(str(a['metadata_json']))
   assert not meta['truncated']and len(frames)==meta['episode_steps']
   assert meta['accepted_native_success']and not meta['teacher_assistance']and meta['stable_hold_s']>=.4
   assert np.array_equal(frames[:,35:455].reshape(-1,12,35)[:,-1],frames[:,:35])
   assert np.allclose(frames[1:,22:28],frames[:-1,455:461],atol=1e-6)
   pool.add(frames,phases,meta);all_frames.append(frames);all_phases.append(phases)
   source_index.append(dict(path=str(f),sha256=hashlib.sha256(f.read_bytes()).hexdigest(),frames=len(frames),metadata=meta))
assert pool.frames>0
ckpath=T/'weights/model_step000.pt';before=hashlib.sha256(ckpath.read_bytes()).hexdigest();ck=torch.load(ckpath,map_location='cpu',weights_only=False);actor=common.LocalRoute2Actor().load_checkpoint(ck);reference=copy.deepcopy(actor.mlp.e1).requires_grad_(False);sample=pool.sample(128,'cpu');scale=torch.tensor([.18,.18,.18,.18,.25,.25])
with torch.no_grad():initial_replay=float(((actor.mlp.e1(sample['policy'],sample['obs_history'])-sample['actions'])/scale).square().mean());actor.mlp.e1.head[-1].bias.add_(.01)
current=actor.mlp.e1(sample['policy'],sample['obs_history']);target=reference(sample['policy'],sample['obs_history']).detach();settle=torch.zeros(128,dtype=torch.bool);settle[:32]=True;settle|=sample['policy'][:,0].abs()<.05
checks={}
for iteration in [0,20,80,1000]:
 progress=min(1.,max(0.,(iteration-20)/60.));high=2*(1-progress)+.5*progress;low=.75*(1-progress)+.15*progress;coefficient=torch.where(sample['policy'][:,3]>1.7,high,low);coefficient=torch.where(settle,torch.full_like(coefficient,8.),coefficient);assert torch.all(coefficient[settle]==8.);checks[iteration]=dict(settle_coefficient=float(coefficient[settle].min()),other_high=high,other_low=low)
anchor=(coefficient*((current-target)/scale).square().mean(-1)).mean();bc=((current-sample['actions'])/scale).square().mean();loss=anchor+.5*bc;loss.backward()
grads={name:float(sum((p.grad.square().sum()for p in m.parameters()if p.grad is not None),torch.tensor(0.)).sqrt())for name,m in [('head',actor.mlp.e1.head),('encoder',actor.mlp.e1.encoder)]};assert all(np.isfinite(v)and v>0 for v in grads.values());assert all(p.grad is None for p in actor.mlp.e0.parameters());assert actor.distribution.e0_std.grad is None
assert hashlib.sha256(ckpath.read_bytes()).hexdigest()==before
assert all(not bool((entry[1]==0).any())for entry in pool.episodes if entry[2]['source_model_sha256']!='a55eeaed11ed7c7471444e1369153824b3fe79544e59296c911a3235507bd7a4')
np.savez_compressed(out/'qualified_native_success_pool.npz',frames=torch.cat([a[0]for a in pool.episodes]).numpy(),phases=torch.cat([a[1]for a in pool.episodes]).numpy(),source_metadata_json=np.asarray(json.dumps(source_index)))
result=dict(passed=True,qualified_pool=pool.summary(),source_index=source_index,initial_v1_replay_MSE_scaled=initial_replay,permanent_settle_checks=checks,replay_anchor_backward_gradient_norms=grads,E0_gradient_zero=True,parent_file_SHA_unchanged=True,PPO_updates=0,optimizer_updates=0,in_memory_head_bias_probe=.01,formal_or_fullDR_graduation=False)
(out/'VERIFICATION.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf8');print(json.dumps({k:v for k,v in result.items()if k!='source_index'},ensure_ascii=False))
