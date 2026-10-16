"""Verify three actual first full PPO updates and distinct actors; no GPU/replay/optimizer."""
from pathlib import Path
import os,hashlib,json,time
os.environ['CUDA_VISIBLE_DEVICES']=''
import torch
torch.set_num_threads(4)
D=Path(__file__).resolve().parent;R=D/'reports'
def H(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def model_hash(sd):return hashlib.sha256(b''.join(k.encode()+str(tuple(z.shape)).encode()+str(z.dtype).encode()+z.contiguous().numpy().tobytes() for k,z in sd.items())).hexdigest()
def check(job,kind,src,initial):
 p=D/'first_independent_models'/('job'+str(job))/'model_update1.pt';v=torch.load(p,map_location='cpu',weights_only=False);s=torch.load(src,map_location='cpu',weights_only=False);count=[0,0]
 def finite(x):
  if torch.is_tensor(x):count[0]+=1;count[1]+=int(x.is_floating_point());assert not x.is_floating_point() or torch.isfinite(x).all()
  elif isinstance(x,dict):
   for z in x.values():finite(z)
  elif isinstance(x,(tuple,list)):
   for z in x:finite(z)
 finite(v);assert len(v['actor_state_dict'])==9 and len(v['critic_state_dict'])==8 and len(v['optimizer_state_dict']['state'])==17;assert {int(z['step']) for z in s['optimizer_state_dict']['state'].values()}=={initial};assert {int(z['step']) for z in v['optimizer_state_dict']['state'].values()}=={initial+20};task=v['independent_expert_task_contract'];assert task['job']==job and task['kind']==kind and task['source_SHA']==H(src)
 changed={k:[n for n,z in v[k].items() if z.contiguous().numpy().tobytes()!=s[k][n].contiguous().numpy().tobytes()] for k in ('actor_state_dict','critic_state_dict')};assert len(changed['actor_state_dict'])==9 and len(changed['critic_state_dict'])==8
 return dict(job=job,kind=kind,model_path=str(p.resolve()),bytes=p.stat().st_size,SHA=H(p),source_path=str(src.resolve()),source_SHA=H(src),tensor_counts=count,whole_checkpoint_finite=True,actor9_STD_critic8_changed=changed,all17Adam_initial=initial,all17Adam_first_update=initial+20,actual_one_update_20_original_minibatch_steps=True,actor_digest=model_hash(v['actor_state_dict']),critic_digest=model_hash(v['critic_state_dict']),new_scope_extra_state_preserved=sorted(v['independent_expert_scope_state']))
def main():
 out=R/'THREE_DISTINCT_EXPERT_FIRST_FULL_MODELS_ACTUAL_LOCAL_CPU_VERIFIED.json';assert not out.exists();wait=json.loads((R/'OWN_WAVE_V3_FIRST_SAVED_PPO_BOUND_WAIT_COMPLETE.json').read_bytes());assert wait['actual_first_model'];rows=[check(0,'CURB20',D/'train_payload/job0/source/source.pt',642840),check(1,'SLOPE5',D/'train_payload/job1/source/source.pt',642980),check(3,'WAVE35',D/'wave_episode_reviewed_payload_v3/job3/source/source.pt',642840)];assert len({r['actor_digest'] for r in rows})==3 and len({r['critic_digest'] for r in rows})==3;assert not torch.cuda.is_initialized();v=dict(epoch=time.time(),passed=True,rows=rows,three_independent_actual_actor_critic_optimizer_updates_not_shared_NCCL=True,same_ancestor_CURB_WAVE_first_parameters_distinct=True,complete_first_models_not_rolling_latest=True,CPU_optimizer_updates=0,not_skill_improvement_or_native_physics_replay=True,prior_WAVE2_failure_preserved_new_job3_verified=True);out.write_text(json.dumps(v,indent=2),encoding='utf8');print(json.dumps(dict(passed=True,models=[{k:r[k] for k in ('job','kind','SHA','all17Adam_initial','all17Adam_first_update')} for r in rows],three_distinct_actors=True,three_distinct_critics=True)),flush=True)
if __name__=='__main__':main()
