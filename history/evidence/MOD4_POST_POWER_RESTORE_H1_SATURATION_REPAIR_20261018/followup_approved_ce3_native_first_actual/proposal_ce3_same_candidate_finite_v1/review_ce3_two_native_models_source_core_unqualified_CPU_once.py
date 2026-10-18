"""Full model integrity/core equality is separate from the rejected row admission."""
from pathlib import Path
import os,sys,json,time,hashlib,traceback
os.environ['CUDA_VISIBLE_DEVICES']=''
import torch
B=Path(__file__).resolve().parent;R=B/'reports';W=B.parent.parent;sys.path.insert(0,str(W/'MOD4_H1_FLAT_JUMP_FULLSTATE_REWARD_NATIVE_ADMISSION_20261016'))
from review_H1_complete_native_models_source_and_admission_local_CPU_once import eq,tensors
H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()

def main():
 torch.set_num_threads(2);rng=torch.get_rng_state().clone();c=json.loads((R/'CE3_OWN_NATIVE_FIRST_COMPLETE_MERGED_MISSING_V2_BOUND_COLLECTION_ACTUAL.json').read_bytes());assert c['target']['errors'];src=B/'payload/h1/job0/source/H1_ce3_public4_closed24.pt';assert H(src)=='ce3c69bbcf56bd6c884681f23f527b9fe9e1884a7b5444ff90d3f7a2e28b2d90';s=torch.load(src,map_location='cpu',weights_only=False);rows=[]
 for row in c['downloaded_models']:
  p=Path(row['local_path']);assert row['twohost_complete_SHA'] and p.stat().st_size==row['bytes'] and H(p)==row['SHA'];x=torch.load(p,map_location='cpu',weights_only=False);counts=[0,0];tensors(x,counts);assert counts==[199,105]
  for k in ('actor_state_dict','critic_state_dict','optimizer_state_dict'):assert eq(s[k],x[k])
  assert {int(v['step']) for v in x['optimizer_state_dict']['state'].values()}=={646100}
  if row['kind']=='own_native_startup0':assert torch.equal(x['sensor_DR_state']['episode'],s['sensor_DR_state']['episode']+1) and not x['H1_public_request_phase_state']['phase']['tensors']['age_control'].any()
  rows.append(dict(row,counts=counts,all_model_runtime_finite=True,source_actor9_STD_critic8_17Adam_literal_exact=True))
 assert len(rows)==2 and torch.equal(rng,torch.get_rng_state()) and not torch.cuda.is_initialized()
 out=dict(epoch=time.time(),passed_two_complete_models_source_core_only=True,models=rows,Adam646100_unchanged=True,initial_only_source_episode_plus1_age0=True,original_dual_FP64_mean_absolute1e4_admission_remains_false=True,no_first_PPO_or_native_admission_permission=True,CPU_RNG_unchanged0CUDA0optimizer=True)
 with (R/'CE3_TWO_COMPLETE_NATIVE_MODELS_FINITE_CORE_ONLY_NOT_ADMISSION_LOCAL_CPU_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(out,f,indent=2)
 print(json.dumps(dict(two_models_finite_core_exact=True,not_admission=True)))

if __name__=='__main__':
 try:main()
 except BaseException:
  with (R/('CE3_TWO_NATIVE_CORE_CPU_ORIGINAL_ERROR_'+str(time.time_ns())+'.json')).open('x',encoding='utf8') as f:json.dump(dict(epoch=time.time(),error=traceback.format_exc(),no_GPU_or_account_mutation=True),f,indent=2)
  raise
