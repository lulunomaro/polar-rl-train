"""Human-authorized normal-episode continuation; structural/data faults still stop."""
from pathlib import Path
import os,sys,time,json,subprocess,traceback,argparse,shutil
D=Path(__file__).resolve().parent;R=D/'reports';CODE=D/'isaac/mod4'
sys.path.insert(0,str(D));sys.path.insert(0,str(CODE))
import supervise_dt2500_solver32_training_test as s
sys.path.insert(0,str(CODE))  # Imported historical controller adds its own path; pin this hook.
from clock_training_health import learning_health_pass
from reviewed_source_guard import verify_original_records
OLD=Path('/home/egde/rl_candidates/MOD4_E0_DT2500_ENV20K_CONTINUATION_20261007')
SOURCE_SHA='4a4456efce65f238e8b02c7a65aa17236b5dcf97754604d54103359dede1c641'

def verify_repair():
 verify_original_records(s.q,D);read=s.q.w.read
 a=read(s.q.ER/'PLAN_APPROVAL.json');assert a['approved'] and 'S2' in a['allowed_stages'] and a['approved_plan_sha256']=='812a4bedd04834a98a7c9391609d0056b47c47398e0ecdda9c61e61c6466d05b'
 f=read(R/'SOURCE_FREEZE.json')['sha256'];old=read(OLD/'reports/SOURCE_FREEZE.json')['sha256']
 for n,h in f.items():assert s.q.base.sha(D/n)==h,n
 for n,h in old.items():
  assert s.q.base.sha(OLD/n)==h,n
  if n!='isaac/mod4/clock_training_health.py':assert f[n]==h,n
 assert read(R/'AUTHORIZATION.json')['human_message']=='把这个问题解决了，别再出现这种一小点问题导致浪费一大堆时间停训的情况了'
 assert read(R/'EPISODE_HEALTH_CPU_PASSED.json')['passed']
 assert read(R/'SOURCE25211_RESUME_CPU_CONTRACT.json')['passed']

s.verify=verify_repair
s.q.verify=s.q.w.verify=s.q.ctl.verify=lambda:verify_original_records(s.q,D)
old_phase=s.phase
def phase(name,**kw):
 if name=='bounded_solver32_formal_training_test':name='bounded_S2_E0_episode_repaired_learning'
 old_phase(name,**kw);s.q.base.status(plan_stage='S2 E0 D1+D2 ordinary-episode supervision repaired',num_envs=20000,active_code_root=str(D),normal_episode_resets_continue_learning=True)
s.phase=phase

def train(init,label,duration):
 """Original PPO/load/account/save contract; only post-exit task classification changes."""
 verify_repair();assert not s.trainers() and s.q.base.budget_state()['active_segment'] is None
 assert not s.q.w.read(s.q.ctl.STATE_PATH).get('active_training') and s.left()>120
 deadline=time.time()+min(duration,s.left());logs=D/'learning_logs';logs.mkdir(exist_ok=True);name=label+'_'+str(time.time_ns());log=D/(name+'.log')
 e=s.runtime();e['RM_RESCUE_DEADLINE']=str(deadline)
 args=[s.q.base.PY,str(CODE/'train_sensor_resume_ppo.py'),'--headless','--num_envs','20000','--steps_per_env','24','--max_iterations','10000','--save_interval','25','--learning_rate','.0001','--seed','20260928','--run_name',name,'--log_root',str(logs),'--init_checkpoint',str(init)]
 with log.open('x') as f:child=subprocess.Popen(args,cwd=s.q.P,env=e,stdin=subprocess.DEVNULL,stdout=f,stderr=subprocess.STDOUT,start_new_session=True)
 s.LIVE=child;s.q.base.start_segment(child,'S2_episode_repair_'+name,log);s.q.ctl.S=s.q.w.read(s.q.ctl.STATE_PATH)
 s.q.ctl.S['active_training']=dict(pid=child.pid,source=s.q.base.checkpoint(init),phase=label,log_root=str(logs),deadline=deadline,physics_dt_s=.0025,solver_position=32,sensor_profile='noise_bias_mild_v1');s.q.ctl.persist()
 phase('bounded_S2_E0_episode_repaired_learning',child=s.identity(child.pid),source=s.q.base.checkpoint(init),deadline_epoch=deadline,active_log=str(log),normal_episode_resets_continue_learning=True)
 while child.poll() is None:
  s.q.base.account_segment()
  roots=list(logs.glob('*_'+name))
  if len(roots)==1:
   run=roots[0]
   if (run/'latest_complete.json').exists():
    receipt=s.q.w.read(run/'latest_complete.json');assert receipt['pid']==child.pid;s.freeze_run(run)
    s.write('SOLVER32_CURRENT_SAVE.json',dict(epoch=time.time(),own_run=str(run),receipt=receipt,discarded_preflight=False))
   if (run/'SENSOR_RESUME_STARTUP_VERIFIED.json').exists():s.write(label+'_STARTUP_VERIFIED.json',s.q.w.read(run/'SENSOR_RESUME_STARTUP_VERIFIED.json'))
   if (run/'CLOCK_TRAINING_HEALTH.json').exists():s.write('ACTIVE_CLASSIFIED_HEALTH.json',s.q.w.read(run/'CLOCK_TRAINING_HEALTH.json'))
  time.sleep(5)
 s.q.base.account_segment(finish=True);s.LIVE=None;s.q.ctl.S['active_training']=None;s.q.ctl.persist()
 assert child.returncode==0 and 'Traceback (most recent call last)' not in log.read_text(errors='replace'),'Worker failure: retain full saves'
 run=s.q.w.rate.trainer_run(logs,child.pid);s.freeze_run(run);receipt=s.q.w.read(run/'latest_complete.json');p=Path(receipt['checkpoint']);info=s.fullsave(p);m=s.q.w.read(run/'run_manifest.json');health=s.q.w.read(run/'CLOCK_TRAINING_HEALTH.json')
 assert receipt['pid']==child.pid and m['source_map']==s.q.w.read(R/'SOURCE_FREEZE.json')['sha256'] and m['init_checkpoint_sha256']==s.q.base.sha(init)
 for n,h in m['src_sha256'].items():assert s.q.base.sha(run/'src_snapshot'/n)==h,n
 segment=[x for x in s.q.w.read(s.q.ctl.CANONICAL)['completed_segments'] if x['pid']==child.pid];assert len(segment)==1
 startup=s.q.w.read(run/'SENSOR_RESUME_STARTUP_VERIFIED.json');assert startup['source_sha256']==s.q.base.sha(init) and startup['new_physical_episode'] and not startup['PhysX_exact_resume_claimed']
 row=dict(epoch=time.time(),checkpoint=info,run=str(run),own_PID_bound_receipt=receipt,health=health,actual_updates=health['control_steps']//24,actual_environment_steps=health['control_steps']*20000,unique_completed_segment=segment,ordinary_episode_failures_preserved_not_zeroed=True)
 s.write(label+'_SAVED_EXIT.json',row)
 assert learning_health_pass(health),('Actual integrity failure: own fullsave retained',health)
 s.write(label+'_PASSED.json',row);return p,row

def publish(row,block):
 """Reuse exact frozen physics/actor package; health-only training delta unused by probes."""
 source=row['checkpoint'];p=Path(source['path']);assert s.q.base.sha(p)==source['sha256'];s.fullsave(p)
 assert learning_health_pass(row['health'])
 package=s.q.w.read(OLD/'reports/ASYNC_CLOCK2500_PACKAGE_AND_JOBS.json')['package'];assert s.q.base.sha(Path(package['path']))==package['sha256']
 E=s.q.ER.parent;t=E/'artifacts'/('clock2500-episode-repair-'+source['sha256']+'.pt');assert not t.exists()
 shutil.copyfile(p,str(t)+'.partial');assert s.q.base.sha(Path(str(t)+'.partial'))==source['sha256'];os.replace(str(t)+'.partial',t)
 cp=dict(path=str(t),bytes=t.stat().st_size,sha256=source['sha256']);a=s.q.w.read(s.q.ER/'PLAN_APPROVAL.json');jobs=[]
 for kind in ('flat','spin','world'):
  job='clk2500-solver32-60-episode-b'+str(block)+'-'+kind;f=E/'eval_queue'/(job+'.json');assert not f.exists()
  item=dict(job_id=job,stage='S0E',immutable=True,plan_id=a['plan_id'],plan_sha256=a['approved_plan_sha256'],published_epoch=time.time(),kind=kind,profile='white_v3',sensor_profile='noise_bias_mild_v1',seed=20261002,num_envs=80 if kind=='flat' else 88,steps=1500,max_wall_seconds=1800,architecture_variant='A0',role='Own supervision-repaired complete source; ordinary reset counts disclosed',physics_dt_s=.0025,control_dt_s=.01,solver_position=32,solver_velocity=4,protocol='Original211 frozen inference/plant/reward exact; only training health classifier/controller changed. No claimed new skill maturity before actual results.',artifacts=dict(runtime=package,checkpoint=cp),no_learning=True,canonical_write_authority=False,GPU_concurrency=1,platform_scope_not_yet_accepted=False)
  s.q.base.atomic_json(f,item);jobs.append(item)
 s.write('BLOCK_'+str(block)+'_ASYNC_PUBLISHED.json',dict(epoch=time.time(),jobs=jobs,source=source,health=row['health'],no_GPU_or_canonical_write_in_publication=True))

def main():
 import torch;torch.set_num_threads(1)
 assert not (R/'REPAIR_STARTED.json').exists();verify_repair()
 s.q.helpers.acquire(s.q.P/'autonomy_controller.lock');s.q.helpers.acquire(s.q.ctl.CANONICAL.parent/'native_floor_supervisor.lock')
 assert not s.trainers() and s.q.base.budget_state()['active_segment'] is None and not s.q.w.read(s.q.ctl.STATE_PATH).get('active_training')
 for n in ('CONTINUATION_STARTED.json','SOLVER32_GUARDIAN_STARTED.json'):
  i=s.q.w.read(OLD/'reports'/n);i=i.get('owner',i);actual=s.identity(i['pid']);assert not actual or actual['state']=='Z' or actual['start_ticks']!=i['start_ticks']
 sdk=s.q.w.read(R/'SUPERVISION_SDK_PASSED.json');assert sdk['passed']
 formal=s.q.w.read(Path('/home/egde/rl_candidates/MOD4_DT2500_SOLVER32_TRAINING_TEST_20261007/reports/solver32_formal45_PASSED.json'))
 init=Path(formal['checkpoint']['path']);assert s.q.base.sha(init)==SOURCE_SHA;s.fullsave(init)
 stop=s.q.w.read(OLD/'reports/env20k_S2_D1D2_stable2h_SAVED_EXIT.json');segments=[x for x in s.q.w.read(s.q.ctl.CANONICAL)['completed_segments'] if x['pid']==stop['own_PID_bound_receipt']['pid']];assert segments==stop['unique_completed_segment']
 before=s.q.ctl.CANONICAL.read_bytes();s.write('REPAIR_INSTALL_BOUNDARY.json',dict(epoch=time.time(),source=formal['checkpoint'],old25525_all_weights_retained=True,old_segment_exact=segments,active_empty=True,two_original_locks_held=True,new_budget_seconds=0,no_duplicate_PPO_preflight=True,task_reward_physics_DR_PPO_unchanged=True))
 s.write('REPAIR_STARTED.json',dict(epoch=time.time(),owner=s.identity(os.getpid()),source=formal['checkpoint'],planned_block_seconds=7200,maximum_same_scope_window_seconds=21600,normal_episode_resets_continue_learning=True,structural_limits_unchanged=True,new_budget_seconds=0))
 with (D/'guardian.log').open('x') as f:g=subprocess.Popen([s.q.base.PY,str(Path(__file__)),'--guardian',str(os.getpid()),str(s.identity(os.getpid())['start_ticks'])],cwd=s.q.P,stdin=subprocess.DEVNULL,stdout=f,stderr=subprocess.STDOUT,start_new_session=True)
 s.write('SOLVER32_GUARDIAN_STARTED.json',s.identity(g.pid));assert before==s.q.ctl.CANONICAL.read_bytes()
 for block in range(1,4):
  if s.left()<=120:break
  init,row=train(init,'episode_repaired_block'+str(block),7200);publish(row,block)
  # Save/evaluate asynchronously. The next same-scope block does not wait for the desktop.
  s.write('BLOCK_'+str(block)+'_DECISION.json',dict(epoch=time.time(),integrity_pass=True,ordinary_events=row['health']['ordinary_episode_reset_events'],next_same_scope_block=block<3,behavior_review_is_separate=True,no_graduation_claim=True))
 s.write('SOLVER32_REVIEW_READY.json',dict(epoch=time.time(),own_saved_source=init.as_posix(),maximum_window_complete_or_budget_safe=True,behavior_comparison_pending=True,all_courses_finished=False,next='Review asynchronous old skills and ordinary episode rates; approved D3 preparation at own complete save boundary'))
 phase('S2_episode_repair_window_saved_review_ready',child=None)

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--guardian',nargs=2);a=p.parse_args()
 try:
  if a.guardian:s.guardian(int(a.guardian[0]),int(a.guardian[1]))
  else:main()
 except BaseException:
  s.write('SOLVER32_ATTENTION.json',dict(epoch=time.time(),error=traceback.format_exc(),own_child_still_alive=bool(s.LIVE and s.LIVE.poll() is None),active_segment=s.q.base.budget_state()['active_segment'],all_weights_retained=True,no_blind_resume=True));raise
