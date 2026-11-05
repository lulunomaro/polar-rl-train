"""New nonPT nine-role V2 stage. Never opens selected checkpoints or starts owner/SDK."""
from pathlib import Path
import json,sys,time,hashlib,shlex,posixpath,ast
D=Path(__file__).resolve().parent;z=json.loads((D/'ADMISSION1_PREIMPORT_FAILURE_TRUTH.json').read_bytes());assert z['all9_GO_SDK_source_input_or_PPO']==0 and z['failed_before_original_main_or_locks']is True;T=D.parent/'mod4v1_experts_fulldr_rm70_20261101';E=D.parent/'e3_fudan_recovery_alignment_20261104';P=D.parent/'mod4v2_p0_mechanical_limits_20261105/candidates/HW300N60/package';marker=D/'STAGE_NINE_ADMISSION2_ONCE.json';result=D/'STAGE_NINE_ADMISSION2_RESULT.json';assert not marker.exists()and not result.exists()
old=json.loads((D.parent/'mod4v1_current_nine_assessment_20261104/GROUP_PLAN_SOURCE.json').read_bytes());roles=old['roles'];assert len(roles)==9
run='MOD4V2_NINE_FULL_LEARNER_MIGRATION_ADMISSION2_'+time.strftime('%Y%m%d_%H%M%S')+'_'+str(time.time_ns());remote='/home/lc01/Zonglin Li/zonglin2/tasks/'+run
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
 x=dict(r);family,entry=entries_map[r['role']];x.update(runtime_origin=r['runtime_root'],source_family=family,entry=entry,job_root=remote+'/roles/'+r['role'],role_key='mod4v2_'+r['role'].lower(),manifest_file='SOURCE_MANIFEST_V2.json',num_envs=20000,steps_per_env=24,max_additional_updates=20,max_parent_seconds=3900,save_after_seconds=3600,exit_headroom_seconds=300,seed=20260928,worker_argv=[remote+'/worker_mod4v2_expert_migration_v1.py','--task','{JOB}/TASK.json'],final_file='production/V2_MIGRATION_FINAL.json',final_updates_key='completed_actual_updates',stop_relative='STOP_AFTER_SAVE.json');entries.append(x)
# Explicit ordering is a queue, not nine simultaneous 20k processes.
order=['E0','H1_normal','CURB_PROTECTED878','W35','E2','CURB_INDEPENDENT113','E3','SLOPE135','SLOPE_INDEPENDENT50'];entries.sort(key=lambda r:order.index(r['role']))
plan=dict(kind='MOD4V2_NINE_ORIGINAL_OWNER_SOURCE_PLAN_V1',run_id=run,root=remote,H1_excluded=False,entries=entries,canonical_path='/home/lc01/Zonglin Li/zonglin2/state/mod4_single_canonical_authority_20261026/TRAINING_BUDGET_10H.json',no_new_budget_ledger=True,two_slot_queue_only=True,host86_excluded=True,native0PT_status='PENDING_ACTUAL_FRESH_V2_WORKER_INITIALIZATION')
files={
'migration_nine_original_owner_v1.py':D/'source_owner_v1/migration_nine_original_owner_v1.py',
'stage_nine_nonpt_runtime_v1.py':D/'stage_nine_nonpt_runtime_v1.py',
'worker_mod4v2_expert_migration_v1.py':D/'worker_mod4v2_expert_migration_v1.py',
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
 if p.suffix=='.py'and rel in('migration_nine_original_owner_v1.py','worker_mod4v2_expert_migration_v1.py','stage_nine_nonpt_runtime_v1.py'):ast.parse(raw.decode('utf-8-sig'))
 payload[rel]=raw
payload['SOURCE_PLAN.json']=json.dumps(plan,indent=2).encode();payload['SCHEDULE_PUBLIC.json']=json.dumps(dict(kind='ORIGINAL_SOURCE_WORK_SCHEDULE_NOT_LEDGER_OR_NEW_BUDGET',experts={e['role_key']:dict(max_parent_seconds=3900,GPU_UUID=('GPU-16828f91-2b45-b646-8dc0-9481138e2842','GPU-c27eecbd-6838-7290-1cd2-37e34522213d')[i%2])for i,e in enumerate(entries)}),indent=2).encode();payload['V2_LOCAL_VALIDATION.json']=(P.parent/'VALIDATION.json').read_bytes()
marker.write_text(json.dumps(dict(epoch=time.time(),run_id=run,root=remote,selected_source_model_operations=0,SDK_GPU_GO_C_or_lock_operations=0),indent=2),encoding='utf8');(D/'SOURCE_PLAN_ADMISSION2_ACTUAL_V1.json').write_bytes(payload['SOURCE_PLAN.json'])
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
 archive=D/'attempts/admission1_executed_owner.py';assert not archive.exists();archive.parent.mkdir(parents=True,exist_ok=True)
 with sftp.open('/home/lc01/Zonglin Li/zonglin2/tasks/MOD4V2_NINE_FULL_LEARNER_MIGRATION_20261105_203701_1793882221738932800/migration_nine_original_owner_v1.py','r')as f:archive.write_bytes(f.read())
 mkdirs(remote)
 for rel,raw in payload.items():
  dest=remote+'/'+rel;mkdirs(posixpath.dirname(dest))
  with sftp.open(dest,'wb')as f:f.write(raw)
 command=shlex.quote('/home/lc01/Zonglin Li/zonglin2/run-python.sh')+' -B '+shlex.quote(remote+'/stage_nine_nonpt_runtime_v1.py')+' --job-root '+shlex.quote(remote)
 i,o,e=c.exec_command(command,timeout=1500);i.close();stdout=o.read().decode();stderr=e.read().decode();rc=o.channel.recv_exit_status();r=dict(epoch=time.time(),run_id=run,root=remote,returncode=rc,stdout=stdout,stderr=stderr,uploaded_nonPT_files=len(payload),selected_PT_stat_hash_decode=0,SDK_GPU_GO_C_or_lock_operations=0,owner_dispatched=False);result.write_text(json.dumps(r,indent=2),encoding='utf8');print(json.dumps(r,indent=2));assert rc==0
finally:sftp.close();c.close()
