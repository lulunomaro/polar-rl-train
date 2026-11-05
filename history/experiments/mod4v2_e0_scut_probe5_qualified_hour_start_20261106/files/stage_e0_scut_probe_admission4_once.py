"""New nonPT nine-role V2 stage. Never opens selected checkpoints or starts owner/SDK."""
from pathlib import Path
import json,sys,time,hashlib,shlex,posixpath,ast
D=Path(__file__).resolve().parent;third=json.loads((D/'SCUT_PROBE_THIRD_CLOSED_MODULE_ENUMERATION_FAILURE.json').read_bytes());assert third['actually_closed_waited_settled_released']is True and third['initial_checkpoint_accepted']is False and third['actual_PPO_updates']==0;second=json.loads((D/'SCUT_PROBE_SECOND_CLOSED_PRESTEP_ALIAS_FAILURE.json').read_bytes());assert second['actually_closed_waited_settled_released']is True and second['source_learner_loaded']is False and second['actual_PPO_updates']==0;prior=json.loads((D/'SCUT_PROBE_FIRST_CLOSED_TENSOR_ABI_FAILURE.json').read_bytes());assert prior['actually_closed_waited_settled_released']is True and prior['source_learner_loaded']is False and prior['actual_PPO_updates']==0;ready=json.loads((D/'E0_D6_NATIVE_ADMITTED_READINESS.json').read_bytes());assert ready['passed']is True and all(ready['checks'].values());f2=json.loads((D/'E0_SINGLE_A2_QUEUE_FAILURE_TRUTH.json').read_bytes());assert f2['source_PT_loaded']is False and f2['all_actual_wait_settle_release']is True;first=json.loads((D/'E0_SINGLE_PREMAIN_FAILURE_TRUTH.json').read_bytes());assert first['all_GO_SDK_PT_PPO']==0 and first['actual_outer_wait']['original_owner_reaped']is True;prior=json.loads(Path(json.loads((D/'NINE_ADMISSION5_CLOSED_RESULT_PATH.json').read_bytes())['path']).read_bytes());pe=prior['metadata']['OWNER_EXIT_ACTUAL.json'];assert prior['closed']is True and all(pe[k]is True for k in('all_own_children_waited','original_cost_settled','original_private_finite_authority_leases_released')) and all(z.get('GO_PRODUCTION.json')is None for z in prior['cases'].values());native4=json.loads((D/'ADMISSION4_NATIVE_LIMIT_FAILURE_SUMMARY.json').read_bytes());assert native4['missing_finite_mechanical_endpoint_count']==10 and native4['source_weights_read_or_decode']==native4['new_PPO_updates']==0 and native4['other_eight_GO']is False and native4['original_owner_exit']['all_own_children_waited']is native4['original_owner_exit']['original_cost_settled']is native4['original_owner_exit']['original_private_finite_authority_leases_released']is True;truth3=json.loads((D/'ADMISSION3_RESOURCE_TIMEOUT_TRUTH.json').read_bytes());assert truth3['all9_actual_GO_SDK_PT_or_PPO']==0 and truth3['actual_outer_wait']['original_owner_reaped']is True and truth3['actual_owner_exit']['original_private_finite_authority_leases_released']is True;truth=json.loads(Path(json.loads((D/'NINE_ADMISSION2_CLOSED_RESULT_PATH.json').read_bytes())['path']).read_bytes());end=truth['metadata']['OWNER_EXIT_ACTUAL.json'];assert truth['closed']is True and all(end[k]is True for k in('all_own_children_waited','original_cost_settled','original_private_finite_authority_leases_released')) and all(v.get('V2_LEARNER_LOADED.json')is None for v in truth['cases'].values());T=D.parent/'mod4v1_experts_fulldr_rm70_20261101';E=D.parent/'e3_fudan_recovery_alignment_20261104';P=D.parent/'mod4v2_p0_mechanical_limits_20261105/candidates/HW300N60_CONTINUOUS_D6_V3/package';marker=D/'STAGE_E0_SCUT_PROBE_ADMISSION4_ONCE.json';result=D/'STAGE_E0_SCUT_PROBE_ADMISSION4_RESULT.json';assert not marker.exists()and not result.exists()
old=json.loads((D.parent/'mod4v1_current_nine_assessment_20261104/GROUP_PLAN_SOURCE.json').read_bytes());roles=old['roles'];assert len(roles)==9;roles=[r for r in roles if r['role']=='E0'];assert len(roles)==1
run='MOD4V2_E0_SCUT_PROBE_ADMISSION4_FULL_LEARNER_MIGRATION_'+time.strftime('%Y%m%d_%H%M%S')+'_'+str(time.time_ns());remote='/home/lc01/Zonglin Li/zonglin2/tasks/'+run
entries_map={
'E0':('e0','runtime/isaac/mod4/train_mod4v1_e0.py'),
'E2':('e2','runtime/isaac/mod4/train_mod4v1_e2.py'),
'E3':('e3','runtime/isaac/mod4/train_mod4v1_e3.py'),
'H1_normal':('h1','job0/runtime/isaac/mod4/train_H1_ground_prelaunch_fullstate_v2.py'),
'W35':('w35','runtime/isaac/mod4/train_mod4v1_w35.py'),
'CURB_PROTECTED878':('e1','runtime/isaac/mod4/train_host72_backend_admission_v1.py'),
'CURB_INDEPENDENT113':('e1','runtime/isaac/mod4/train_independent_owned_axis_v1.py'),
'SLOPE135':('e1','runtime/isaac/mod4/train_slope5_snapshot_reviewed_resume_ppo.py'),
'SLOPE_INDEPENDENT50':('e1','runtime/isaac/mod4/train_independent_owned_axis_v1.py')}
entries=[]
for r in roles:
 x=dict(r);family,entry=entries_map[r['role']];x.update(runtime_origin=r['runtime_root'],source_family=family,entry=entry,job_root=remote+'/roles/'+r['role'],role_key='mod4v2_'+r['role'].lower(),manifest_file='SOURCE_MANIFEST_V2.json',num_envs=20000,steps_per_env=24,max_additional_updates=1,window_mode='SCUT_V14_NATIVE_AND_ONE_PPO_PROBE_NOT_HOUR',max_parent_seconds=3900,save_after_seconds=3600,exit_headroom_seconds=300,seed=20260928,worker_argv=[remote+'/worker_e0_scut_v14_probe_v4.py','--task','{JOB}/TASK.json'],final_file='production/V2_MIGRATION_FINAL.json',final_updates_key='completed_actual_updates',stop_relative='STOP_AFTER_SAVE.json');entries.append(x)
# Explicit ordering is a queue, not nine simultaneous 20k processes.
order=['H1_normal','E0','CURB_PROTECTED878','W35','E2','CURB_INDEPENDENT113','E3','SLOPE135','SLOPE_INDEPENDENT50'];entries.sort(key=lambda r:order.index(r['role']))
plan=dict(kind='MOD4V2_NINE_ORIGINAL_OWNER_SOURCE_PLAN_V1',run_id=run,root=remote,H1_excluded=False,entries=entries,canonical_path='/home/lc01/Zonglin Li/zonglin2/state/mod4_single_canonical_authority_20261026/TRAINING_BUDGET_10H.json',no_new_budget_ledger=True,two_slot_queue_only=False,single_slot_queue_only=True,max_concurrent_workers=1,host86_excluded=True,native_asset_gate_role='E0',native0PT_status='PENDING_ACTUAL_FRESH_V2_WORKER_INITIALIZATION')
files={
'migration_nine_original_owner_v1.py':D/'source_owner_e0_scut_probe_v1/migration_nine_original_owner_v1.py',
'stage_e0_scut_probe_nonpt_v4.py':D/'stage_e0_scut_probe_nonpt_v4.py',
'worker_e0_scut_v14_probe_v4.py':D/'worker_e0_scut_v14_probe_v4.py',
'helpers/app_close_semantics_v6.py':E/'source_fudan_frozen_native_eval_v8_resume55/app_close_semantics_v6.py',
'helpers/resume_runtime_contracts_v3.py':E/'source_fudan_frozen_native_eval_v8_resume55/resume_runtime_contracts_v3.py'}
base=T/'POSTTRAIN_EIGHT_EXCLUDING_H1_20261102/PAIR4_GENERIC_V2_DATA_PAYLOAD'
for name in('three_slot_common_v1.py','single_writer72_authority_V85M_source.py'):files[name]=base/name
for p in P.rglob('*'):
 if '__pycache__'in p.parts or p.suffix.lower()in('.pyc','.pyo'):continue
 if p.is_file():files['v2_package/'+p.relative_to(P).as_posix()]=p
payload={}
for rel,p in files.items():
 assert p.suffix.lower()not in('.pt','.pth','.ckpt','.onnx','.safetensors');raw=p.read_bytes()
 if p.suffix=='.py'and rel in('migration_nine_original_owner_v1.py','worker_e0_scut_v14_probe_v4.py','stage_e0_scut_probe_nonpt_v4.py'):ast.parse(raw.decode('utf-8-sig'))
 payload[rel]=raw
payload['scut_v14_flat_reward_adapter_v4.py']=(D/'scut_v14_flat_reward_adapter_v4.py').read_bytes();payload['scut_v14_flat_command_termination_adapter_v1.py']=(D/'scut_v14_flat_command_termination_adapter_v1.py').read_bytes();plan.update(reference_task='Robotics-Wheelbipe-V14-Flat-v0',reference_HEAD='b8ff79f3df855faf9dc92f4a282bd80c42649466',probe_only=True,hour_not_started=True);payload['SOURCE_PLAN.json']=json.dumps(plan,indent=2).encode();payload['SCHEDULE_PUBLIC.json']=json.dumps(dict(kind='ORIGINAL_SOURCE_WORK_SCHEDULE_NOT_LEDGER_OR_NEW_BUDGET',experts={e['role_key']:dict(max_parent_seconds=3900,GPU_UUID=('GPU-16828f91-2b45-b646-8dc0-9481138e2842','GPU-c27eecbd-6838-7290-1cd2-37e34522213d')[i%2])for i,e in enumerate(entries)}),indent=2).encode();payload['V2_LOCAL_VALIDATION.json']=(D/'E0_D6_NATIVE_ADMITTED_READINESS.json').read_bytes()
marker.write_text(json.dumps(dict(epoch=time.time(),run_id=run,root=remote,selected_source_model_operations=0,SDK_GPU_GO_C_or_lock_operations=0),indent=2),encoding='utf8');(D/'SOURCE_PLAN_E0_SCUT_PROBE_ADMISSION4_ACTUAL_V1.json').write_bytes(payload['SOURCE_PLAN.json'])
sys.path.insert(0,str(T));from project_connector import connect72
c=connect72();sftp=c.open_sftp()
def mkdirs(path):
 parts=path.split('/');cur=''
 for v in parts:
  if not v:continue
  cur+='/'+v
  try:sftp.stat(cur)
  except FileNotFoundError:sftp.mkdir(cur)
try:
 try:sftp.lstat(remote)
 except FileNotFoundError:pass
 else:raise FileExistsError(remote)
 mkdirs(remote)
 for rel,raw in payload.items():
  dest=remote+'/'+rel;mkdirs(posixpath.dirname(dest))
  with sftp.open(dest,'wb')as f:f.write(raw)
 command=shlex.quote('/home/lc01/Zonglin Li/zonglin2/run-python.sh')+' -B '+shlex.quote(remote+'/stage_e0_scut_probe_nonpt_v4.py')+' --job-root '+shlex.quote(remote)
 i,o,e=c.exec_command(command,timeout=1500);i.close();stdout=o.read().decode();stderr=e.read().decode();rc=o.channel.recv_exit_status();assert rc==0;precode='import sys,runpy;sys.path.insert(0,'+repr(remote)+');ns=runpy.run_path('+repr(remote+'/migration_nine_original_owner_v1.py')+",run_name='source_dependency_preflight_not_main');import json;ns['verify_sources'](json.loads((ns['B']/'OWNER_PLAN.json').read_bytes()));print('owner_manifest_and_source_validation_passed_no_GO_SDK_models_locks_or_C_access')";pi,po,pe=c.exec_command(shlex.quote('/home/lc01/Zonglin Li/zonglin2/run-python.sh')+' -B -c '+shlex.quote(precode),timeout=60);pi.close();preout=po.read().decode();preerr=pe.read().decode();prc=po.channel.recv_exit_status();assert prc==0,(preout,preerr);r=dict(owner_import_only_preflight_rc=prc,owner_import_only_preflight_stdout=preout,epoch=time.time(),run_id=run,root=remote,returncode=rc,stdout=stdout,stderr=stderr,uploaded_nonPT_files=len(payload),selected_PT_stat_hash_decode=0,SDK_GPU_GO_C_or_lock_operations=0,owner_dispatched=False);result.write_text(json.dumps(r,indent=2),encoding='utf8');print(json.dumps(r,indent=2));assert rc==0
finally:sftp.close();c.close()
