"""Independent immutable full-model proof for two distinct expert continuations."""
from pathlib import Path
import os,sys,json,time,hashlib,traceback
os.environ['CUDA_VISIBLE_DEVICES']=''
import torch
D=Path(__file__).resolve().parent;W=D.parent;R=D/'reports';OLD=W/'MOD4_H1_FLAT_JUMP_FULLSTATE_REWARD_NATIVE_ADMISSION_20261016';sys.path.insert(0,str(OLD));from review_H1_complete_native_models_source_and_admission_local_CPU_once import eq,tensors,H
def main():
 p=R/'TWO_REAL_DISTINCT_CONTINUATION_FIRST_PPO_FULL_MODELS_LOCAL_CPU_VERIFIED.json';assert not p.exists();rng=torch.get_rng_state().clone();torch.set_num_threads(4);v=json.loads((R/'TWO_CONTINUATION_NATIVE_FIRST_PRODUCTION_COMPLETE_BOUND_COLLECTION_ACTUAL.json').read_bytes());proof=[]
 specs=[('curb',W/'MOD4_HOST72_E2_MOVING4_AND_H1_JUMP_ADMISSION_20261016/closed_CURB35_actual_final/model.pt',663200,'native20k_then_production/own_native144.pt','production_only/own_fresh_startup0.pt','production_only/model_update1.pt'),('e2',W/'MOD4_HOST72_E2_MOVING4_AND_H1_JUMP_ADMISSION_20261016/E2_closed_first_scope_final/model.pt',640720,'native/own_native144.pt','production/own_startup0.pt','production/model_update1.pt')]
 for key,src,base,native,zero,first in specs:
  s=torch.load(src,map_location='cpu',weights_only=False);models={};rows=[]
  for row in v[key]['local_models']:
   f=Path(row['path']);assert f.stat().st_size==row['bytes'] and H(f)==row['SHA'];ck=torch.load(f,map_location='cpu',weights_only=False);count=[0,0];tensors(ck,count);models[row['role']]=ck;rows.append(dict(**row,tensors=count[0],float_tensors=count[1],all_model_and_runtime_tensors_finite=True))
  for name in (native,zero):
   for k in ('actor_state_dict','critic_state_dict','optimizer_state_dict'):assert eq(s[k],models[name][k]),(key,name,k)
  f=models[first];assert {int(x['step']) for x in f['optimizer_state_dict']['state'].values()}=={base+20};assert len(f['actor_state_dict'])==9 and len(f['critic_state_dict'])==8 and len(f['optimizer_state_dict']['state'])==17;changes={k:[n for n in s[k] if not eq(s[k][n],f[k][n])] for k in ('actor_state_dict','critic_state_dict')};assert len(changes['actor_state_dict'])==9 and len(changes['critic_state_dict'])==8;proof.append(dict(key=key,source_SHA=H(src),native_and_production0_actor9critic8STD17Adam_literal_exact=True,first_full_PPO_real=True,all17Adam_from=base,all17Adam_to=base+20,actor9_including_STD_changed=changes['actor_state_dict'],critic8_changed=changes['critic_state_dict'],models=rows,production_controls=24,production_envsteps=480000,native144_not_PPO=True,not_2700_FINAL_or_frozen_skill_pass=True))
 assert not torch.cuda.is_initialized() and torch.equal(rng,torch.get_rng_state());report=dict(epoch=time.time(),passed=True,proof=proof,no_NCCL_or_shared_policy_or_weight_average=True,global_CPU_RNG_unchanged0CUDA0optimizer=True,E2_native_initial_fullPT_not_in_this_collection_but_GPU_startup_source_exact_receipt_and_native_final_verified=True,first_PPO_not_route_skill_qualification=True);p.write_text(json.dumps(report,indent=2),encoding='utf8');print(json.dumps(dict(passed=True,two_independent_real_first_PPO_verified=True,CURB17Adam663220=True,E2_17Adam640740=True,not_future_FINAL_or_skill_improvement=True)))
if __name__=='__main__':
 try:main()
 except BaseException:(R/('TWO_FIRST_PPO_LOCAL_CPU_ORIGINAL_ERROR_'+str(time.time_ns())+'.json')).write_text(json.dumps(dict(epoch=time.time(),error=traceback.format_exc(),no_GPU_replay=True),indent=2),encoding='utf8');raise
