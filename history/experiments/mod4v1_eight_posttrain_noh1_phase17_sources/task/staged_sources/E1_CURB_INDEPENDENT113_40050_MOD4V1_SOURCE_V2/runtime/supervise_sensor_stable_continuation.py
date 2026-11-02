"""Unique same-scope2h continuation;3060 frozen evaluations stay independent."""
from pathlib import Path
import sys,os,json,time,subprocess,traceback,shutil,argparse
D=Path(__file__).resolve().parent;R=D/'reports';CODE=D/'isaac/mod4'
OLD=Path('/home/egde/rl_candidates/MOD4_E0_SENSOR_DEPENDENCY_REVIEW_20261007')
N=Path('/home/egde/rl_candidates/MOD4_PHYSICS_DT1000_WORKER_REVIEW_20261007')
sys.path.insert(0,str(N));import continue_clock1000_worker_manifest_review_once as q
ER=q.ER;LIVE=None
def write(n,v):q.base.atomic_json(R/n,v)
def identity(pid):
 i=q.helpers.identity(pid)
 if i:i['ppid']=int((Path('/proc')/str(pid)/'stat').read_text().rsplit(')',1)[1].split()[1])
 return i
def trainers():
 result=[]
 for p in Path('/proc').glob('[0-9]*/cmdline'):
  try:
   a=[x.decode(errors='replace') for x in p.read_bytes().split(b'\0')]
   if any(Path(x).name in ('train_mod4_ppo.py','train_sensor_ppo.py','train_sensor_resume_ppo.py','train_history_ppo.py') for x in a):result.append(identity(int(p.parent.name)))
  except (OSError,ValueError):pass
 return result
def verify():
 q.verify();a=q.w.read(ER/'PLAN_APPROVAL.json');assert a['approved'] and 'S2' in a['allowed_stages']
 assert a['approved_plan_sha256']=='812a4bedd04834a98a7c9391609d0056b47c47398e0ecdda9c61e61c6466d05b'
 for n,h in q.w.read(R/'SOURCE_FREEZE.json')['sha256'].items():assert q.base.sha(D/n)==h,n
 for n,h in q.w.read(OLD/'reports/SOURCE_FREEZE.json')['sha256'].items():assert q.base.sha(OLD/n)==h and q.base.sha(D/n)==h,n
 assert q.w.read(CODE/'env.json')==q.w.read(OLD/'isaac/mod4/env.json')
 assert q.w.read(R/'SENSOR_RESUME_CPU_CONTRACT.json')['passed']
def left():
 b=q.base.budget_state();a=b['active_segment'];return b['remaining_training_seconds']-(max(0,time.time()-a['accounted_through_epoch']) if a else 0)
def phase(name,**kw):
 write('SENSOR_STABLE_STATE.json',dict(epoch=time.time(),phase=name,owner=identity(os.getpid()),**kw))
 q.base.status(stage=name,supervisor_pid=os.getpid(),active_code_root=str(D),active_expert='E0',plan_stage='S2 D1+D2 stable continuation',architecture_variant='A0',physics_dt_s=.001,profile='white_v3',sensor_profile='noise_bias_mild_v1',active_log=kw.get('active_log'))
def freeze_run(run):
 if (run/'rolling_source_freeze.json').exists():return
 f=q.w.read(R/'SOURCE_FREEZE.json')
 for n,h in f['sha256'].items():
  assert q.base.sha(D/n)==h;p=run/'sensor_source_snapshot'/n;p.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(D/n,p)
 q.base.atomic_json(run/'rolling_source_freeze.json',dict(candidate_root=str(D),sha256=f['sha256'],old202_byte_exact=True,new_episode_stochastic_resume_contract=True,physics_dt_s=.001))
def train(init):
 global LIVE
 verify();assert not trainers() and q.base.budget_state()['active_segment'] is None and not q.w.read(q.ctl.STATE_PATH).get('active_training')
 assert left()>120;duration=min(7200,left());deadline=time.time()+duration
 logs=D/'learning_logs';logs.mkdir();name='sensor_stable2h_'+str(time.time_ns());log=D/(name+'.log')
 e=q.w.runtime();e.update(PYTHONPATH=str(D)+os.pathsep+str(CODE),RM_SENSOR_PROFILE='noise_bias_mild_v1',RM_RESCUE_DEADLINE=str(deadline),PYTHONUNBUFFERED='1')
 args=[q.base.PY,str(CODE/'train_sensor_resume_ppo.py'),'--headless','--num_envs','20000','--steps_per_env','24','--max_iterations','10000','--save_interval','25','--learning_rate','.0001','--seed','20260928','--run_name',name,'--log_root',str(logs),'--init_checkpoint',str(init)]
 with log.open('x') as f:child=subprocess.Popen(args,cwd=q.P,env=e,stdin=subprocess.DEVNULL,stdout=f,stderr=subprocess.STDOUT,start_new_session=True)
 LIVE=child;q.base.start_segment(child,'moe_S2_D1D2_stable_'+name,log)
 q.ctl.S=q.w.read(q.ctl.STATE_PATH);q.ctl.S['active_training']=dict(pid=child.pid,source=q.base.checkpoint(init),phase='sensor_stable2h',log_root=str(logs),deadline=deadline,profile='white_v3',sensor_profile='noise_bias_mild_v1');q.ctl.persist()
 phase('bounded_E0_sensor_stable_learning',child=identity(child.pid),source=q.base.checkpoint(init),deadline_epoch=deadline,active_log=str(log))
 while child.poll() is None:
  q.base.account_segment()
  roots=list(logs.glob('*_'+name))
  if len(roots)==1:
   run=roots[0]
   if (run/'SENSOR_RESUME_STARTUP_VERIFIED.json').exists():
    audit=q.w.read(run/'SENSOR_RESUME_STARTUP_VERIFIED.json');assert audit['source_sha256']==q.base.sha(init)
    write('SENSOR_STABLE_STARTUP_VERIFIED.json',audit)
   if (run/'latest_complete.json').exists():
    receipt=q.w.read(run/'latest_complete.json');assert receipt['pid']==child.pid
    freeze_run(run);write('SENSOR_STABLE_CURRENT_SAVE.json',dict(epoch=time.time(),own_run=str(run),receipt=receipt))
  time.sleep(5)
 q.base.account_segment(finish=True);LIVE=None;q.ctl.S['active_training']=None;q.ctl.persist()
 assert child.returncode==0 and 'Traceback (most recent call last)' not in log.read_text(errors='replace'),('Worker failure; preserve own saves',child.returncode)
 run=q.w.rate.trainer_run(logs,child.pid);freeze_run(run);receipt=q.w.read(run/'latest_complete.json');p=Path(receipt['checkpoint']);info=q.base.checkpoint(p)
 health=q.w.read(run/'CLOCK_TRAINING_HEALTH.json');m=q.w.read(run/'run_manifest.json');startup=q.w.read(run/'SENSOR_RESUME_STARTUP_VERIFIED.json')
 assert m['source_map']==q.w.read(R/'SOURCE_FREEZE.json')['sha256'] and m['init_checkpoint_sha256']==q.base.sha(init)
 assert startup['source_sha256']==q.base.sha(init) and startup['new_physical_episode'] and not startup['PhysX_exact_resume_claimed']
 for n,h in m['src_sha256'].items():assert q.base.sha(run/'src_snapshot'/n)==h,n
 assert health['actual_task_reset_events']==0 and health['failed_environments']==0 and health['max_closure_error_m']<=.002 and health['max_mimic_error_rad']<=.01 and health['actual_physics_callbacks']==health['expected_physics_callbacks'],('Actual task/model/data failure',health)
 segment=[x for x in q.w.read(q.ctl.CANONICAL)['completed_segments'] if x['pid']==child.pid];assert len(segment)==1
 row=dict(epoch=time.time(),checkpoint=info,run=str(run),own_PID_bound_receipt=receipt,health=health,actual_updates=health['control_steps']//24,actual_environment_steps=health['control_steps']*20000,unique_completed_segment=segment,discarded_preflight=False,source_init=str(init),startup=startup)
 write('SENSOR_STABLE_COMPLETE.json',row);return p,row
def publish_final(p,row):
 old=q.w.read(ER/'SENSOR_COMPLETE_ASYNC_PACKAGE_AND_JOBS.json');runtime=old['package'];assert q.base.sha(Path(runtime['path']))==runtime['sha256']
 target=ER.parent/'artifacts'/('clock1000-s2sensor-stable-'+row['checkpoint']['sha256']+'.pt');assert not target.exists()
 shutil.copyfile(p,str(target)+'.partial');assert q.base.sha(Path(str(target)+'.partial'))==row['checkpoint']['sha256'];os.replace(str(target)+'.partial',target)
 jobs=[];a=q.w.read(ER/'PLAN_APPROVAL.json')
 for kind in ('flat','spin','world'):
  job='clk1000-s2complete-20-stable-'+kind;path=ER.parent/'eval_queue'/(job+'.json');assert not path.exists()
  item=dict(job_id=job,stage='S0E',immutable=True,plan_id=a['plan_id'],plan_sha256=a['approved_plan_sha256'],published_epoch=time.time(),kind=kind,profile='white_v3',sensor_profile='noise_bias_mild_v1',seed=20261002,num_envs=80 if kind=='flat' else 88,steps=1500,max_wall_seconds=1800,architecture_variant='A0',role='Actual healthy stable2h sensor candidate',physics_dt_s=.001,control_dt_s=.01,protocol='Same202 plant/feedback/frozen inference bytes exact reused; new training entry only restores stochastic streams before fresh physical episode.',artifacts=dict(runtime=runtime,checkpoint=dict(path=str(target),bytes=target.stat().st_size,sha256=row['checkpoint']['sha256'])),no_learning=True,canonical_write_authority=False,GPU_concurrency=1)
  q.base.atomic_json(path,item);jobs.append(item)
 write('SENSOR_STABLE_ASYNC_PUBLISHED.json',dict(epoch=time.time(),jobs=jobs,source=row['checkpoint'],training_original202_runtime_exact=True,no_frozen_worker_changes=True))
def guardian(owner,ticks):
 while True:
  p=identity(owner);a=q.base.budget_state()['active_segment'];lost=not p or p['state']=='Z' or p['start_ticks']!=ticks
  if a and (lost or left()<=0):
   child=identity(a['pid'])
   if child and str(CODE/'train_sensor_resume_ppo.py') in child['argv']:
    try:run=q.w.rate.trainer_run(D/'learning_logs',child['pid'])
    except AssertionError:run=None
    if run and not (run/'STOP_AFTER_SAVE').exists():(run/'STOP_AFTER_SAVE').write_text('Own fullsave: owner or canonical budget protection\n')
  if not a and (lost or (R/'SENSOR_STABLE_REVIEW_READY.json').exists() or (R/'SENSOR_STABLE_ATTENTION.json').exists()):return
  time.sleep(15)
def main():
 import torch;torch.set_num_threads(1)
 assert not (R/'SENSOR_STABLE_STARTED.json').exists();verify()
 q.helpers.acquire(q.P/'autonomy_controller.lock');q.helpers.acquire(q.ctl.CANONICAL.parent/'native_floor_supervisor.lock')
 assert q.base.budget_state()['active_segment'] is None and not trainers() and not q.w.read(q.ctl.STATE_PATH).get('active_training')
 review=q.w.read(R/'SENSOR_MODEL24061_FIRST_MATCHED_REVIEW.json');formal=review['formal'];init=Path(formal['checkpoint']['path'])
 assert q.base.sha(init)==formal['checkpoint']['sha256'] and formal['checkpoint']['finite_tensors']==74
 assert formal['health']['actual_task_reset_events']==0 and len(formal['unique_completed_segment'])==1
 for name in ('E0_SENSOR_STARTED.json','E0_SENSOR_GUARDIAN_STARTED.json'):
  receipt=q.w.read(OLD/'reports'/name);ident=receipt.get('owner',receipt);p=identity(ident['pid']);assert not p or p['state']=='Z' or p['start_ticks']!=ident['start_ticks']
 actual=[x for x in q.w.read(q.ctl.CANONICAL)['completed_segments'] if x['pid']==formal['own_PID_bound_receipt']['pid']]
 assert actual==formal['unique_completed_segment']
 assert review['candidate']['world']['target_count']==64 and all(x['passed']==x['total'] for x in review['candidate']['spin']['pure4pi'])
 before=q.ctl.CANONICAL.read_bytes();write('SENSOR_STABLE_INSTALL_BOUNDARY.json',dict(epoch=time.time(),prior_full_source=formal['checkpoint'],prior_segment_exact=actual,noactive=True,prior_authorities_exited=True,old202_exact=True,no_new_range_preflight=True))
 write('SENSOR_STABLE_STARTED.json',dict(epoch=time.time(),owner=identity(os.getpid()),source=q.base.checkpoint(init),planned_seconds=7200,new_budget_seconds=0,old_same_scope_preflight_exact_reused=True))
 with (D/'guardian.log').open('x') as f:g=subprocess.Popen([q.base.PY,str(Path(__file__)),'--guardian',str(os.getpid()),str(identity(os.getpid())['start_ticks'])],cwd=q.P,stdin=subprocess.DEVNULL,stdout=f,stderr=subprocess.STDOUT,start_new_session=True)
 write('SENSOR_STABLE_GUARDIAN_STARTED.json',identity(g.pid));assert q.ctl.CANONICAL.read_bytes()==before
 p,row=train(init);publish_final(p,row)
 write('SENSOR_STABLE_REVIEW_READY.json',dict(epoch=time.time(),formal=row,next='Actual async retention review; then D3 validated contract or next bounded block',all_courses_finished=False))
 phase('E0_sensor_stable_saved_review_ready',child=None,source=row['checkpoint'])
if __name__=='__main__':
 parser=argparse.ArgumentParser();parser.add_argument('--guardian',nargs=2);a=parser.parse_args()
 try:
  if a.guardian:guardian(int(a.guardian[0]),int(a.guardian[1]))
  else:main()
 except BaseException:
  write('SENSOR_STABLE_ATTENTION.json',dict(epoch=time.time(),error=traceback.format_exc(),own_child_still_alive=bool(LIVE and LIVE.poll() is None),active_segment=q.base.budget_state()['active_segment'],all_weights_retained=True,no_blind_resume=True));raise
