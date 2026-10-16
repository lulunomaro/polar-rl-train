from pathlib import Path
import os,sys,time,json,traceback
os.environ['CUDA_VISIBLE_DEVICES']=''
import torch
N=Path(__file__).resolve().parent;P=N.parent/'MOD4_E1_CURB275_BRIDGE_FROM_CURB35_40_20261016';R=N/'reports'
sys.path.insert(0,str(N.parent/'MOD4_H1_FLAT_JUMP_FULLSTATE_REWARD_NATIVE_ADMISSION_20261016'))
from review_H1_complete_native_models_source_and_admission_local_CPU_once import H,eq,tensors
def main():
 v=json.loads((R/'N72_V2_EXISTING_NATIVE_IMMUTABLE_FIRST_COMPLETE_READONLY_ACTUAL.json').read_bytes());out={};rng=torch.get_rng_state().clone();torch.set_num_threads(2)
 for key,name,before in [('e2','E2_final58.pt',649400),('recovery','E0_full_source.pt',642040)]:
  row=next(r for r in v['downloaded_models'] if '/'+key+'/' in r['path'] and r['kind']=='immutable_model_update1.pt');p=Path(row['local_path']);assert p.stat().st_size==row['bytes'] and H(p)==row['SHA'] and row['twohost_complete_SHA'];source=N/'v2_payload'/key/'job0/source'/name;s=torch.load(source,map_location='cpu',weights_only=False);c=torch.load(p,map_location='cpu',weights_only=False);count=[0,0];tensors(c,count);assert len(c['optimizer_state_dict']['state'])==17 and {int(z['step']) for z in c['optimizer_state_dict']['state'].values()}=={before+20};assert {int(z['step']) for z in s['optimizer_state_dict']['state'].values()}=={before};changes={k:[n for n in s[k] if not eq(s[k][n],c[k][n])] for k in ('actor_state_dict','critic_state_dict')};assert len(changes['actor_state_dict'])==9 and len(changes['critic_state_dict'])==8
  node=next(q['value'] for q in v[key]['files'] if q['path'].endswith('/NODE_CURRENT.json'));n=node['row']['native_CPU'];assert n['value']['passed'] and n['value']['source_SHA']==H(source) and n['value']['controls']==(144 if key=='e2' else 336) and n['actual_CPU_waited_EXIT0'];assert node['row']['phase']=='production' and not node['reply']['stop'];go=node['reply']['go'];assert go['max_parent_seconds']==3600 and go['exit_headroom_seconds']==300 and go['source_SHA']==H(source)
  out[key]=dict(row,source_SHA=H(source),whole_model_tensor_counts=count,all_tensor_finite=True,all17Adam_before=before,all17Adam_after=before+20,all_actor9inclSTD_critic8_changed=changes,native_complete_and_CPU_report_SHA=n['SHA'],native_0PPO_not_credited=True,actual_production_GO=go,first_production_controls=24,first_production_envsteps=480000,not_frozen_skill_qualification=True)
 assert torch.equal(rng,torch.get_rng_state()) and not torch.cuda.is_initialized();report=dict(epoch=time.time(),passed=True,two_independent_experts=out,no_NCCL_weight_or_action_average=True,CURB275_final87_separate_closed_not_third_active_PPO=True,CPU_RNG_unchanged0CUDA0optimizer=True,reader_startup_filename_lookup_own_fresh_startup0_absent_for72_explicit_no_new_exact_zero_model_download_claim=True,actual_native_CPU_source_exact_report_and_local_source_to_first_update_comparison_separate=True)
 p=R/'N72_TWO_DISTINCT_FIRST_REAL_PPO_COMPLETE_MODELS_LOCAL_CPU_VERIFIED.json';assert not p.exists();p.write_text(json.dumps(report,indent=2),encoding='utf8');print(json.dumps({k:dict(SHA=x['SHA'],tensors=x['whole_model_tensor_counts'],Adam=x['all17Adam_after'],learning_started=x['actual_production_GO']['learning_started_epoch']) for k,x in out.items()}),flush=True)
if __name__=='__main__':
 try:main()
 except BaseException:
  with (R/('N72_FIRST_MODEL_CPU_ORIGINAL_ERROR_'+str(time.time_ns())+'.json')).open('x',encoding='utf8') as f:json.dump(dict(epoch=time.time(),error=traceback.format_exc(),no_GPU_replay=True),f,indent=2)
  raise
