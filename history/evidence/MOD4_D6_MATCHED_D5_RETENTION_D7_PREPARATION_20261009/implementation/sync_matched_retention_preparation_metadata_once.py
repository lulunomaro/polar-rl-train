"""Publish reviewed stage indices. Metadata only, never production or budget mutations."""
from pathlib import Path
import json,sys,time,hashlib,base64
D=Path(__file__).resolve().parent;R=D/'reports';F=D.parent/'MOD4_D6_FULL_CONTRACT_20261009';Q=F/'reports'
read=lambda p:json.loads(p.read_text(encoding='utf8'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
receipt=R/'D6_MATCHED_D5_RETENTION_D7_METADATA_SYNCED.json';assert not receipt.exists()
g=read(R/'D6_MATCHED_D5_RETENTION_D7_PREPARATION_GIT_RECORDED.json');a=read(Q/'D6_CURRENT_ACTUAL.json');sdk=read(R/'D7_ACTUAL_INTERFACE_SCOPE_REVIEW.json')
assert g['remote_main_tag_peeled_verified'] and not g['push_pending'] and a['attention'] is None and a['actual_child'] and a['current']
assert a['current']['manifest']['init_checkpoint_sha256']==a['state']['source']['sha256']
assert a['current']['startup']['predecessor_had_gas_damping_state'] and a['current']['startup']['gas_factor_episode_two_CUDA_RNG_restored_exact']
assert read(Q/'D5_FULL_RETENTION_ACTUAL_REVIEW.json')['actual_model_task_data_passed_all18']
sys.path.insert(0,str(D.parent/'MOD4_AUTONOMY_SLEEP_20261003'));from remote_io import connect
sys.path.insert(0,str(D.parent/'MOD4_MOE_PLAN_EXECUTION_20261007'));from eval_remote_io import connect_eval
n=connect();w=connect_eval();central='/home/egde/rl_candidates/MOD4_MOE_PLAN_EXECUTION_20261007/reports';training='/home/egde/rl_candidates/MOD4_D6_FULL_CONTRACT_20261009/reports';prep='/home/egde/rl_candidates/MOD4_D7_COM_PD_PREPARE_20261009/reports'
try:
 ps="$p=@(Get-CimInstance Win32_Process|Where-Object {$_.CommandLine -like '*closure_episode_clock2500_v15*' -and $_.Name -like 'python*'}|Select-Object ProcessId,ParentProcessId,CommandLine,@{n='creation_epoch';e={([DateTimeOffset]$_.CreationDate).ToUnixTimeMilliseconds()/1000}});[pscustomobject]@{processes=$p}|ConvertTo-Json -Depth 5 -Compress"
 _,o,e=w.exec_command('powershell.exe -NoProfile -NonInteractive -EncodedCommand '+base64.b64encode(ps.encode('utf-16le')).decode(),timeout=30);raw=o.read();err=e.read();assert o.channel.recv_exit_status()==0,(raw+err).decode(errors='replace');processes=json.loads(raw)['processes']
 with w.open_sftp() as f:
  root='D:/MOD4_async_eval/closure_episode_clock2500_v15';started=json.loads(f.open(root+'/SDK_PREPARATION_ISOLATION_WORKER_STARTED.json').read())
  own=[p for p in processes if p['ProcessId']==started['pid'] and 'eval_worker_sdk_preparation_isolation.py' in p['CommandLine'] and abs(p['creation_epoch']-started['epoch'])<2];assert len(own)==1
  def optional(name):
   try:return json.loads(f.open(root+'/'+name).read())
   except FileNotFoundError:return None
  attention=optional('SDK_PREPARATION_ISOLATION_WORKER_ATTENTION.json');assert attention is None,attention
  assert hashlib.sha256(f.open(root+'/eval_worker_sdk_preparation_isolation.py').read()).hexdigest()==sha(D/'eval_worker_sdk_preparation_isolation.py')
  evaluator=dict(epoch=time.time(),own_actual_identity=own[0],processes=processes,current_attention=None,state=optional('SDK_PREPARATION_ISOLATION_WORKER_STATE.json'),held_preparation_jobs=optional('SDK_PREPARATION_HELD_JOBS.json'),source='eval_worker_sdk_preparation_isolation.py',demand_task='MOD4_AsyncFrozenEvaluation_v15_sdk_preparation_isolation',no_periodic_or_boot_trigger=True,shared_single_GPU_lock=True,old_attention_files_preserved_as_history=True,canonical_write_authority=False,training_launch_authority=False,per_job_hold_only_explicit10env300control_nonlearning_D7_preparations=True)
 (R/'D7_PREPARATION_EVALUATOR_CURRENT_ACTUAL.json').write_text(json.dumps(evaluator,indent=2),encoding='utf8')
 with n.open_sftp() as f:
  def get(name):return json.loads(f.open(central+'/'+name).read())
  def put(name,obj,where=central):
   raw=obj.encode('utf8') if isinstance(obj,str) else json.dumps(obj,ensure_ascii=False,indent=2).encode('utf8');p=where+'/'+name;t=p+'.d6_matched_d7_preparation_partial'
   with f.open(t,'wb') as out:out.write(raw)
   f.posix_rename(t,p);assert f.open(p).read()==raw
  approval=get('PLAN_APPROVAL.json');tracks=get('EXECUTION_TRACKS.json');old=get('MOE_PLAN_EXECUTION_CURRENT.json');handoff=f.open(central+'/LATEST_HANDOFF.md').read().decode('utf8');order=get('NEXT_D7_COM_PD_WORK_ORDER.json')
  assert approval['approved'] and 'S2' in approval['allowed_stages'] and approval['approved_plan_sha256']==g['master_SHA_unchanged']
  for name,obj in [('PLAN_APPROVAL.json',approval),('EXECUTION_TRACKS.json',tracks),('MOE_PLAN_EXECUTION_CURRENT.json',old),('LATEST_HANDOFF.md',handoff),('NEXT_D7_COM_PD_WORK_ORDER.json',order)]:
   backup=name.rsplit('.',1)[0]+'_BEFORE_D6_MATCHED_D5_RETENTION_D7_PREPARATION_20261009.'+name.rsplit('.',1)[1]
   try:f.stat(central+'/'+backup)
   except FileNotFoundError:put(backup,obj)
  order.update(epoch=time.time(),preparation_root='/home/egde/rl_candidates/MOD4_D7_COM_PD_PREPARE_20261009',actual_chassis_named_index_and_PD_nominal_SDK_accepted=sdk['nominal_actual_interface_accepted'],actual_COM_off_on_SDK_accepted=sdk['COM_actual_off_on_accepted'],SDK_actual_interface_scope=sdk,COM_component_CPU_passed=14,current_frame_fake_backend_CPU_passed=13,stale_full_row_buffer_refresh_CPU_passed=14,PD_component_CPU_passed=12,COM_buffer_on_new_package=read(R/'D7_COM_BUFFER_SDK_PUBLISHED.json'),PD_adapter_randomization_SDK_pending=True,D7_fullcheckpoint_native20k_PPO_executor_deployed=False)
  order['next_required']='Review actual92-on COM SDK; preserve91-on error and successful91-off exact reuse. Build explicit motor PD adapter plus actual reset/CUDA/backend-zero-drive/gain-limit SDK. Separately preserve each approved group, then combined actor/critic/std/optimizer/D1-D6/COM/PD/global-named complete save-resume with first admission explicitly new group and new physical episode. Only genuinely new-scope20k/128x2/20kx4 PPO after natural D6 fullsave/launch retirement/real child exits/settled active-Sactive/two locks; discard preflight weights, charge unique canonical once. No clock45min or repeat valid same-scope evidence. Use actually behavior-reviewed31416 or later genuinely paired source, not highest iter or unreviewed save. No actual learning authority in preparation root.'
  (R/'NEXT_D7_FULL_LEARNING_WORK_ORDER.json').write_text(json.dumps(order,indent=2),encoding='utf8')
  names=('D6_MATCHED_D5_RETENTION_D7_PREPARATION_GIT_RECORDED.json','D6_MATCHED_D5_RETENTION_D7_PREPARATION_REVIEW.json','D6_MATCHED_D5_RETENTION_D7_PREPARATION_REPORT.md','D7_ACTUAL_INTERFACE_SCOPE_REVIEW.json','D7_PREPARATION_EVALUATOR_CURRENT_ACTUAL.json','CHASSIS_COM_TARGET_CPU_PASSED.json','CHASSIS_CURRENT_FRAME_TARGET_CPU_PASSED.json','CHASSIS_BUFFER_REFRESH_TARGET_CPU_PASSED.json','D7_EXPLICIT_PD_TARGET_CPU_PASSED.json','SDK_PREPARATION_ISOLATION_CPU_PASSED.json','D7_COM_BUFFER_SDK_PUBLISHED.json','NEXT_D7_FULL_LEARNING_WORK_ORDER.json')
  for name in names:
   raw=(R/name).read_text(encoding='utf8');put(name,raw);put(name,raw,prep)
  for name in ('D6_CURRENT_ACTUAL.json','D6_ACTUAL_BASELINE_SCOPE_REVIEW.json','D5_FULL_RETENTION_ACTUAL_REVIEW.json'):put(name,(Q/name).read_text(encoding='utf8'))
  put('NEXT_D7_COM_PD_WORK_ORDER.json',order)
  st=a['state'];cur=a['current'];current=dict(old,epoch=a['epoch'],actual_phase=st['phase'],parent=a['actual_owner'],guardian=a['actual_guardian'],trainer=a['actual_child'],source=st['source'],active_log=st['active_log'],deadline_epoch=st['deadline_epoch'],run=cur['run'],own_current_save=cur['checkpoint'],own_PID_bound_receipt=cur['receipt'],own_gas_startup=cur['startup'],own_snapshot_count=cur['snapshot_count'],actual_PPO_log_count=cur['PPO_log_updates'],live_health=cur['live_health'],live_health_is_not_final=True,D6_actual_complete_block2=a['completed']['d6_stable_block2_PASSED'],D6_firstblock_matched_scope=read(Q/'D6_ACTUAL_BASELINE_SCOPE_REVIEW.json'),D5_full_retention_results_pending=False,D5_full_retention_complete=read(Q/'D5_FULL_RETENTION_ACTUAL_REVIEW.json'),D6_behavior_results_pending=True,D6_candidate_pending_blocks=['b2','b3'],D6_firstblock_behavior_complete=True,evaluator_current=evaluator,D7_preparation=order,new_budget_seconds=0,Git=g)
  approval.setdefault('execution_events',{})['D6-MATCHED-D5-RETENTION-D7-PREPARATION-20261009']=dict(epoch=time.time(),existing_S2_authorization=True,new_human_approval_generated=False,master_changed=False,production_GPU_PPO_budget_operations=0,D6_firstblock_behavior_complete=True,D6_own_secondblock_complete=True,D5_18_development_cases_complete=True,D7_preparation_scope=sdk,SDK_short_preparation_failures_held_per_job_not_passed=True,Git=g)
  tracks.update(epoch=a['epoch'],learning=current,next_D7_preparation=order)
  tracks['evaluation'].update(evaluator_current=evaluator,current_attention=None,D5_full_retention_pending=False,D5_full_retention_complete=current['D5_full_retention_complete'],D6_learned_candidate_pending=True,D6_firstblock_learned_candidate_complete=True,D6_pending_candidates=['b2','b3'],D7_interface_scope=sdk,no_wait_for_evaluation_to_continue_validated_training=True,Git=g)
  tracks['budget'].update(snapshot_epoch=a['epoch'],current_snapshot=a['budget'],actual_tail_adjusted_remaining_seconds=a['actual_tail_adjusted_remaining_seconds'],new_budget_seconds=0)
  for name,obj in [('PLAN_APPROVAL.json',approval),('EXECUTION_TRACKS.json',tracks),('MOE_PLAN_EXECUTION_CURRENT.json',current)]:put(name,obj)
  header=(R/'D6_MATCHED_D5_RETENTION_D7_PREPARATION_REPORT.md').read_text(encoding='utf8')
  header+='\nCurrent learning receipt is D6_CURRENT_ACTUAL: block3 owns its32182 predecessor and complete gas/D1-D5 CUDA state restoration, CPU90/source265/36snapshots. Its periodic checkpoint is a save/startup proof, not mature behavior. D6 block2 behavior and block3 final are not substituted by block1 review. Actual deadline09:33:59+08 is a planned saved-review boundary; parent/guardian naturally exiting then noactive is legal, not a failure or full-course completion. Do not restart oldmain/once.\n\nD7 nominal actual index/frame/explicit PD and COM-off SDK accepted; original91-on failed invariant is held, separate92-on buffer-refresh SDK pending unless its actual D7_ACTUAL_INTERFACE_SCOPE_REVIEW says accepted. Short preparation failures now hold only their job; SDK_PREPARATION_ISOLATION_WORKER_* is current authority, previous JOB_IDENTIFIER/COM_READBACK/NOMINAL/GAS attentions are history. New combined D7 full checkpoint/native/PPO/learning executor is absent. Follow NEXT_D7_FULL_LEARNING_WORK_ORDER autonomously within approvedS2, prepare explicit PD actual adapter and genuinely newscope contracts. No larger ranges or repeated clock45min. Retain latest human healthv3/230h canonical/sixextensions/ownfullsave-realexit-settledactive-two-lock boundary and S8 specific approval. User ended MuJoCo/playground. All original errors, failed sources/raws/weights/costs preserved. Prior handoff is in LATEST_HANDOFF_BEFORE_D6_MATCHED_D5_RETENTION_D7_PREPARATION_20261009.md.\n'
  put('LATEST_HANDOFF.md',header)
  proof=dict(epoch=time.time(),metadata_only=True,production_GPU_PPO_canonical_writes=0,master_SHA_unchanged=g['master_SHA_unchanged'],Git=g,current_trainer=current['trainer'],current_evaluator=evaluator['own_actual_identity'],D5_18_development_cases_complete=True,D6_firstblock_matched_complete=True,D6_secondblock_saved_health_complete=True,D7_full_learning_not_deployed=True,D7_actual_scope=sdk)
  for where in (central,training,prep):put(receipt.name,proof,where)
  receipt.write_text(json.dumps(proof,indent=2),encoding='utf8');print(json.dumps(dict(synchronized=True,trainer=current['trainer']['pid'],evaluator=evaluator['own_actual_identity'],Git=g['commit'],master_unchanged=True,D7_complete_learning=False)))
finally:w.close();n.close()
