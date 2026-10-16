"""Full first SLOPE checkpoint, source-linked Adam increment, no GPU or optimization."""
from pathlib import Path
import os,json,time,hashlib
os.environ['CUDA_VISIBLE_DEVICES']=''
import torch
torch.set_num_threads(4)
D=Path(__file__).resolve().parent
def main():
 p=D/'first_independent_models/job1/model_update1.pt';src=D/'train_payload/job1/source/source.pt';v=torch.load(p,map_location='cpu',weights_only=False);s=torch.load(src,map_location='cpu',weights_only=False);counts=[0,0]
 def finite(x):
  if torch.is_tensor(x):counts[0]+=1;counts[1]+=int(x.is_floating_point());assert not x.is_floating_point() or torch.isfinite(x).all()
  elif isinstance(x,dict):
   for z in x.values():finite(z)
  elif isinstance(x,(tuple,list)):
   for z in x:finite(z)
 finite(v);assert len(v['actor_state_dict'])==9 and len(v['critic_state_dict'])==8 and len(v['optimizer_state_dict']['state'])==17;assert {int(z['step']) for z in s['optimizer_state_dict']['state'].values()}=={642980};assert {int(z['step']) for z in v['optimizer_state_dict']['state'].values()}=={643000}
 changed={k:[n for n,z in v[k].items() if z.contiguous().numpy().tobytes()!=s[k][n].contiguous().numpy().tobytes()] for k in ('actor_state_dict','critic_state_dict')};assert len(changed['actor_state_dict'])==9 and len(changed['critic_state_dict'])==8 and v['independent_expert_task_contract']['kind']=='SLOPE5';assert not torch.cuda.is_initialized()
 r=dict(epoch=time.time(),passed=True,first_model_path=str(p.resolve()),bytes=p.stat().st_size,SHA=hashlib.sha256(p.read_bytes()).hexdigest(),source_SHA=hashlib.sha256(src.read_bytes()).hexdigest(),all_tensor_counts=counts,whole_checkpoint_finite=True,Adam_all17_source642980_to643000=True,one_original_PPO_update_20_minibatch_steps=True,all_actor9_including_STD_and_critic8_changed=changed,independent_expert_no_NCCL_or_cross_expert_equality_claim=True,CPU_optimizer_updates=0,not_frozen_evaluation_or_training_improvement_claim=True)
 out=D/'reports/FIRST_INDEPENDENT_SLOPE_MODEL_UPDATE1_COMPLETE_LOCAL_CPU_VERIFIED.json';assert not out.exists();out.write_text(json.dumps(r,indent=2),encoding='utf8');print(json.dumps(r),flush=True)
if __name__=='__main__':main()
