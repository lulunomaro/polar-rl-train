from pathlib import Path
import sys,json,time,hashlib
D=Path(__file__).resolve().parent;R=D/'reports'
assert not (R/'PLAN_EVALUATOR_RESTORED.json').exists(),'Once already executed'
sys.path.insert(0,str(D.parent/'MOD4_MOE_PLAN_EXECUTION_20261007'))
from eval_remote_io import connect_eval
jobs=json.loads((R/'USER_PAUSE_EXECUTED.json').read_text(encoding='utf8'))['paused_jobs']
s=(D/'eval_worker_shallow_boundary_review.py').read_text(encoding='utf8').replace('SHALLOW_BOUNDARY_REVIEW_WORKER','PLAN_CONTINUATION_WORKER')
s=s.replace('\ndef main():','\nPAUSED_SHALLOW_JOBS='+repr(tuple(jobs))+'\n\ndef main():')
s=s.replace("j not in RETIRED]","j not in RETIRED and j not in PAUSED_SHALLOW_JOBS]")
s=s.replace('retired_invalid_immutable_jobs=list(RETIRED)','retired_invalid_immutable_jobs=list(RETIRED),human_paused_shallow_jobs=list(PAUSED_SHALLOW_JOBS),normal_plan_evaluation_continues=True')
s=s.replace('reviewed_invalid_jobs_excluded=list(RETIRED)','reviewed_invalid_jobs_excluded=list(RETIRED),human_paused_shallow_jobs_excluded=list(PAUSED_SHALLOW_JOBS)')
compile(s,'eval_worker_plan_continuation_review.py','exec')
(D/'eval_worker_plan_continuation_review.py').write_text(s,encoding='utf8')
a=(D.parent/'MOD4_D7_COM_PD_PREPARE_20261009/admit_sdk_preparation_isolation_once.py').read_text(encoding='utf8')
a=a.replace('SDK_PREPARATION_ISOLATION','PLAN_CONTINUATION').replace('sdk_preparation_isolation','plan_continuation_review')
begin=a.index("    fault=read(D/'COM_READBACK_REVIEW_WORKER_ATTENTION.json')")
end=a.index('    actual=ps(',begin)
a=a[:begin]+'''    pause=read(D/'SHALLOW_EVALUATION_USER_PAUSE.json')
    assert pause['not_skill_pass'] and pause['no_4090_or_canonical_mutation']
    fault=read(D/'SHALLOW_BOUNDARY_REVIEW_WORKER_ATTENTION.json')
    job=D/'jobs/clk2500-closure-episode-d3-94-shallow-bounded-latest-20261003-flat'
    failed=read(job/'result.json')
    assert failed['phase']=='retained_failed' and failed['checkpoint']['iteration_stored']==32575 and failed['new_learning'] is False
    assert read(job/'USER_PAUSE_REQUEST.json')['paused_jobs']==pause['paused_jobs']
''' +a[end:]
a=a.replace("old='MOD4_AsyncFrozenEvaluation_v15_com_readback_review'","old='MOD4_AsyncFrozenEvaluation_v15_shallow_boundary_review'")
a=a.replace('only_reviewed_D7_readonly_failure_retired=True','human_paused_shallow_jobs_excluded=pause["paused_jobs"],user_cancel_is_not_production_fault=True')
a=a.replace('Immutable D7 read-only correction; prior failure retained; valid completed cases reused; no trainer or budget authority.','Resume normal planned frozen evaluation; user-paused synthetic shallow jobs excluded; data retained; completed cases reused; no trainer or budget authority.')
compile(a,'admit_plan_continuation_review_once.py','exec')
(D/'admit_plan_continuation_review_once.py').write_text(a,encoding='utf8')
w=connect_eval();W='D:/MOD4_async_eval/closure_episode_clock2500_v15'
try:
 with w.open_sftp() as f:
  for name in ('eval_worker_plan_continuation_review.py','admit_plan_continuation_review_once.py'):
   try:f.stat(W+'/'+name)
   except FileNotFoundError:pass
   else:raise AssertionError('Already staged; no rerun')
   b=(D/name).read_bytes()
   with f.open(W+'/'+name,'wb') as q:q.write(b)
   assert f.open(W+'/'+name).read()==b
 _,o,e=w.exec_command('"D:/claude2/fangzhen/.venv-isaaclab/Scripts/python.exe" "'+W+'/admit_plan_continuation_review_once.py"',timeout=45)
 b=o.read();err=e.read();rc=o.channel.recv_exit_status()
 if rc:
  (R/'PLAN_EVALUATOR_RESTORE_ERROR.json').write_text(json.dumps({'returncode':rc,'stdout':b.decode(errors='replace'),'stderr':err.decode(errors='replace')},indent=2));raise RuntimeError((b+err).decode(errors='replace'))
 v=json.loads(b);v['worker_source_sha256']=hashlib.sha256(s.encode()).hexdigest()
 (R/'PLAN_EVALUATOR_RESTORED.json').write_text(json.dumps(v,indent=2),encoding='utf8')
 print(json.dumps({'worker':v['new_worker'],'task':v['new_task'],'human_paused_jobs_excluded':jobs,'no_4090_or_canonical_mutation':True}))
finally:w.close()
