
from pathlib import Path
import json,time,traceback,shutil,hashlib,subprocess,os,sys
D=Path(__file__).resolve().parent;R=D/'reports';R.mkdir(exist_ok=True)
E=Path('/home/egde/rl_candidates/MOD4_MOE_PLAN_EXECUTION_20261007')
TARGET=Path('/home/egde/rl_candidates/MOD4_S3_E1_ROUTE_BEHAVIOR_CONTINUATION_20261009/reports')
read=lambda p:json.loads(p.read_text())
def write(p,v):
 q=p.with_suffix('.cpu_partial');q.write_text(json.dumps(v,indent=2));q.replace(p)
def main():
 assert not (R/'STARTED.json').exists();pub=read(R/'E1_PLANNED_BEHAVIOR_PUBLISHED.json')
 write(R/'STARTED.json',dict(epoch=time.time(),pid=os.getpid(),CPU_only=True,GPU_PPO_canonical_launch_authority=False,only_actual_five_planned_E1_jobs=True))
 while True:
  rows={};pending=[]
  for m in pub['jobs']:
   j=m['job_id'];folder=E/'eval_results'/j;result=read(folder/'result.json') if (folder/'result.json').exists() else None
   if result and result['phase']=='retained_failed':raise AssertionError(('Actual frozen case failed; keep all raw, no replay',j,result))
   if not result or result['phase']!='complete':pending.append(j);continue
   p=read(folder/'probe.json');dest=R/'actual_cases'/j;dest.mkdir(parents=True,exist_ok=True)
   for n in ('result.json','probe.json'):shutil.copyfile(folder/n,dest/n)
   row=dict(manifest=m,result=result,probe=p)
   if m['actual_behavior_scope'].startswith('gentle terrain'):
    n=p['full_route_raw']['name'];assert n=='route_raw.npz'
    if not (folder/n).exists():pending.append(j);continue
    if not (dest/n).exists():shutil.copyfile(folder/n,dest/n)
    assert hashlib.sha256((dest/n).read_bytes()).hexdigest()==p['full_route_raw']['sha256'];row['raw_SHA_exact']=True
   rows[j]=row
  write(R/'STATE.json',dict(epoch=time.time(),phase='waiting_actual_five_cases' if pending else 'independent_actual_review',pending=pending,CPU_only=True))
  if not pending:break
  time.sleep(15)
 for kind,case in pub['reused_old_skill_baseline'].items():
  folder=E/'eval_results'/case['job_id'];dest=R/'baseline'/kind;dest.mkdir(parents=True,exist_ok=True)
  raw=(folder/'probe.json').read_bytes();assert hashlib.sha256(raw).hexdigest()==case['probe_sha256'];(dest/'probe.json').write_bytes(raw)
 write(R/'E1_PLANNED_BEHAVIOR_CURRENT_ACTUAL.json',dict(epoch=time.time(),rows=rows,evaluator_receipts=dict(ATTENTION=None),central_finalized_bytes_review=True,no_GPU_or_canonical_write=True))
 subprocess.run([sys.executable,str(D/'review_completed_behavior.py')],check=True,stdout=(D/'review.log').open('x'),stderr=subprocess.STDOUT)
 v=read(R/'E1_PLANNED_BEHAVIOR_REVIEW.json');n=v['terrain']['candidate']['probe']
 g={x['group']:x for x in n['groups']}
 # Direction is a commanded physical fact. No new success percentage is made.
 assert g['forward']['mean_valid_prefix_along_m_s']>0 and g['reverse']['mean_valid_prefix_along_m_s']<0
 assert abs(g['stand']['mean_valid_prefix_along_m_s'])<=.12,'Standing mean outside original flat diagnostic tolerance; diagnose'
 for kind,r in v['retention'].items():
  f=r['facts']
  if kind=='flat':
   assert all(x['error']<=max(.12,.25*abs(x['command'])) for x in f['straight']),'Systemic straight error outside retained original diagnostic tolerance'
  if kind=='spin':assert all(abs(x['mean']-x['command'])<=.2 for x in f['pure4pi']),'Systemic signed spin-rate error; retain all per-env facts'
  if kind=='world':
   rr=f['world_target']['rows'];tol=max(.03,.1*.5)
   assert abs(sum(x['along_m_s'] for x in rr)/len(rr)-.5)<=tol
   assert sum(abs(x['cross_m_s']) for x in rr)/len(rr)<=tol,'Systemic full signed-circle cross drift; diagnose'
 v.update(no_systemic_direction_or_major_retention_failure_observed=True,limited_same_scope_stable_learning_admitted=True,
  original_per_environment_tolerances_and_raw_flags_retained=True,no_graduation_percent_added=True,not_terrain_graduation=True,
  accepted_next='Same actual gentle geometry bounded independent E1 stable blocks; no clock/native/PPO replay',CPU_review_no_GPU_or_canonical_write=True)
 write(R/'E1_PLANNED_BEHAVIOR_SCOPE_ACCEPTED.json',v)
 write(TARGET/'E1_PLANNED_BEHAVIOR_SCOPE_ACCEPTED.json',v)
 write(R/'STATE.json',dict(epoch=time.time(),phase='actual_behavior_review_accepted_release_report_written',source_sha256=v['source_sha256'],CPU_only=True,no_GPU_or_canonical_write=True))
if __name__=='__main__':
 try:main()
 except BaseException:
  v=dict(epoch=time.time(),error=traceback.format_exc(),no_GPU_or_canonical_write=True,no_automatic_case_replay=True)
  write(R/'ATTENTION.json',v);write(TARGET/'E1_BEHAVIOR_SCOPE_ATTENTION.json',v);raise
