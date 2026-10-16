from pathlib import Path
import os,sys,json,time,traceback
os.environ['CUDA_VISIBLE_DEVICES']=''
import torch
D=Path(__file__).resolve().parent;R=D/'reports';sys.path.insert(0,str(D.parent/'MOD4_H1_FLAT_JUMP_FULLSTATE_REWARD_NATIVE_ADMISSION_20261016'));from review_H1_complete_native_models_source_and_admission_local_CPU_once import H,eq,tensors
def main():
 v=json.loads((R/'V9_TWO_AVAILABLE_IMMUTABLE_FIRST_MODELS_CURB275_NATIVE_BOUND_COLLECTION_ACTUAL.json').read_bytes());proof=json.loads((R/'V9_FINAL_SOURCE_STATUS_FIX_E3_NATIVE_REUSE_CURB_DEFERRED_CPU_ACTUAL.json').read_bytes());specs={s['key']:s for s in proof['frozen']};rng=torch.get_rng_state().clone();torch.set_num_threads(2);out={}
 for key in ('e2','recovery'):
  rows=v[key]['immutable_models'];b=D/'actual_V9_first_models'/key;first=b/'model_update1.pt';zero=b/'own_startup0.pt'
  if not first.exists() or not zero.exists():out[key]=dict(first_immutable_PPO_verified=False,reason='Incomplete in actual collected snapshot, not inferred failed');continue
  for row in rows:assert Path(row['local_path']).stat().st_size==row['bytes'] and H(row['local_path'])==row['SHA'] and row['twohost_complete_SHA']
  spec=specs[key];source=D/'v9_payload'/key/'job0/source'/spec['source_filename'];assert H(source)==spec['source_SHA'];s=torch.load(source,map_location='cpu',weights_only=False);z=torch.load(zero,map_location='cpu',weights_only=False);c=torch.load(first,map_location='cpu',weights_only=False);count=[0,0];tensors(c,count)
  for k in ('actor_state_dict','critic_state_dict','optimizer_state_dict'):assert eq(s[k],z[k]),(key,k)
  before=spec['source_Adamstep'];assert len(c['optimizer_state_dict']['state'])==17 and {int(x['step']) for x in c['optimizer_state_dict']['state'].values()}=={before+20};changed={k:[n for n in s[k] if not eq(s[k][n],c[k][n])] for k in ('actor_state_dict','critic_state_dict')};assert len(changed['actor_state_dict'])==9 and len(changed['critic_state_dict'])==8
  out[key]=dict(first_immutable_PPO_verified=True,path=str(first),bytes=first.stat().st_size,SHA=H(first),source_SHA=spec['source_SHA'],all17Adam_before=before,all17Adam_after=before+20,source0_core_literal_exact=True,actor9inclSTD_critic8_all_changed=changed,whole_model_counts=count,all_tensor_finite=True,production_controls=24,production_envsteps=480000,native_not_credited_as_PPO=True)
 assert torch.equal(rng,torch.get_rng_state()) and not torch.cuda.is_initialized();p=R/'V9_TWO_AVAILABLE_FIRST_MODELS_COMPLETE_LOCAL_CPU_VERIFIED_ACTUAL.json';assert not p.exists();p.write_text(json.dumps(dict(epoch=time.time(),passed_all_available_models=True,experts=out,CURB275_native_not_called_PPO=True,no_skill_qualification_inferred=True,CPU_RNG_unchanged0CUDA0optimizer=True),indent=2),encoding='utf8');print(json.dumps(out),flush=True)
if __name__=='__main__':
 try:main()
 except BaseException:
  with (R/('V9_FIRST_MODELS_CPU_ORIGINAL_ERROR_'+str(time.time_ns())+'.json')).open('x',encoding='utf8') as f:json.dump(dict(epoch=time.time(),error=traceback.format_exc(),no_GPU_replay=True),f,indent=2)
  raise
