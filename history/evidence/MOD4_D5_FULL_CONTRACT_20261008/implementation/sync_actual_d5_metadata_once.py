"""Update actual stage metadata after verified deployment; no runtime or budget mutation."""
from pathlib import Path
import json,hashlib,sys,time
D=Path(__file__).resolve().parent;R=D/'reports';assert not (R/'D5_ACTUAL_METADATA_SYNCED.json').exists()
read=lambda p:json.loads(p.read_text(encoding='utf8'));sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
MASTER='812a4bedd04834a98a7c9391609d0056b47c47398e0ecdda9c61e61c6466d05b';REPO=D.parent/'polar-rl-train'
assert sha(REPO/'history/plans/MOD4_MOE_MASTER_PLAN.md')==MASTER
a=read(R/'D5_FORMAL_OWN_SOURCE_VERIFIED.json');git=read(R/'D5_FULL_CONTRACT_GIT_RECORDED.json');v=read(R/'D4_CLOSEOUT_D5_FORMAL_REVIEW.json')
assert git['remote_main_tag_peeled_verified'] and not git['push_pending']
sys.path.insert(0,str(D.parent/'MOD4_AUTONOMY_SLEEP_20261003'));from remote_io import connect
c=connect();central='/home/egde/rl_candidates/MOD4_MOE_PLAN_EXECUTION_20261007/reports';root='/home/egde/rl_candidates/MOD4_D5_FULL_CONTRACT_20261008/reports'
try:
 with c.open_sftp() as f:
  def get(n):return json.loads(f.open(central+'/'+n).read())
  def put(n,o,where=central):
   raw=o.encode('utf8') if isinstance(o,str) else json.dumps(o,ensure_ascii=False,indent=2).encode('utf8');p=where+'/'+n;t=p+'.d5metadata_tmp'
   with f.open(t,'wb') as out:out.write(raw)
   f.posix_rename(t,p);assert f.open(p).read()==raw
  approval=get('PLAN_APPROVAL.json');tracks=get('EXECUTION_TRACKS.json');oldcurrent=get('MOE_PLAN_EXECUTION_CURRENT.json');d5=get('NEXT_D5_FORCE_STROKE_WORK_ORDER.json');handoff=f.open(central+'/LATEST_HANDOFF.md').read().decode('utf8')
  assert approval['approved'] and approval['approved_plan_sha256']==MASTER and 'S2' in approval['allowed_stages']
  for n,o in [('PLAN_APPROVAL.json',approval),('EXECUTION_TRACKS.json',tracks),('MOE_PLAN_EXECUTION_CURRENT.json',oldcurrent),('NEXT_D5_FORCE_STROKE_WORK_ORDER.json',d5),('LATEST_HANDOFF.md',handoff)]:
   backup=n.rsplit('.',1)[0]+'_BEFORE_D5_FULL_DEPLOYMENT_20261008.'+n.rsplit('.',1)[1]
   try:f.stat(central+'/'+backup)
   except FileNotFoundError:put(backup,o)
  for n in ('D4_CLOSEOUT_D5_FORMAL_REVIEW.json','D4_CLOSEOUT_D5_FORMAL_REPORT.md','D5_FORMAL_OWN_SOURCE_VERIFIED.json',
   'D5_CURRENT_ACTUAL.json','D5_FROZEN_BEHAVIOR_PACKAGES.json','D5_CLOSEDLOOP_PACKAGE_PUBLISHED.json','D5_FULL_CONTRACT_GIT_RECORDED.json',
   'NEXT_D6_DAMPING_FRICTION_WORK_ORDER.json','MOD4_D4_CHECKPOINT_INDEX.json','D5_FORMAL_FIRST_READER_ERRORS.json'):
   value=(R/n).read_text(encoding='utf8');put(n,value);put(n,value,root)
  machine=REPO/'history/plans/MOD4_S2_D5_SPRING_STIFFNESS_PRESSURE.json'
  for n in ('MOD4_S2_D5_SPRING_STIFFNESS_PRESSURE.json','MOD4_S2_D5_SPRING_STIFFNESS_PRESSURE.md'):put(n,(REPO/'history/plans'/n).read_text(encoding='utf8'))
  approval.setdefault('execution_events',{})['MOD4-S2-D5-SPRING-STIFFNESS-PRESSURE-001']=dict(epoch=a['epoch'],
   status='ACTUAL_FULLSCALE_PPO_PASSED_AND_STABLE_LEARNING',existing_S2_authorization_only=True,new_human_approval_inferred=False,
   master_plan_changed=False,implementation_contract_SHA=sha(machine),actual_root=root.rsplit('/',1)[0],source255=True,Git=git)
  current=dict(epoch=a['epoch'],root=root.rsplit('/',1)[0],actual_phase=a['phase'],parent=a['owner'],guardian=a['guardian'],trainer=a['trainer'],
   source=a['source'],run=a['run'],active_log=a['active_log'],deadline_epoch=a['deadline_epoch'],own_current_save=a['checkpoint'],
   own_PID_bound_receipt=a['own_receipt'],source_count=a['source_count'],snapshots=a['snapshots'],live_health=a['live_health'],live_health_is_not_final=True,
   actual_D5_spring_startup=a['spring_startup'],actual_D4_action_startup=a['action_startup'],actual_PPO_iteration_log_count=a['PPO_iteration_log_count'],
   current_expert='E0',architecture='A0',plan_stage='S2 D5 independent episode stiffness.9-1.1 with D0-D4 retained',
   no_repeated45min_clock_trial=True,no_wait_for3060_to_continue=True,stable_block_seconds=7200,maximum_window_seconds=21600,
   D5_behavior_pending=True,D4_final_block3_ordinary465_preserved=True,D4_final_behavior_pending='3' not in v['D4_paired_later_review']['later_blocks'],
   D4_later_behavior=v['D4_paired_later_review']['later_blocks'],selected_behavior_source29690=True,
   hardware_force_stroke_calibration_available=False,SDK_effort_is_approximation=True,new_budget_seconds=0,all_courses_finished=False,Git=git)
  tracks['epoch']=a['epoch'];tracks['learning']=current
  tracks['evaluation'].update(epoch=a['epoch'],D5_true_closedloop_package=v['D5_packages'],D5_behavior_pending=True,
   evaluator_current='D:/MOD4_async_eval/closure_episode_clock2500_v15/eval_worker_spring_audit_review.py',
   demand_task='MOD4_AsyncFrozenEvaluation_v15_spring_audit_review',no_periodic_or_boot_trigger=True,shared_single_GPU_lock=True,
   canonical_write_authority=False,training_launch_authority=False,production255_runtime_unchanged_by_readers=True,
   future_D5_world_corrected_directly=True,D4_later_review=v['D4_paired_later_review']['later_blocks'],
   no_wait_for_evaluation_to_continue_validated_training=True)
  tracks['budget'].update(current_snapshot=a['budget'],snapshot_epoch=a['epoch'],actual_tail_adjusted_remaining_seconds=a['actual_tail_adjusted_remaining_seconds'],new_budget_seconds=0)
  d5.update(epoch=a['epoch'],D5_learning_executor_deployed=True,actual_root=current['root'],actual_phase=a['phase'],actual_source=a['source'],
   complete_native20k_and128x2_20kx4_PPO_passed=True,preflight_weights_discarded=True,parameter_lifecycle_resume_verified=True,
   spring_profile='gas_stiffness_independent_episode_090_110_v1',native_and_PPO_proof='D4_CLOSEOUT_D5_FORMAL_REVIEW.json',
   nominal_model_unchanged=True,measured_hardware_force_stroke_available=False,scope_does_not_claim_real_force_certification=True,Git=git,
   next_required=['Actual same-platform D5 baseline/candidate retention and pressure readback/recipes/assignments','Finish bounded window and advance D6 using actual behavior-reviewed source and safe boundary'])
  tracks['next_D5_preparation']=d5;tracks['next_D6_preparation']=read(R/'NEXT_D6_DAMPING_FRICTION_WORK_ORDER.json')
  for n,o in [('PLAN_APPROVAL.json',approval),('EXECUTION_TRACKS.json',tracks),('MOE_PLAN_EXECUTION_CURRENT.json',current),('NEXT_D5_FORCE_STROKE_WORK_ORDER.json',d5)]:
   put(n,o);(R/n).write_text(json.dumps(o,ensure_ascii=False,indent=2),encoding='utf8')
  heading=(R/'D4_CLOSEOUT_D5_FORMAL_REPORT.md').read_text(encoding='utf8')
  heading+='\nActual proc/cwd/argv/start and own phase/receipt override all locator PIDs. New supervise_d5_path_review.py already executed; rejected supervise_d5_full_contract.py and every oldstage/launch/record/package/SDK/PPO/metadata/once/main/resume must never rerun. Reusable read_d5_actual.py/verify_d5_formal_own_source.py read actual stage; current ownCPU89 is not oldCPU88/84. Formal health absent at early startup is pending, not task0 or failure. D5 preflight/native actual complete; do not duplicate or reuse discarded weights. Three<=2h automatically continue, publish70anchor and75-bN trueD5 flat/spin/world, no3060wait. D5_REVIEW_READY/E0_D5_saved_review_ready with noactive and planned parentguardian exit is a safe review boundary, not failure/fullcoursefinished. Positional source29690 remains explicit; do not hot-swap to30745 or directorymax. Review sustained ordinary rates/final30745 retention honestly. Uncalibrated engineering pressure only. S8 still separate approval; MoEgate untrained. Canonical828000s/230h/sixextensions once,newbudget0; actual tail subtract. No ledgercopy/clear/repeatedsettlements. Only host15s guardian/save25, desktopevery2h healthquiet. Monitor stays ACTIVE; no hourly/5minSSH/ping/newRich or autoextra time.\n\n# Previous handoff retained\n\n'
  put('LATEST_HANDOFF.md',heading+handoff)
  proof=dict(epoch=time.time(),metadata_only=True,runtime_GPU_PPO_canonical_writes=0,master_plan_SHA_unchanged=MASTER,Git=git)
  put('D5_ACTUAL_METADATA_SYNCED.json',proof);put('D5_ACTUAL_METADATA_SYNCED.json',proof,root)
  (R/'D5_ACTUAL_METADATA_SYNCED.json').write_text(json.dumps(proof,indent=2),encoding='utf8');print(json.dumps(proof))
finally:c.close()
