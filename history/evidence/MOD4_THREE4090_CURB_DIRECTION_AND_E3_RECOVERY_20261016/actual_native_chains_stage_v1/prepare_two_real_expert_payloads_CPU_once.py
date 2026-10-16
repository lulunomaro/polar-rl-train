from pathlib import Path
import os,sys,shutil,json,hashlib,ast,time
os.environ['CUDA_VISIBLE_DEVICES']=''
import torch
D=Path(__file__).resolve().parent;W=D.parent;Q=D/'payload';OLD=W/'MOD4_CURB140_E2_58_HEALTHY_CONTINUATION_ADMISSION_20261016';R=D/'reports'
def H(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 assert not (R/'TWO_NEW_EXPERTS_FULL_SOURCE_CONTRACT_CPU_ACTUAL.json').exists();rng=torch.get_rng_state().clone();rt=Q/'recovery/job0/runtime/isaac/mod4';base=rt/'train_H1_fullstate_admission_v1.py';s=base.read_text('utf8');s=s.replace('from h1_fullstate_environment_v1 import H1FullstateEnv as Mod4Env','from e3_recovery_runtime_v1 import RecoveryEnv as Mod4Env').replace('from h1_reward_scope_v1 import configure as configure_h1_rewards','from e3_recovery_runtime_v1 import configure as configure_h1_rewards').replace('from h1_fullstate_checkpoint_v1 import resume_h1_new_episode as resume_chassis_pd_new_episode','from e3_fullstate_checkpoint_v1 import resume as resume_chassis_pd_new_episode').replace('from h1_fullstate_checkpoint_v1 import install_h1_save_contract as install_chassis_pd_save_contract','from e3_fullstate_checkpoint_v1 import install as install_chassis_pd_save_contract');(rt/'train_E3_fullstate_v1.py').write_text(s,encoding='utf8')
 p=rt/'e3_recovery_runtime_v1.py';s=p.read_text('utf8').replace(",all_term_dones=self.termination_manager._term_dones.clone()",'');p.write_text(s,encoding='utf8')
 task=dict(id='E3_PUBLIC_RECOVERY_12LEGAL_FALLS_FULL20K_NATIVE336',kind='E3_PUBLIC_RECOVERY',source_SHA=H(Q/'recovery/job0/source/E0_full_source.pt'),source_Adamstep=639560,GPU_UUID='GPU-c27eecbd-6838-7290-1cd2-37e34522213d',num_envs=20000,seed=20260928,controls=336,callbacks=1344,public_mode3_controls=300,then_normal=True,normal_case_oneof13=True,legal_roll_pitch_degrees=[-90,-60,-30,30,60,90],new_reward='Unit coefficient capped upright-peak increase plus one stable-recovery event; rate divided by actual control dt',soft_task_terms_only=['bad_orientation','base_contact'],original_closure_mimic_timeout_unknown_nonfinite_guards_preserved=True,original_energy_torque_actionrate_hardware_preserved=True,explicit_height_vertical_masks_only_public_rescue_rows=True,approved_for_PPO=False,template_approved_GPU=False,max_parent_seconds=1800,exit_headroom_seconds=300);(Q/'recovery/job0/TASK.json').write_text(json.dumps(task,indent=2),encoding='utf8')
 sys.path.insert(0,str(rt));from e3_public_recovery_phase_v1 import RecoveryPhase
 phase=RecoveryPhase(26,'cpu');phase.begin();assert phase.mode().tolist()==([3]*12+[0])*2
 for z in (1.,0.,-1.,1.,-1.):phase.update(torch.full((26,),z),torch.ones(26),torch.ones(26));phase.begin()
 before=phase.state_dict();p=R/'E3_CPU_PHASE_ROUNDTRIP_FIXTURE.pt';torch.save(before,p);phase.load_state_dict(torch.load(p,map_location='cpu',weights_only=False));ids=torch.tensor([1,3]);old={k:v.clone() for k,v in phase.state_dict()['tensors'].items()};phase.reset(ids);keep=torch.ones(26,dtype=torch.bool);keep[ids]=False
 for k,v in old.items():assert torch.equal(getattr(phase,k)[keep],v[keep])
 bad=0
 for key,val in [('age',torch.full((26,),-1,dtype=torch.long)),('peak',torch.full((26,),2.)),('recipe',torch.full((26,),13,dtype=torch.long))]:
  fresh=RecoveryPhase(26,'cpu');d=fresh.state_dict();d['tensors'][key]=val
  try:fresh.load_state_dict(d)
  except AssertionError:bad+=1
  else:raise AssertionError('Invalid phase accepted')
 # Reuse exact proven finite cohort functions, separate new socket/root. Per-GPU lock admission added below.
 cohort=(OLD/'training_payload/curb/cohort_finite.py').read_text('utf8').replace('PORT=29736','PORT=29742').replace("'e2'","'recovery'")
 cohort=cohort.replace("str(B/('native_admission_worker.py' if phase=='native' else 'production_worker.py'))","str(B/(('native_admission_worker.py' if phase=='native' else 'production_worker.py') if key=='curb' else 'recovery_worker.py'))")
 cohort=cohort.replace("v['controls']==144 and v['callbacks']==576","v['controls']==cfg['native_controls'] and v['callbacks']==cfg['native_controls']*4").replace("v.get('controls')==144 and v.get('callbacks')==576","v.get('controls')==cfg['native_controls'] and v.get('callbacks')==cfg['native_controls']*4")
 cohort=cohort.replace("go['max_parent_seconds']==2700","go['max_parent_seconds']==cfg['max_parent_seconds']")
 cohort=cohort.replace("lock=(owned/'state/finite_environment_validation.lock').open('rb+');p=None","from per_gpu_recovery_resource_v1 import acquire\n lock=acquire(B);p=None")
 a="  while True:\n   try:fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB);break\n   except BlockingIOError:\n    assert time.time()-begun<3600;put(B/'NODE_CURRENT.json',dict(epoch=time.time(),phase=phase,no_old_H1_stop_or_lock_removal=True));send(cfg,dict(key=cfg['key'],phase=phase));time.sleep(5)"
 assert a in cohort;cohort=cohort.replace(a,'  # Actual private GPU1 fcntl and exact existing GPU0 owner were verified by acquire().')
 cohort=cohort.replace("'max_parent_seconds':2700","'max_parent_seconds':g['max_parent_seconds']")
 cohort=cohort.replace("max_parent_seconds=2700))","max_parent_seconds=g['max_parent_seconds']))").replace("a['charged_seconds']<=2700","a['charged_seconds']<=g['max_parent_seconds']")
 cohort=cohort.replace("save_deadline=now+2400,nominal_end_epoch=now+2700,max_parent_seconds=2700","save_deadline=now+spec['max_parent_seconds']-300,nominal_end_epoch=now+spec['max_parent_seconds'],max_parent_seconds=spec['max_parent_seconds']")
 cohort=cohort.replace('Linux_TWO_DISTINCT_CURB35_E2_HEALTHY_CONTINUATIONS_','Linux_CURB35_APPROACH_AND_E3_RECOVERY_').replace("cfg['e2']","cfg['recovery']")
 # Existing owner may still hold the sole accounting locks: native may run, learning waits normally.
 for key in ('curb','recovery'):(Q/key/'cohort_finite.py').write_text(cohort,encoding='utf8')
 frozen=[]
 for key in ('curb','recovery'):
  b=Q/key;source=b/'job0/source'/('CURB140.pt' if key=='curb' else 'E0_full_source.pt');ck=torch.load(source,map_location='cpu',weights_only=False);steps={int(v['step']) for v in ck['optimizer_state_dict']['state'].values()};assert steps=={666140 if key=='curb' else 639560};count=[0,0]
  def walk(x):
   if torch.is_tensor(x):count[0]+=1;count[1]+=int(x.is_floating_point());assert not x.is_floating_point() or torch.isfinite(x).all()
   elif isinstance(x,dict):
    for v in x.values():walk(v)
   elif isinstance(x,(list,tuple)):
    for v in x:walk(v)
  walk(ck);frozen.append(dict(key=key,source_SHA=H(source),source_Adamstep=next(iter(steps)),source_schema_counts=count,native_controls=144 if key=='curb' else 336,max_parent_seconds=2700 if key=='curb' else 1800,exit_headroom_seconds=300,GPU_UUID='GPU-937bdb0b-0d8f-aa3d-a10e-1b24969a5d4e' if key=='curb' else task['GPU_UUID']))
 assert torch.equal(rng,torch.get_rng_state()) and not torch.cuda.is_initialized();out=dict(epoch=time.time(),passed_CPU_only=True,scope='New CURB35 reset-bound command and E3 recovery fullstate candidate',frozen=frozen,phase_schema_negative_count=bad,phase_selected_reset_roundtrip=True,original_canonical_single_owner_wait_old_E2_actual_exit=True,no_native_or_PPO_yet=True,global_CPU_RNG_unchanged0CUDA0optimizer=True)
 (R/'TWO_NEW_EXPERTS_FULL_SOURCE_CONTRACT_CPU_ACTUAL.json').write_text(json.dumps(out,indent=2),encoding='utf8');print(json.dumps(out))
if __name__=='__main__':main()
