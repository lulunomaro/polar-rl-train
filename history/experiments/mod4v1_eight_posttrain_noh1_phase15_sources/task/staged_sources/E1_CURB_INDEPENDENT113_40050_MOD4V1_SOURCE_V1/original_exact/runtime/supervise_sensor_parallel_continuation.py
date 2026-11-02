"""Bounded same-scope S2 continuation with asynchronous frozen feedback.

Original206 files remain exact. No new DR, physics, PPO, observation or task.
Every block <=2h, additional window <=6h incl loading/saving/exit. A prepared
next lesson may request our own STOP_AFTER_SAVE; it never launches itself here.
"""
from pathlib import Path
import sys,os,time,json,inspect,subprocess,shutil,argparse,traceback,math
D=Path(__file__).resolve().parent;R=D/'reports'
sys.path.insert(0,str(D));import supervise_sensor_stable_continuation as s
sys.path.insert(0,str(s.CODE));from scut_curriculum_gate_v4 import evidence
from world_progress_contract import target
PRIOR=Path('/home/egde/rl_candidates/MOD4_E0_SENSOR_STABLE_CONTINUATION_20261007')
CAP=21600
BASE_LEFT=s.left
PATCHED_TRAIN=None

def spent():
 b=s.q.w.read(s.q.ctl.CANONICAL)
 total=sum(x['ended_epoch']-x['started_epoch'] for x in b['completed_segments'] if str(x.get('log','')).startswith(str(D)+'/'))
 a=b.get('active_segment')
 if a and str(a.get('log','')).startswith(str(D)+'/'):total+=time.time()-a['started_epoch']
 return total

def remaining():return min(BASE_LEFT(),CAP-120-spent())
s.left=remaining

def action(left,handover=False,attention=False):
 if attention:return 'saved_attention'
 if handover:return 'saved_handover'
 if left<=120:return 'saved_window_or_budget_boundary'
 return 'continue_same_validated_scope'

def inspect_result(job):
 root=s.ER.parent/'eval_results'/job
 if not (root/'result.json').exists() or not (root/'probe.json').exists():return dict(job=job,status='pending')
 result=s.q.w.read(root/'result.json');raw=s.q.w.read(root/'probe.json');queue=s.q.w.read(s.ER.parent/'eval_queue'/(job+'.json'))
 assert result['checkpoint']['sha256']==queue['artifacts']['checkpoint']['sha256']
 kind=result['probe_kind'];v=evidence(raw,'spin' if kind=='world' else kind,minimum_seconds=15)
 row=dict(job=job,status='complete',source_sha256=result['checkpoint']['sha256'],v4=v,kind=kind,attention=False)
 if result['exit_code']!=0 or result.get('errors') or not v['pass_']:
  row.update(attention=True,reason='actual_task_model_data_or_worker_failure');return row
 if kind=='flat':
  groups=[x for x in raw['groups'] if x['profile']=='constant'];row['straight']=[dict(command=x['command_vx'],error=x['vel_error'],speed=x['speed']) for x in groups]
  wrong=[x for x in groups if abs(x['command_vx'])==1.5 and x['speed']*x['command_vx']<=0]
  if wrong:row.update(attention=True,reason='whole_group_wrong_straight_direction')
 elif kind=='spin':
  pure=[x for x in raw['groups'] if x['profile']=='spin' and abs(abs(x['wz'])-4*math.pi)<1e-6];facts=[]
  for g in pure:
   values=[raw['per_environment']['yaw_rate'][i] for i,idx in enumerate(raw['group_ids']) if idx==g['group_id']]
   facts.append(dict(command=g['wz'],values=values,passed=sum(abs(x-g['wz'])<=.2 for x in values),total=len(values)))
   if values and all(x*g['wz']<=0 for x in values):row.update(attention=True,reason='whole_group_wrong_pure_rotation_direction')
  row['pure4pi']=facts
 else:
  facts=target(raw,.5);rows=facts['rows'];row['world']=facts;row['target_count']=sum(x['pass_'] for x in rows)
  row['max_abs_cross']=max(abs(x['cross_m_s']) for x in rows)
  moving=[x for x in rows if abs(x['command_yaw_rad_s'])==2]
  if moving and all(x['along_m_s']<=0 for x in moving):row.update(attention=True,reason='systemic_wrong_world_progress')
  if len(moving)==48 and all(not x['pass_'] for x in moving):row.update(attention=True,reason='all_48_fast_direction_samples_lost_original_target_requires_review')
 return row

def feedback():
 rows=[]
 for batch in sorted(R.glob('ASYNC_PUBLICATION_*.json')):
  rows.extend(inspect_result(x['job_id']) for x in s.q.w.read(batch)['jobs'])
 if (R/'INITIAL_FEEDBACK_JOBS.json').exists():rows.extend(inspect_result(x) for x in s.q.w.read(R/'INITIAL_FEEDBACK_JOBS.json')['jobs'])
 s.write('ASYNC_CURRENT_REVIEW.json',dict(epoch=time.time(),rows=rows,strict_facts_preserved=True,complete_dualseed_scope_not_implied=True))
 return any(x.get('attention') for x in rows)

def publish(p,row,index,full=False):
 package=s.q.w.read(s.ER/'SENSOR_COMPLETE_ASYNC_PACKAGE_AND_JOBS.json')['package'];assert s.q.base.sha(Path(package['path']))==package['sha256']
 sha=row['checkpoint']['sha256'];out=s.ER.parent/'artifacts'/('sensor-parallel-'+sha+'.pt')
 if not out.exists():
  shutil.copyfile(p,str(out)+'.partial');assert s.q.base.sha(Path(str(out)+'.partial'))==sha;os.replace(str(out)+'.partial',out)
 assert s.q.base.sha(out)==sha
 jobs=[]
 for seed in ((20261002,20261003) if full else (20261002,)):
  for profile in (('nominal','white_v2','white_v3') if full else ('white_v3',)):
   for kind in ('flat','spin','world'):
    job=f'clk1000-s2complete-30-cont-{index:02d}-{sha[:12]}-{seed}-{profile}-{kind}';path=s.ER.parent/'eval_queue'/(job+'.json')
    item=dict(job_id=job,stage='S0E',immutable=True,plan_id='MOD4-MOE-PLAN-001',plan_sha256='812a4bedd04834a98a7c9391609d0056b47c47398e0ecdda9c61e61c6466d05b',published_epoch=time.time(),kind=kind,profile=profile,sensor_profile='noise_bias_mild_v1',seed=seed,num_envs=80 if kind=='flat' else 88,steps=1500,max_wall_seconds=1800,architecture_variant='A0',role='Same-scope healthy bounded continuation; asynchronous retention check',physics_dt_s=.001,control_dt_s=.01,artifacts=dict(runtime=package,checkpoint=dict(path=str(out),bytes=out.stat().st_size,sha256=sha)),no_learning=True,canonical_write_authority=False,GPU_concurrency=1)
    if path.exists():assert s.q.w.read(path)['artifacts']['checkpoint']['sha256']==sha
    else:s.q.base.atomic_json(path,item)
    jobs.append(item)
 s.write(f'ASYNC_PUBLICATION_{index:02d}.json',dict(epoch=time.time(),jobs=jobs,full_dualseed_threeprofile_requested=full,source=row['checkpoint'],own_health=row['health'],no_new_scope=True))

def train(init):
 # Only allow repeated block directories. All physics/PPO/resume/health/budget
 # logic remains the original proven train() function byte-for-byte otherwise.
 global PATCHED_TRAIN
 if PATCHED_TRAIN is None:
  original=inspect.getsource(s.train);changed=original.replace('logs.mkdir();','logs.mkdir(exist_ok=True);')
  assert original!=changed and changed.replace('logs.mkdir(exist_ok=True);','logs.mkdir();')==original
  exec(compile(changed,str(D/'supervise_sensor_stable_continuation.py'),'exec'),s.__dict__)
  PATCHED_TRAIN=s.train
 return PATCHED_TRAIN(init)

def guardian(owner,ticks):
 while True:
  ident=s.identity(owner);lost=not ident or ident['state']=='Z' or ident['start_ticks']!=ticks
  active=s.q.base.budget_state()['active_segment'];review_attention=False
  try:review_attention=feedback()
  except BaseException:
   s.write('ASYNC_READER_ATTENTION.json',dict(epoch=time.time(),error=traceback.format_exc(),no_GPU_or_PPO_changes=True))
   review_attention=True
  request=lost or remaining()<=0 or review_attention or (R/'NEXT_STAGE_READY_REQUEST.json').exists()
  if active and request:
   child=s.identity(active['pid'])
   if child and str(s.CODE/'train_sensor_resume_ppo.py') in child['argv']:
    try:run=s.q.w.rate.trainer_run(D/'learning_logs',child['pid'])
    except AssertionError:run=None
    if run and not (run/'STOP_AFTER_SAVE').exists():
     (run/'STOP_AFTER_SAVE').write_text('Own complete-save boundary: parallel review / next lesson / owner / budget\n')
  if not active and (lost or (R/'PARALLEL_REVIEW_READY.json').exists() or (R/'PARALLEL_ATTENTION.json').exists()):return
  time.sleep(15)

def main():
 import torch;torch.set_num_threads(1)
 assert not (R/'PARALLEL_STARTED.json').exists();s.verify()
 assert s.q.w.read(R/'PARALLEL_CONTROLLER_CPU_CONTRACT.json')['passed']
 s.q.helpers.acquire(s.q.P/'autonomy_controller.lock');s.q.helpers.acquire(s.q.ctl.CANONICAL.parent/'native_floor_supervisor.lock')
 assert not s.trainers() and s.q.base.budget_state()['active_segment'] is None and not s.q.w.read(s.q.ctl.STATE_PATH).get('active_training')
 prior=s.q.w.read(PRIOR/'reports/SENSOR_STABLE_COMPLETE.json');state=s.q.w.read(PRIOR/'reports/SENSOR_STABLE_STATE.json');guard=s.q.w.read(PRIOR/'reports/SENSOR_STABLE_GUARDIAN_STARTED.json')
 for old in (state['owner'],guard):
  now=s.identity(old['pid']);assert not now or now['state']=='Z' or now['start_ticks']!=old['start_ticks']
 init=Path(prior['checkpoint']['path']);assert s.q.base.checkpoint(init)==prior['checkpoint']
 assert prior['health']['actual_task_reset_events']==0 and prior['health']['actual_physics_callbacks']==prior['health']['expected_physics_callbacks']
 assert [x for x in s.q.w.read(s.q.ctl.CANONICAL)['completed_segments'] if x['pid']==prior['own_PID_bound_receipt']['pid']]==prior['unique_completed_segment']
 s.write('PARALLEL_STARTED.json',dict(epoch=time.time(),owner=s.identity(os.getpid()),source=prior['checkpoint'],additional_window_cap_seconds=CAP,block_max_seconds=7200,new_budget_seconds=0,same_scope_preflight_reused=True,previous_completed_segment_not_recharged=True))
 with (D/'parallel_guardian.log').open('x') as f:g=subprocess.Popen([s.q.base.PY,str(Path(__file__)),'--guardian',str(os.getpid()),str(s.identity(os.getpid())['start_ticks'])],cwd=s.q.P,stdin=subprocess.DEVNULL,stdout=f,stderr=subprocess.STDOUT,start_new_session=True)
 s.write('PARALLEL_GUARDIAN_STARTED.json',s.identity(g.pid));index=0
 while True:
  why=action(remaining(),(R/'NEXT_STAGE_READY_REQUEST.json').exists(),feedback())
  if why!='continue_same_validated_scope':break
  index+=1;p,row=train(init);s.write(f'PARALLEL_BLOCK_{index:02d}_COMPLETE.json',row)
  publish(p,row,index,full=CAP-spent()<=120)
  init=p;s.write('PARALLEL_DECISION.json',dict(epoch=time.time(),block=index,action='continue_same_scope_without_waiting_for3060',source=row['checkpoint'],remaining_window_seconds=CAP-spent(),no_new_scope_or_graduation_claim=True))
 s.write('PARALLEL_REVIEW_READY.json',dict(epoch=time.time(),reason=why,source=s.q.base.checkpoint(init),spent_seconds=spent(),all_courses_finished=False,next='Prepared D3 handover or actual full retention review; never revive old main'))
 s.phase('E0_sensor_parallel_saved_boundary',child=None,source=s.q.base.checkpoint(init),reason=why)

if __name__=='__main__':
 parser=argparse.ArgumentParser();parser.add_argument('--guardian',nargs=2);a=parser.parse_args()
 try:
  if a.guardian:guardian(int(a.guardian[0]),int(a.guardian[1]))
  else:main()
 except BaseException:
  s.write('PARALLEL_ATTENTION.json',dict(epoch=time.time(),error=traceback.format_exc(),own_child_still_alive=bool(s.LIVE and s.LIVE.poll() is None),active_segment=s.q.base.budget_state()['active_segment'],all_weights_retained=True,no_blind_resume=True));raise
