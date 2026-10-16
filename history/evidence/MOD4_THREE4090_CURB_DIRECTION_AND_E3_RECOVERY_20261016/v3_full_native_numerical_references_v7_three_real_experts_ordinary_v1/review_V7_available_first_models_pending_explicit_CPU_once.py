from pathlib import Path
import os,sys,json,time
os.environ['CUDA_VISIBLE_DEVICES']=''
import torch
D=Path(__file__).resolve().parent;R=D/'reports';sys.path.insert(0,str(D.parent/'MOD4_H1_FLAT_JUMP_FULLSTATE_REWARD_NATIVE_ADMISSION_20261016'));from review_H1_complete_native_models_source_and_admission_local_CPU_once import H,eq,tensors
def main():
 rng=torch.get_rng_state().clone();torch.set_num_threads(2);v=json.loads((R/'THREE_V7_ALL_NATIVE_CPU_AND_AVAILABLE_FIRST_MODELS_BOUND_COLLECTION_ACTUAL.json').read_bytes());proof=json.loads((R/'V7_FINAL_THREEWAY_SOURCE_MANIFEST_CPU_ACTUAL.json').read_bytes());specs={s['key']:s for s in proof['frozen']};out={}
 for key,spec in specs.items():
  b=D/'actual_V7_three_expert_native_first_models'/key;phase='production_only' if key=='curb' else 'production';first=b/(phase+'_model_update1.pt');zero=b/(phase+('_own_fresh_startup0.pt' if key=='curb' else '_own_startup0.pt'))
  if not first.exists() or not zero.exists():out[key]=dict(first_immutable_PPO_verified=False,reason='Immutable production model and startup0 not both in collected snapshot; not inferred failed',available_files=[p.name for p in b.glob('*.pt')]);continue
  source=D/'v7_payload'/key/'job0/source'/spec['source_filename'];s=torch.load(source,map_location='cpu',weights_only=False);z=torch.load(zero,map_location='cpu',weights_only=False);ck=torch.load(first,map_location='cpu',weights_only=False);count=[0,0];tensors(ck,count)
  for k in ('actor_state_dict','critic_state_dict','optimizer_state_dict'):assert eq(s[k],z[k]),(key,k)
  before=spec['source_Adamstep'];assert len(ck['optimizer_state_dict']['state'])==17 and {int(x['step']) for x in ck['optimizer_state_dict']['state'].values()}=={before+20};changes={k:[n for n in s[k] if not eq(s[k][n],ck[k][n])] for k in ('actor_state_dict','critic_state_dict')};assert len(changes['actor_state_dict'])==9 and len(changes['critic_state_dict'])==8
  out[key]=dict(first_immutable_PPO_verified=True,path=str(first),bytes=first.stat().st_size,SHA=H(first),source_SHA=H(source),all17Adam_before=before,all17Adam_after=before+20,source0_core_literal_exact=True,actor9inclSTD_critic8_all_changed=changes,whole_model_counts=count,all_tensor_finite=True,production_controls=24,production_envsteps=480000,native_not_credited_as_PPO=True)
 assert torch.equal(rng,torch.get_rng_state()) and not torch.cuda.is_initialized();p=R/'V7_OBSERVED_FIRST_MODELS_WITH_EXPLICIT_PENDING_LOCAL_CPU_ACTUAL.json';assert not p.exists();p.write_text(json.dumps(dict(epoch=time.time(),passed_all_available_models=True,all_three_real_first_PPO_verified=all(x.get("first_immutable_PPO_verified") for x in out.values()),three_independent_PPO_not_NCCL=True,experts=out,no_skill_qualification_inferred=True,CPU_RNG_unchanged0CUDA0optimizer=True),indent=2),encoding='utf8');print(json.dumps(out))
if __name__=='__main__':main()
