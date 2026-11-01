"""First CPU decode of exact recovered305final; original305reader failed pre-read."""
import os
os.environ['CUDA_VISIBLE_DEVICES']=''
from pathlib import Path
import hashlib,io,json,sys,time,traceback
N=Path(__file__).resolve().parent;T=N.parent;O=T/'REFERENCE_TRACKING_REAL_VALUE_V305_20261101';R=N/'reports'
def put(n,x):
 with(R/n).open('x',encoding='utf8')as f:json.dump(x,f,indent=2,allow_nan=False)
try:
 assert not(R/'CPU307_RECOVERED305_CONSUMED.json').exists()
 transfer=json.loads((R/'ROOT307_NEW_FINAL305_SINGLE_TRANSFER.json').read_bytes());closed=json.loads((R/'ROOT307_EXACT_FINAL_OWN_CLOSURE_AND_DIAGNOSTIC_CLASSIFICATION.json').read_bytes());assert transfer['passed']and closed['passed']and closed['canonical_None']
 sys.path.insert(0,str(O));from teacher_task305 import validate_final
 task=json.loads((O/'TASK305_FROZEN.json').read_bytes());final=closed['final'];validate_final(final,task,final['original_finite_owner_GO'])
 put('CPU307_RECOVERED305_CONSUMED.json',dict(epoch=time.time(),purpose='First wholeCPUdecode exact305final after independentfilenameclassificationrecovery; original305CPUfailedbeforeread',model_reads_max=1,SDK=0,GO=0,CUDA=False))
 import torch
 raw=Path(transfer['path']).read_bytes();assert len(raw)==transfer['bytes']and hashlib.sha256(raw).hexdigest()==transfer['SHA']
 ck=torch.load(io.BytesIO(raw),map_location='cpu',weights_only=False);del raw
 count=[0]
 def finite(x):
  if torch.is_tensor(x):
   count[0]+=1
   if x.is_floating_point()or x.is_complex():assert torch.isfinite(x).all()
  elif isinstance(x,dict):
   for y in x.values():finite(y)
  elif isinstance(x,(list,tuple)):
   for y in x:finite(y)
 finite(ck);s=ck['student'];pi=ck['actual_new_Pi_updates'];wm=ck['total_WM_updates']
 assert ck['kind']=='REFERENCE_TRACKING_BPTT305_COMPLETE'and pi==ck['actual_new_critic_updates']==2724 and wm==12468
 assert s['actor_state_dict']['mlp.0.weight'].shape==(128,103)and s['critic_state_dict']['mlp.0.weight'].shape==(128,106)
 assert s['target_critic_state_dict'].keys()==s['critic_state_dict'].keys()
 teacher=ck['teacher_full_PPO_state'];assert teacher['iter']==2135 and len(teacher['optimizer_state_dict']['state'])==17 and all(int(v['step'])==42940 for v in teacher['optimizer_state_dict']['state'].values())
 assert torch.equal(s['actor_state_dict']['distribution.std_param'],teacher['actor_state_dict']['distribution.std_param'])
 for scope,offset in(('actor',45533),('critic',2593)):
  optimizer=s[scope+'_optimizer'];ids={r['optimizer_id']:r['state_key']for r in s['identity']['targets'][scope]['parameter_bindings']};assert len(optimizer['state'])==(9 if scope=='actor' else 8)
  for pid,v in optimizer['state'].items():
   key=ids[pid];assert int(v['step'])==(42940 if key=='distribution.std_param'else offset+pi)
   assert v['exp_avg'].shape==v['exp_avg_sq'].shape==s[scope+'_state_dict'][key].shape
 assert all(int(v['step'])==wm for v in ck['world_model']['world_optimizer']['state'].values())
 assert s['actor_Adam_offset']==45533 and s['critic_Adam_offset']==2593 and s['goal_dim']==59 and not s['old_Fudan_return']and s['critic_same_tracking_return']
 assert ck['current_episodes'].shape==ck['reference_phase_steps'].shape==(80,)and not ck['mixed_ground_JUMP_state']['flat_mask'].any()
 assert set(ck['target_DR_state']['components'])=={'sensor','feedback','physics_action_queue','spring','damping','COM','PD'}
 row=dict(epoch=time.time(),passed=True,path=transfer['path'],remote_path=final['final']['path'],SHA=transfer['SHA'],bytes=transfer['bytes'],Pi=pi,critic=pi,totalWM=wm,newWM=wm-9712,finite_tensors=count[0],allthreeAdam=True,EMA_target=True,teacher17Adam=True,STD=True,actor103=True,critic106=True,phase=True,full_DR_norm_rng=True,model_reads=1,CUDA=torch.cuda.is_initialized(),original305classification_false_preserved=True,originalfee=transfer['original_fee'],skill_not_inferred=True)
 put('ROOT307_NEW_FINAL305_WHOLE_CPU_RETURNED_ACTUAL.json',row);print(json.dumps(row),flush=True)
except BaseException:
 put('CPU307_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),once_consumed=True));raise
