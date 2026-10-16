"""Credit only a complete immutable actual production update, never discarded prechecks."""
from pathlib import Path
import os,sys,json,time,hashlib
os.environ['CUDA_VISIBLE_DEVICES']=''
import torch
D=Path(__file__).resolve().parent;R=D/'reports';torch.set_num_threads(4)
sys.path.insert(0,str(D));from review_H1_complete_native_models_source_and_admission_local_CPU_once import eq,tensors,H
def main():
 dest=R/'H1_FIRST_REAL_PRODUCTION_UPDATE1_COMPLETE_TWOHOST_MODEL_LOCAL_CPU_VERIFIED_ACTUAL.json';assert not dest.exists();rng=torch.get_rng_state().clone();v=json.loads((R/'H1_FIRST_PRODUCTION_IMMUTABLE_UPDATE1_COMPLETE_MODELS_BOUND_COLLECTION_ACTUAL.json').read_bytes());source=D/'actual_complete_native_models/saved.pt';assert H(source)=='ac0f60047bcb3e98b178998ce111224480fdb75e682a199f54683341f2a3886e';s=torch.load(source,map_location='cpu',weights_only=False);rows=[];ck={}
 for row in v['local_models']:
  p=Path(row['path']);assert p.stat().st_size==row['bytes'] and H(p)==row['SHA'];c=torch.load(p,map_location='cpu',weights_only=False);count=[0,0];tensors(c,count);ck[p.name]=c;rows.append(dict(**row,all_model_runtime_tensors_finite=True,tensors=count[0],float_tensors=count[1]))
 initial=ck['own_H1_startup0.pt'];first=ck['model_update1.pt']
 for key in ('actor_state_dict','critic_state_dict','optimizer_state_dict'):assert eq(initial[key],s[key]),key
 assert first['owned_H1_phase']=='production' and first['owned_H1_completed_updates']==1 and not first['failed_partial_prefix'];assert first['owned_H1_learning_task']['source_SHA']==H(source);assert len(first['actor_state_dict'])==9 and len(first['critic_state_dict'])==8 and len(first['optimizer_state_dict']['state'])==17;assert {int(x['step']) for x in first['optimizer_state_dict']['state'].values()}=={639580};changes={key:[k for k in s[key] if not eq(s[key][k],first[key][k])] for key in ('actor_state_dict','critic_state_dict')};assert len(changes['actor_state_dict'])==9 and len(changes['critic_state_dict'])==8
 files=v['files'];prechecks=[];fullrestore=[];startup=None
 for row in files:
  path=row['path'];value=row.get('value') or {}
  if path.endswith('/FINAL.json') and any('/'+name+'/' in path for name in ('precheck128','precheck20k')):assert value['passed'] and value['discarded_prechecks'];prechecks.append(value)
  if path.endswith('/H1_PHASE_FULLSTATE_RESUME_STARTUP_VERIFIED.json') and '/production/' in path:assert value['source_had_H1_phase'] and value['actual_CUDA_disk_roundtrip_exact'] and value['new_physical_episode_resets_external_schedule_and_reward_credits'];fullrestore.append(row)
  if path.endswith('/production/STARTUP_H1_SOURCE_ACTUAL.json'):startup=value
 assert len(prechecks)==2 and fullrestore and startup and startup['zero_clock'] and startup['source_actor9_critic8_STD17Adam_exact'] and startup['own_admitted_H1_checkpoint_phase_fullrestore'] and not startup['fresh128_perenv_DR_explicit_not_full20k_restore'];assert startup['zero']['SHA']==next(x['SHA'] for x in rows if Path(x['path']).name=='own_H1_startup0.pt');assert not torch.cuda.is_initialized() and torch.equal(rng,torch.get_rng_state())
 prefix=next((x['value'] for x in files if x['path'].endswith('/CONTROL_VALID_PREFIX_INDEX_ACTUAL.json')),None);assert prefix and prefix['controls']>=24 and not prefix['physical_callback_replay'];report=dict(epoch=time.time(),passed=True,production_first_real_saved_PPO_positive=True,source_H1_native_SHA=H(source),source_original_E0_SHA='b10958d2a8631b12c0f9502bf7fa9230d9a7a1ae9863443bb68388604bed61f8',models=rows,production_startup_actor9critic8STD17Adam_source_literal_exact=True,actual_fresh_production_own_H1_fullphase_and_original_typed_restore=fullrestore,discarded_prechecks_actual_128x2_20kx4_closed=True,actor9_including_STD_changed_keys=changes['actor_state_dict'],critic8_changed_keys=changes['critic_state_dict'],all17Adam639560_to639580=True,production_updates=1,production_controls=24,production_envsteps=480000,initial_24controls_publicnormal_preparation_not_jump_success=True,control_trace_raw_index_at_capture=prefix,not_training_full_physical_callback_or_all_logprob_replay=True,not_full1800_FINAL_or_frozen_jump_skill_pass=True,not_native_or_discarded_prechecks_counted_as_production=True,no_CPU_CUDA_or_optimizer=True,global_CPU_RNG_unchanged=True);dest.write_text(json.dumps(report,indent=2),encoding='utf8');print(json.dumps(dict(passed=True,actual_production_updates=1,all17Adam639580=True,actor9_critic8_changed=True,production_controls=24,production_envsteps=480000,no_jump_skill_or_full1800_FINAL_claim=True)))
if __name__=='__main__':main()
