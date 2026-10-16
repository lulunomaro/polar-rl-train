from pathlib import Path
import os,sys,time,json,traceback
os.environ['CUDA_VISIBLE_DEVICES']=''
import torch
N=Path(__file__).resolve().parent;R=N/'reports';sys.path.insert(0,str(N.parent/'MOD4_H1_FLAT_JUMP_FULLSTATE_REWARD_NATIVE_ADMISSION_20261016'))
from review_H1_complete_native_models_source_and_admission_local_CPU_once import H,eq,tensors
def main():
 v=json.loads((R/'H1_SOURCE210_NATIVE_ONLY_EXISTING_CHAIN_BOUND_COLLECTION_ACTUAL.json').read_bytes());h=v['H1'];assert not h['actual_own_processes'];parent=next(r['value'] for r in h['files'] if r['path'].endswith('/PARENT_FINAL.json'));assert parent['passed'] and parent['native_and_CPU_only'] and not parent['canonical_write'] and parent['optimizer_updates']==0;assert next(r['value'] for r in h['files'] if r['path'].endswith('/OWN_VALIDATION_FCNTL_RELEASED_ACTUAL.json'))['actual_unlock'];native=next(r for r in h['files'] if r['path'].endswith('/H1_PRELAUNCH_V2_NATIVE180_ALL_ROWS_CPU_ADMITTED.json'));assert native['value']['passed'] and native['value']['controls']==180 and native['value']['callbacks']==720 and native['value']['all_policy_rows']==3600000 and native['value']['all_physical_rows']==14400000
 source=N/'h1_closed25_source210_nativeonly_payload/job0/source/H1_final10_protected.pt';s=torch.load(source,map_location='cpu',weights_only=False);rng=torch.get_rng_state().clone();models=[]
 for row in v['downloaded_models']:
  p=Path(row['local_path']);assert H(p)==row['SHA'] and p.stat().st_size==row['bytes'] and row['twohost_complete_SHA'];ck=torch.load(p,map_location='cpu',weights_only=False);count=[0,0];tensors(ck,count)
  for k in ('actor_state_dict','critic_state_dict','optimizer_state_dict'):assert eq(s[k],ck[k]),k
  assert len(ck['optimizer_state_dict']['state'])==17 and {int(x['step']) for x in ck['optimizer_state_dict']['state'].values()}=={640260}
  if row['kind']=='initial':assert torch.equal(ck['sensor_DR_state']['episode'],s['sensor_DR_state']['episode']+1) and not ck['H1_public_request_phase_state']['phase']['tensors']['age_control'].any()
  models.append(dict(row,all_tensors_finite=True,whole_model_tensor_counts=count,source_core9STD8critic17Adam_literalexact=True,all17Adam640260_no_update=True))
 assert len(models)==2 and torch.equal(torch.get_rng_state(),rng) and not torch.cuda.is_initialized();owner=next(r['value'] for r in v['N72_owner']['files'] if r['path'].endswith('/OWNER_CURRENT.json'));assert owner['original_canonical_active'] and owner['original_two_fcntl_held'] and not owner['stop'];current={k:dict(phase=r['phase'],latest_actual_saved_metadata=r.get('latest_save'),not_new_whole_local_model_download=True) for k,r in owner['rows'].items()};out=dict(epoch=time.time(),passed=True,source_SHA=H(source),models=models,H1_native_GPU_CPU_actual_closed_and_own_private_fcntl_free=True,original_source_episode_exact_plus1=True,all3600000_policy_and14400000_physical_rows_CPU_admitted_report=dict(path=native['path'],SHA=native['SHA'],value=native['value']),H1_PPO_updates0_new_canonical_charge0=True,H1_native_events_not_skill=True,current_two72_saved_PPO_snapshot=current,current_sourceGPU_compute_snapshot=v['original_canonical']['compute_snapshot'],source_GPU_temporarily_idle_after_native_original_two_key_writer_still_active=True,next_unified_three_slot_contract_prepared_runtime_not_dispatched=True,no_second_writer_or_hot_add_or_forced_healthy_stop=True,CPU_RNG_unchanged0CUDA0optimizer=True)
 p=R/'H1_SOURCE210_NATIVE180_ALL_ROWS_TWO_COMPLETE_MODELS_LOCAL_CPU_VERIFIED_ACTUAL.json';assert not p.exists();p.write_text(json.dumps(out,indent=2),encoding='utf8');print(json.dumps(dict(H1_native_passed=True,models=[dict(SHA=x['SHA'],counts=x['whole_model_tensor_counts']) for x in models],H1_new_PPO=False,source_episode_plus1=True,existing_two72_phase={k:x['phase'] for k,x in current.items()})),flush=True)
if __name__=='__main__':
 try:main()
 except BaseException:
  with (R/('H1_SOURCE210_NATIVE_MODEL_CPU_ORIGINAL_ERROR_'+str(time.time_ns())+'.json')).open('x',encoding='utf8') as f:json.dump(dict(epoch=time.time(),error=traceback.format_exc(),no_GPU_or_native_replay=True),f,indent=2)
  raise
