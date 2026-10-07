"""CPU-only final-source publisher. No GPU, training launch or budget writes."""
from pathlib import Path
import sys,json,time,os,shutil,traceback,hashlib
D=Path(__file__).resolve().parent;R=D/'reports'
S=Path('/home/egde/rl_candidates/MOD4_E0_DT2500_ENV20K_CONTINUATION_20261007')
sys.path.insert(0,str(S));import supervise_dt2500_env20k_continuation as w
s=w.s
def write(n,v):s.q.base.atomic_json(R/n,v)
def main():
 assert not (R/'STARTED.json').exists();w.verify_continuation()
 write('STARTED.json',dict(epoch=time.time(),owner=s.identity(os.getpid()),CPU_only=True,no_GPU_or_canonical_write_or_training_authority=True))
 while not (S/'reports/SOLVER32_REVIEW_READY.json').exists():
  if (S/'reports/SOLVER32_ATTENTION.json').exists():raise RuntimeError('Own training review failed: preserve source, no publication')
  i=s.q.w.read(S/'reports/CONTINUATION_STARTED.json')['owner'];a=s.identity(i['pid'])
  if not a or a['state']=='Z' or a['start_ticks']!=i['start_ticks']:raise RuntimeError('Own parent exited without complete review; audit required')
  write('STATE.json',dict(epoch=time.time(),phase='waiting_own_healthy_final',no_training_dependency=True));time.sleep(30)
 row=s.q.w.read(S/'reports/SOLVER32_REVIEW_READY.json')['formal'];source=row['checkpoint'];p=Path(source['path']);run=Path(row['run'])
 assert s.q.base.sha(p)==source['sha256'] and s.fullsave(p)['finite_tensors']==74
 assert row['health']['actual_task_reset_events']==0 and row['health']['max_closure_error_m']<=.002
 assert row['health']['actual_physics_callbacks']==row['health']['expected_physics_callbacks']
 assert s.q.w.read(run/'latest_complete.json')['pid']==row['own_PID_bound_receipt']['pid']
 m=s.q.w.read(run/'run_manifest.json');assert m['source_map']==s.q.w.read(S/'reports/SOURCE_FREEZE.json')['sha256']
 assert m['init_checkpoint_sha256']==w.SOURCE_SHA
 for n,h in m['src_sha256'].items():assert s.q.base.sha(run/'src_snapshot'/n)==h
 segment=[x for x in s.q.w.read(s.q.ctl.CANONICAL)['completed_segments'] if x['pid']==row['own_PID_bound_receipt']['pid']]
 assert segment==row['unique_completed_segment'] and len(segment)==1
 package=s.q.w.read(S/'reports/ASYNC_CLOCK2500_PACKAGE_AND_JOBS.json')['package'];assert s.q.base.sha(Path(package['path']))==package['sha256']
 E=s.q.ER.parent;target=E/'artifacts'/('clock2500-stable-'+source['sha256']+'.pt');assert not target.exists()
 shutil.copyfile(p,str(target)+'.partial');assert s.q.base.sha(Path(str(target)+'.partial'))==source['sha256'];os.replace(str(target)+'.partial',target)
 cp=dict(path=str(target),bytes=target.stat().st_size,sha256=source['sha256']);a=s.q.w.read(s.q.ER/'PLAN_APPROVAL.json');jobs=[]
 for kind in ('flat','spin','world'):
  job='clk2500-solver32-30-stable-'+kind;path=E/'eval_queue'/(job+'.json');assert not path.exists()
  item=dict(job_id=job,stage='S0E',immutable=True,plan_id=a['plan_id'],plan_sha256=a['approved_plan_sha256'],published_epoch=time.time(),kind=kind,profile='white_v3',sensor_profile='noise_bias_mild_v1',seed=20261002,num_envs=80 if kind=='flat' else 88,steps=1500,max_wall_seconds=1800,architecture_variant='A0',role='Own complete healthy2h20k source',physics_dt_s=.0025,control_dt_s=.01,solver_position=32,solver_velocity=4,protocol='Exact211 physics/sensor frozen package;213 only adds controller/contracts. Own final CPU74/receipt/manifest/unique segment verified. New platform evidence remains pending until actual review.',artifacts=dict(runtime=package,checkpoint=cp),no_learning=True,canonical_write_authority=False,GPU_concurrency=1,platform_scope_not_yet_accepted=True)
  s.q.base.atomic_json(path,item);jobs.append(item)
 write('PUBLISHED.json',dict(epoch=time.time(),jobs=jobs,source=source,own_unique_segment=segment,own213_except_controllers_exact211=True,no_canonical_write=True,scope_pending=True))
 write('STATE.json',dict(epoch=time.time(),phase='published_own_final_frozen_jobs',no_training_dependency=True))
if __name__=='__main__':
 try:main()
 except BaseException:
  write('ATTENTION.json',dict(epoch=time.time(),error=traceback.format_exc(),no_training_or_canonical_mutation=True));raise
