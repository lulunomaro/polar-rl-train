"""Consume only a completed local collection; no runtime mutation or missing-model PASS."""
from pathlib import Path
import os,sys,json,time,hashlib,traceback
os.environ['CUDA_VISIBLE_DEVICES']=''
import torch
B=Path(__file__).resolve().parent;R=B/'reports';W=B.parent
sys.path.insert(0,str(W/'MOD4_H1_FLAT_JUMP_FULLSTATE_REWARD_NATIVE_ADMISSION_20261016'))
from review_H1_complete_native_models_source_and_admission_local_CPU_once import eq,tensors
H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 path=R/'H1_NEW_NATIVE_FIRST_AND_RECOVERY85_NATIVE_ONLY_COMPLETE_OR_PENDING_BOUND_COLLECTION_ACTUAL.json';assert path.is_file();v=json.loads(path.read_bytes());prep=json.loads((R/'H1_BOUNDED_ONE_PAID_SLOT_RECOVERY_NATIVE_ONLY_OWNER_HTTP_CPU_ACTUAL.json').read_bytes());rng=torch.get_rng_state().clone();torch.set_num_threads(2);out={}
 for key in ('h1','recovery'):
  spec=prep['specs'][key];source=B/'payload'/key/'job0/source'/spec['source_filename'];assert H(source)==spec['source_SHA'];s=torch.load(source,map_location='cpu',weights_only=False);rows=v['downloaded_models'].get(key,[]);ck={};counts={}
  for r in rows:
   p=Path(r['local_path']);assert p.stat().st_size==r['bytes'] and H(p)==r['SHA'] and r['twohost_complete_SHA'];x=torch.load(p,map_location='cpu',weights_only=False);n=[0,0];tensors(x,n);ck[r['kind']]=x;counts[r['kind']]=n
  if key=='h1':
   if 'immutable_first' not in ck or 'immutable_startup0' not in ck:
    out[key]=dict(real_first_complete_local_CPU_verified=False,actual_collected_kinds=list(ck),pending_not_failure_or_PPOpositive=True);continue
   z=ck['immutable_startup0'];first=ck['immutable_first'];assert counts['immutable_first']==[199,105]
   for g in ('actor_state_dict','critic_state_dict','optimizer_state_dict'):assert eq(s[g],z[g])
   assert {int(x['step']) for x in first['optimizer_state_dict']['state'].values()}=={643720} and {int(x['step']) for x in z['optimizer_state_dict']['state'].values()}=={643700};changes={g:[n for n in s[g] if not eq(s[g][n],first[g][n])] for g in ('actor_state_dict','critic_state_dict')};assert len(changes['actor_state_dict'])==9 and len(changes['critic_state_dict'])==8
   assert torch.equal(z['sensor_DR_state']['episode'],s['sensor_DR_state']['episode']+1) and not z['H1_public_request_phase_state']['phase']['tensors']['age_control'].any();assert first['owned_H1_completed_updates']==1 and first['failed_partial_prefix'] is False and first['owned_H1_learning_task']['max_completed_updates']==24
   cpu=next(x['value'] for x in v[key]['files'] if x['path'].endswith('/H1_PRELAUNCH_V2_NATIVE180_ALL_ROWS_CPU_ADMITTED.json'));assert cpu['passed'] and cpu['source_SHA']==spec['source_SHA'] and cpu['controls']==180 and cpu['callbacks']==720
   native=ck.get('native_complete');assert native is not None
   for g in ('actor_state_dict','critic_state_dict','optimizer_state_dict'):assert eq(s[g],native[g])
   row=next(x for x in rows if x['kind']=='immutable_first');out[key]=dict(real_first_complete_local_CPU_verified=True,first=row,whole_model_counts=counts['immutable_first'],source9STD8critic17Adam_startup0_literalexact=True,all17Adam643700_to643720=True,all17_actorcritic_changes=changes,source_episode_exact_plus1_phaseage0=True,own_new_native180_full_CPU_passed=True,native_core_and_optimizer_unchanged=True,first24control480000productionenvsteps=True,H1_cap1800_max24updates_reserve8GiB_no_future_FINAL_claim=True,not_jump_skill_qualification=True)
  else:
   final=next((x['value'] for x in v[key]['files'] if x['path'].endswith('/NATIVE_ONLY_FINAL_ACTUAL.json')),None)
   if 'native_complete' not in ck or not final:
    out[key]=dict(native_only_full_model_and_CPU_verified=False,actual_collected_kinds=list(ck),pending_no_PPO_or_skill=True);continue
   assert final['passed_native_GPU_and_full_CPU'] and final['source_SHA']==spec['source_SHA'];native=ck['native_complete'];assert counts['native_complete']==[173,96]
   for g in ('actor_state_dict','critic_state_dict','optimizer_state_dict'):assert eq(s[g],native[g])
   assert {int(x['step']) for x in native['optimizer_state_dict']['state'].values()}=={657660}
   out[key]=dict(native_only_full_model_and_CPU_verified=True,native=next(x for x in rows if x['kind']=='native_complete'),all_source9STD8critic17Adam_core_literalexact=True,all17Adam657660_no_updates=True,whole_model_counts=counts['native_complete'],actual_parent_final=final,zero_PPO_zero_charge_no_selfrescue_skill_PASS=True)
 assert torch.equal(rng,torch.get_rng_state()) and not torch.cuda.is_initialized();report=dict(epoch=time.time(),H1_real_first_complete_local_CPU_positive=out['h1'].get('real_first_complete_local_CPU_verified',False),experts=out,recovery_native_only_never_PPO_positive=True,E2_no_new_paid_worker_or_GO=True,all_missing_or_pending_preserved_not_faked=True,CPU_RNG_unchanged0CUDA0optimizer=True,not_all_three_learning_or_course_complete=True)
 p=R/'NEW_H1_FIRST_AND_RECOVERY85_NATIVE_ONLY_COMPLETE_MODELS_LOCAL_CPU_ACTUAL.json'
 with p.open('x',encoding='utf8') as f:json.dump(report,f,indent=2)
 print(json.dumps(dict(H1_first_CPU_positive=report['H1_real_first_complete_local_CPU_positive'],recovery_native_only_CPU=out['recovery'].get('native_only_full_model_and_CPU_verified',False))),flush=True)
if __name__=='__main__':
 try:main()
 except BaseException:
  with (R/('M_H1_FIRST_NATIVEONLY_MODEL_CPU_ORIGINAL_ERROR_'+str(time.time_ns())+'.json')).open('x',encoding='utf8') as f:json.dump(dict(epoch=time.time(),error=traceback.format_exc(),no_GPU_or_old_once_replay=True),f,indent=2)
  raise
