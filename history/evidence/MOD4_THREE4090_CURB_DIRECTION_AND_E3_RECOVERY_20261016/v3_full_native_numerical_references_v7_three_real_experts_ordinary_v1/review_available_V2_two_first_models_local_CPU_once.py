from pathlib import Path
import os,sys,time,json
os.environ['CUDA_VISIBLE_DEVICES']=''
import torch
D=Path(__file__).resolve().parent;R=D/'reports';sys.path.insert(0,str(D.parent/'MOD4_H1_FLAT_JUMP_FULLSTATE_REWARD_NATIVE_ADMISSION_20261016'));from review_H1_complete_native_models_source_and_admission_local_CPU_once import H,eq,tensors
def main():
 p=R/'V2_CURB_AND_E2_FIRST_IMMUTABLE_MODELS_AVAILABLE_LOCAL_CPU_ACTUAL.json';assert not p.exists();rng=torch.get_rng_state().clone();torch.set_num_threads(2);out={}
 for key in ('curb','e2'):
  b=D/'actual_V2_positive_and_V3_native_models'/key;phase='production_only' if key=='curb' else 'production';first=b/(phase+'_model_update1.pt');zero=b/(phase+('_own_fresh_startup0.pt' if key=='curb' else '_own_startup0.pt'));source=D/'v2_payload'/key/'job0/source'/('CURB140.pt' if key=='curb' else 'E2_final58.pt');assert first.exists() and zero.exists();s=torch.load(source,map_location='cpu',weights_only=False);z=torch.load(zero,map_location='cpu',weights_only=False);v=torch.load(first,map_location='cpu',weights_only=False);counts=[0,0];tensors(v,counts)
  for n in ('actor_state_dict','critic_state_dict','optimizer_state_dict'):assert eq(s[n],z[n])
  before=666160 if key=='curb' else 643760;assert {int(x['step']) for x in s['optimizer_state_dict']['state'].values()}=={before};assert len(v['optimizer_state_dict']['state'])==17 and {int(x['step']) for x in v['optimizer_state_dict']['state'].values()}=={before+20};changes={n:[k for k in s[n] if not eq(s[n][k],v[n][k])] for n in ('actor_state_dict','critic_state_dict')};assert len(changes['actor_state_dict'])==9 and len(changes['critic_state_dict'])==8
  out[key]=dict(path=str(first),bytes=first.stat().st_size,SHA=H(first),source_SHA=H(source),source0_actor9_critic8_STD17Adam_literal_exact=True,whole_checkpoint_tensor_count=counts,all_finite=True,all17Adam_before=before,all17Adam_after=before+20,actor9_including_STD_critic8_actual_changes=changes,production_controls=24,production_envsteps=480000,complete_immutable_first_PPO_verified=True,download_protocol='Completed .partial rename only after collector verified remote bytes and SHA; full collection receipt pending nativeV3 finish')
 assert torch.equal(rng,torch.get_rng_state()) and not torch.cuda.is_initialized();result=dict(epoch=time.time(),passed=True,experts=out,not_skill_pass_or_FINAL=True,CPU_RNG_unchanged0CUDA0optimizer=True);p.write_text(json.dumps(result,indent=2),encoding='utf8');print(json.dumps(result))
if __name__=='__main__':main()
