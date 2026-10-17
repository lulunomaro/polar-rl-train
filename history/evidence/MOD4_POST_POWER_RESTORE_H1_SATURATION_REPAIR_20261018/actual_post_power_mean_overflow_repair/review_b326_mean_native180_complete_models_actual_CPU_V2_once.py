"""Consume only actually returned native-only full models; no production or remote connection."""
from pathlib import Path
import os,sys,json,time,hashlib,traceback
os.environ['CUDA_VISIBLE_DEVICES']=''
import torch
B=Path(__file__).resolve().parent;R=B/'reports';W=B.parent;sys.path.insert(0,str(W/'MOD4_H1_FLAT_JUMP_FULLSTATE_REWARD_NATIVE_ADMISSION_20261016'))
from review_H1_complete_native_models_source_and_admission_local_CPU_once import eq,tensors
H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 v=json.loads((R/'B326_MEAN_NATIVE_COMPLETE_TERMINAL_METADATA_MERGED_V2_COLLECTION_ACTUAL.json').read_bytes());prep=json.loads((R/'B326_MEAN_OVERFLOW_NATIVE_PAYLOAD_CPU_PREPARED_ACTUAL.json').read_bytes());spec=prep['spec'];source=B/'payload_h1_native/job0/source/H1_final10_protected.pt';assert H(source)==spec['source_SHA'];assert v['parent_terminal_observed'] and not v['actual_own_processes'];rows=v['rows'];end=rows['NATIVE_ONLY_PARENT_EXIT_ACTUAL.json'];final=rows['NATIVE_ONLY_FINAL_ACTUAL.json'];assert end['all_actual_own_GPU_children_waited'] and end['private_GPU_fcntl_released_if_acquired'] and end['passed_native_CPU'] and not end['original_error'];assert final['passed_native_GPU_and_full_CPU'] and final['actual_GPU_worker_EXIT0'] and final['no_production_GO_or_PPO_or_canonical_charge'];cpu=final['native_CPU']['value'];assert cpu['passed'] and cpu['source_SHA']==spec['source_SHA'] and cpu['controls']==180 and cpu['callbacks']==720 and cpu['all_policy_rows']==3600000 and cpu['all_physical_rows']==14400000
 s=torch.load(source,map_location='cpu',weights_only=False);rng=torch.get_rng_state().clone();checked=[]
 for row in v['models']:
  p=Path(row['local_path']);assert row['twohost_complete_SHA'] and p.stat().st_size==row['bytes'] and H(p)==row['SHA'];ck=torch.load(p,map_location='cpu',weights_only=False);c=[0,0];tensors(ck,c);assert c==[199,105]
  for g in ('actor_state_dict','critic_state_dict','optimizer_state_dict'):assert eq(s[g],ck[g])
  assert {int(z['step']) for z in ck['optimizer_state_dict']['state'].values()}=={645620}
  startup=p.name=='own_source_full20k_startup0.pt'
  if startup:assert torch.equal(ck['sensor_DR_state']['episode'],s['sensor_DR_state']['episode']+1) and not ck['H1_public_request_phase_state']['phase']['tensors']['age_control'].any()
  checked.append(dict(**row,all199tensor105float_finite=True,source_actor9_STD_critic8_all17Adam_literalexact=True,initial_source_episode_plus_one=bool(startup)))
 assert len(checked)>=2 and torch.equal(rng,torch.get_rng_state()) and not torch.cuda.is_initialized()
 out=dict(epoch=time.time(),passed_complete_native180_allrow_remote_and_full_model_local_CPU=True,source_SHA=spec['source_SHA'],source_all17Adam645620=True,models=checked,actual_remote_allrow_CPU=cpu,parent_exit=end,original_actual_private_resource_receipt=rows.get('job0/native_ACTUAL_GPU_RAM_DURABLE_RESOURCE.json'),zero_PPO_zero_charge_no_GO_or_writer=True,not_jump_skill_or_new_production_PASS=True,new_TASK_current_GPU_and_owned24_bound_separate_historical_original_task_retained=True,execution_backend_and_actual_source_bound_by_new_manifest_spec_and_target_resource_receipts=True,never_rewrote_live_TASK_or_model_to_hide_legacy_labels=True,CPU_RNG_unchanged0CUDA0optimizer=True)
 with (R/'NEW_B326_MEAN_NATIVE180_TWO_COMPLETE_MODELS_SOURCE_EXACT_LOCAL_CPU_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(out,f,indent=2)
 print(json.dumps(dict(native180_full_model_CPU=True,models=len(checked),PPO_updates=0,source_Adam=645620)),flush=True)
if __name__=='__main__':
 try:main()
 except BaseException:
  with (R/('LATEST_H1_NATIVE_COMPLETE_MODELS_CPU_V2_ORIGINAL_ERROR_'+str(time.time_ns())+'.json')).open('x',encoding='utf8') as f:json.dump(dict(epoch=time.time(),error=traceback.format_exc(),no_GPU_replay_or_automatic_retry=True),f,indent=2)
  raise
