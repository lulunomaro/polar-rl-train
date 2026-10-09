"""Retain invalid110, publish one transport-compatible interface, safely transfer CPU worker."""
from pathlib import Path
import sys,json,time,hashlib,copy
D=Path(__file__).resolve().parent;R=D/'reports';B=D.parent
read=lambda p:json.loads(p.read_text(encoding='utf8'));sha=lambda b:hashlib.sha256(b).hexdigest()
assert not (R/'E1_TRANSPORT_AUTHORITY_REPAIRED.json').exists()
actual=read(R/'E1_INTERFACE_CURRENT_ACTUAL.json');pub=read(R/'E1_GROUND_SDK_PUBLISHED.json')
assert not actual['actual_processes'] and not actual['row']['result']
assert 'Invalid published job' in actual['worker_receipts']['ATTENTION']['error']
oldjob=pub['job']['job_id'];assert pub['job']['stage']=='S3'
sys.path.insert(0,str(D));from e1_preparation_isolation import can_hold_e1_interface,JOB,PACKAGE,SOURCE
m=copy.deepcopy(pub['job']);m.update(job_id=JOB,stage='S0E',actual_curriculum_stage='S3',actual_curriculum_expert='E1',transport_stage_fixed_by_existing_bridge_contract=True,published_epoch=time.time(),supersedes_invalid_transport_manifest=oldjob)
assert m['artifacts']['runtime']['sha256']==PACKAGE and m['artifacts']['checkpoint']['sha256']==SOURCE
failure={'phase':'retained_failed','new_learning':False};assert can_hold_e1_interface(JOB,m,failure)
for field,value in [('no_learning',False),('canonical_write_authority',True),('steps',1500),('num_envs',80),('actual_curriculum_stage','S2')]:
 wrong=copy.deepcopy(m);wrong[field]=value;assert not can_hold_e1_interface(JOB,wrong,failure)
assert not can_hold_e1_interface(oldjob,m,failure) and not can_hold_e1_interface(JOB,m,{'phase':'complete','new_learning':False})
worker=(B/'MOD4_SHALLOW_TERRAIN_ZERO_SHOT_EVAL_20261009/eval_worker_plan_continuation_review.py').read_text(encoding='utf8')
worker=worker.replace('PLAN_CONTINUATION_WORKER','E1_CURRICULUM_INTERFACE_WORKER')
worker=worker.replace('from sdk_preparation_isolation import can_hold_preparation','from sdk_preparation_isolation import can_hold_preparation\nfrom e1_preparation_isolation import can_hold_e1_interface')
needle="RETIRED=tuple(OLD_RETIRED)+(";assert worker.count(needle)==1;worker=worker.replace(needle,"RETIRED=tuple(OLD_RETIRED)+("+repr(oldjob)+",")
worker=worker.replace('not can_hold_preparation(job,manifest,result)','not (can_hold_preparation(job,manifest,result) or can_hold_e1_interface(job,manifest,result))')
worker=worker.replace('Short isolated D7 SDK preparation failed; original raw retained, no pass, no retry. Other proven-scope evaluation continues.','Pinned no-learning SDK preparation failed; original raw retained, no pass, no automatic retry. Planned frozen evaluation continues.')
compile(worker,'eval_worker_e1_curriculum_interface_review.py','exec');(D/'eval_worker_e1_curriculum_interface_review.py').write_text(worker,encoding='utf8')
admit=(B/'MOD4_SHALLOW_TERRAIN_ZERO_SHOT_EVAL_20261009/admit_plan_continuation_review_once.py').read_text(encoding='utf8')
admit=admit.replace('PLAN_CONTINUATION','E1_CURRICULUM_INTERFACE').replace('plan_continuation_review','e1_curriculum_interface_review')
start=admit.index("    pause=read(D/'SHALLOW_EVALUATION_USER_PAUSE.json')");end=admit.index('    actual=ps(',start)
admit=admit[:start]+"""    pause=read(D/'SHALLOW_EVALUATION_USER_PAUSE.json')
    assert pause['not_skill_pass'] and pause['no_4090_or_canonical_mutation']
    fault=read(D/'PLAN_CONTINUATION_WORKER_ATTENTION.json')
    assert 'Invalid published job' in fault['error']
    failed=read(D/'E1_TRANSPORT_MANIFEST_REVIEW.json')
    assert failed['old_stage_S3_rejected_by_unchanged_S0E_transport_guard'] and failed['old_job_never_fetched_or_GPU_launched']
"""+admit[end:]
admit=admit.replace("old='MOD4_AsyncFrozenEvaluation_v15_shallow_boundary_review'","old='MOD4_AsyncFrozenEvaluation_v15_plan_continuation_review'")
admit=admit.replace('OLD_TASK_BEFORE_E1_CURRICULUM_INTERFACE.xml','OLD_PLAN_TASK_BEFORE_E1_INTERFACE.xml')
admit=admit.replace('Resume normal planned frozen evaluation; user-paused synthetic shallow jobs excluded; data retained; completed cases reused; no trainer or budget authority.','Retain reviewed invalid transport manifest; pin approved E1 interface to unchanged frozen bridge scope; preserve normal queue and user pause; no trainer or budget authority.')
compile(admit,'admit_e1_curriculum_interface_review_once.py','exec');(D/'admit_e1_curriculum_interface_review_once.py').write_text(admit,encoding='utf8')
review={'epoch':time.time(),'old_job_id':oldjob,'old_manifest':pub['job'],'old_stage_S3_rejected_by_unchanged_S0E_transport_guard':True,'old_job_never_fetched_or_GPU_launched':True,'original_attention_and_manifest_retained':actual['worker_receipts']['ATTENTION'],'new_manifest':m,'existing_restricted_bridge_code_unchanged':True,'actual_curriculum_stage':'S3/E1 interface only','classifier_negative_cases_pass':7,'no_4090_PPO_canonical_or_main_runtime_change':True}
(R/'E1_TRANSPORT_MANIFEST_REVIEW.json').write_text(json.dumps(review,indent=2),encoding='utf8')
sys.path.insert(0,str(B/'MOD4_AUTONOMY_SLEEP_20261003'));from remote_io import connect
sys.path.insert(0,str(B/'MOD4_MOE_PLAN_EXECUTION_20261007'));from eval_remote_io import connect_eval
n=connect();w=connect_eval();E='/home/egde/rl_candidates/MOD4_MOE_PLAN_EXECUTION_20261007';W='D:/MOD4_async_eval/closure_episode_clock2500_v15'
try:
 with n.open_sftp() as nf:
  old=nf.open(E+'/eval_queue/'+oldjob+'.json').read();assert json.loads(old)==pub['job']
  dest=E+'/eval_queue/'+JOB+'.json'
  try:nf.stat(dest)
  except FileNotFoundError:pass
  else:raise AssertionError('New job already published; no replay')
  with nf.open(dest+'.partial','wb') as q:q.write(json.dumps(m,indent=2).encode())
  nf.rename(dest+'.partial',dest)
 with w.open_sftp() as wf:
  for name in ('e1_preparation_isolation.py','eval_worker_e1_curriculum_interface_review.py','admit_e1_curriculum_interface_review_once.py'):
   try:wf.stat(W+'/'+name)
   except FileNotFoundError:pass
   else:raise AssertionError('New source already staged; no repeat')
   data=(D/name).read_bytes()
   with wf.open(W+'/'+name,'wb') as q:q.write(data)
   assert wf.open(W+'/'+name).read()==data
  with wf.open(W+'/E1_TRANSPORT_MANIFEST_REVIEW.json','wb') as q:q.write((R/'E1_TRANSPORT_MANIFEST_REVIEW.json').read_bytes())
 _,o,e=w.exec_command('"D:/claude2/fangzhen/.venv-isaaclab/Scripts/python.exe" "'+W+'/admit_e1_curriculum_interface_review_once.py"',timeout=45)
 raw=o.read();err=e.read();assert o.channel.recv_exit_status()==0,(raw+err).decode(errors='replace')
 admitted=json.loads(raw);proof={'epoch':time.time(),'review':review,'admission':admitted,'worker_source_sha256':sha(worker.encode()),'manifest':m,'original_failed_manifest_preserved':True,'base_frozen_and_bridge_unchanged':True,'main_runtime_GPU_PPO_canonical_transactions':0,'E1_learning_executor_deployed':False}
 (R/'E1_TRANSPORT_AUTHORITY_REPAIRED.json').write_text(json.dumps(proof,indent=2),encoding='utf8')
 print(json.dumps({'new_worker':admitted['new_worker'],'new_task':admitted['new_task'],'published':JOB,'actual_E1_SDK_pending':True,'main_transactions':0}))
finally:w.close();n.close()
