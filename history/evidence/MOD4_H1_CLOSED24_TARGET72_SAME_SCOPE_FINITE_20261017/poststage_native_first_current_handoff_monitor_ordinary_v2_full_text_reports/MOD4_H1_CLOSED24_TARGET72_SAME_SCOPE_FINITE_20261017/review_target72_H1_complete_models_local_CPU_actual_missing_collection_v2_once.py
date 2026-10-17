"""Only actually collected target72 native/first full PTs can earn separate CPU evidence."""
from pathlib import Path
import os,sys,json,time,hashlib,traceback
os.environ['CUDA_VISIBLE_DEVICES']=''
import torch
B=Path(__file__).resolve().parent;R=B/'reports';W=B.parent;sys.path.insert(0,str(W/'MOD4_H1_FLAT_JUMP_FULLSTATE_REWARD_NATIVE_ADMISSION_20261016'))
from review_H1_complete_native_models_source_and_admission_local_CPU_once import eq,tensors
H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 v=json.loads((R/'H1_TARGET72_MISSING_NATIVE_FIRST_COMPLETE_MERGED_BOUND_COLLECTION_V2_ACTUAL.json').read_bytes());prep=json.loads((R/'H1_CLOSED24_TARGET72_SAME_SCOPE_PAYLOAD_FULL_CPU_PREPARED_ACTUAL.json').read_bytes());spec=prep['specs']['h1'];src=B/'payload/h1/job0/source'/spec['source_filename'];assert H(src)==spec['source_SHA'];rng=torch.get_rng_state().clone();torch.set_num_threads(2);s=torch.load(src,map_location='cpu',weights_only=False);cks={};counts={}
 for row in v['downloaded_models']:
  p=Path(row['local_path']);assert row['twohost_complete_SHA'] and p.stat().st_size==row['bytes'] and H(p)==row['SHA'];x=torch.load(p,map_location='cpu',weights_only=False);c=[0,0];tensors(x,c);assert c==[199,105];cks[row['kind']]=x;counts[row['kind']]=c
 cpu=next((x['value'] for x in v['h1']['files'] if x['path'].endswith('/H1_PRELAUNCH_V2_NATIVE180_ALL_ROWS_CPU_ADMITTED.json')),None);native=False;first=False;change={}
 if cpu and 'native_complete' in cks:
  assert cpu['passed'] and cpu['source_SHA']==spec['source_SHA'] and cpu['controls']==180 and cpu['callbacks']==720 and cpu['all_policy_rows']==3600000 and cpu['all_physical_rows']==14400000
  for kind in ('native_complete','native_startup0'):
   if kind in cks:
    for g in ('actor_state_dict','critic_state_dict','optimizer_state_dict'):assert eq(s[g],cks[kind][g])
    assert {int(z['step']) for z in cks[kind]['optimizer_state_dict']['state'].values()}=={644180}
  native=True
 if 'immutable_first' in cks and 'immutable_startup0' in cks:
  assert native;z=cks['immutable_startup0'];p=cks['immutable_first']
  for g in ('actor_state_dict','critic_state_dict','optimizer_state_dict'):assert eq(s[g],z[g])
  assert {int(a['step']) for a in p['optimizer_state_dict']['state'].values()}=={644200} and {int(a['step']) for a in z['optimizer_state_dict']['state'].values()}=={644180};change={g:[n for n in s[g] if not eq(s[g][n],p[g][n])] for g in ('actor_state_dict','critic_state_dict')};assert len(change['actor_state_dict'])==9 and len(change['critic_state_dict'])==8
  assert torch.equal(z['sensor_DR_state']['episode'],s['sensor_DR_state']['episode']+1) and not z['H1_public_request_phase_state']['phase']['tensors']['age_control'].any();assert p['owned_H1_completed_updates']==1 and not p['failed_partial_prefix'] and p['owned_H1_learning_task']['max_completed_updates']==24;first=True
 assert torch.equal(rng,torch.get_rng_state()) and not torch.cuda.is_initialized();out=dict(epoch=time.time(),H1_new72_backend_own_native180_full_models_allrow_CPU_verified=native,H1_real_immutable_first_complete_local_CPU_verified=first,all_complete_models=v['downloaded_models'],counts=counts,source_startup0_core9STD8critic17Adam_literalexact=first,first_all17Adam644180_to644200=first,all17_actorcritic_actual_changes=change,source_episode_plus1_phaseage0=first,first24controls480000productionenvsteps=first,actual_native_CPU=cpu,missing_models_or_first_are_pending_not_PASS=True,target72_GPU0_not_source210=True,E2_recovery_no_new_paid_workers=True,not_jump_skill_or_final_or_all_three_PPO=True,CPU_RNG_unchanged0CUDA0optimizer=True)
 with (R/'H1_TARGET72_NATIVE_FIRST_COMPLETE_MODELS_LOCAL_CPU_V2_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(out,f,indent=2)
 print(json.dumps(dict(native_full_CPU=native,first_complete_PPO_CPU=first,source_step=644180,first_step=644200 if first else None)),flush=True)
if __name__=='__main__':
 try:main()
 except BaseException:
  with (R/('H1_TARGET72_MODELS_CPU_V2_ORIGINAL_ERROR_'+str(time.time_ns())+'.json')).open('x',encoding='utf8') as f:json.dump(dict(epoch=time.time(),error=traceback.format_exc(),no_GPU_or_old_task_replay=True),f,indent=2)
  raise
