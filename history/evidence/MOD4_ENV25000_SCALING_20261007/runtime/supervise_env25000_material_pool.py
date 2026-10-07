"""Human-authorized25000 scaling test, paired count benches and no permanent adoption."""
from pathlib import Path
import argparse,json,os,re,shutil,statistics,subprocess,sys,time,traceback
D=Path(__file__).resolve().parent;R=D/'reports';CODE=D/'isaac/mod4';OLD=Path('/home/egde/rl_candidates/MOD4_DT2500_SOLVER32_TRAINING_TEST_20261007')
sys.path.insert(0,str(OLD));import supervise_dt2500_solver32_training_test as s
LIVE=None
def read(p):return s.q.w.read(p)
def write(n,v):s.q.base.atomic_json(R/n,v)
def verify():
 s.verify();f=read(R/'SOURCE_FREEZE.json')['sha256'];old=read(OLD/'reports/SOURCE_FREEZE.json')['sha256'];assert len(f)==219
 for n,h in f.items():assert s.q.base.sha(D/n)==h,n
 assert read(R/'FIXED_POOL_CPU_PASSED.json')['CPU']['passed']
 for n,h in old.items():
  if n!='isaac/mod4/mod4_task.py':assert f[n]==h,n
 assert read(R/'SCALING_CPU_PASSED.json')['passed'] and read(R/'HUMAN_ENV25000_AUTHORIZATION.json')['approved']
 source=read(R/'FINAL25211_CPU_SOURCE_LEDGER_VERIFIED.json');assert source['formal']['health']['actual_task_reset_events']==0 and source['checkpoint']['sha256']=='4a4456efce65f238e8b02c7a65aa17236b5dcf97754604d54103359dede1c641'
def source():
 p=Path(read(R/'FINAL25211_CPU_SOURCE_LEDGER_VERIFIED.json')['checkpoint']['path']);assert s.q.base.sha(p)=='4a4456efce65f238e8b02c7a65aa17236b5dcf97754604d54103359dede1c641';return p
def runtime():
 e=s.runtime();e.update(PYTHONPATH=str(D)+os.pathsep+str(CODE));return e
def trainers():
 result=s.trainers()
 for p in Path('/proc').glob('[0-9]*/cmdline'):
  try:
   if str(CODE/'train_scaling_ppo.py').encode() in p.read_bytes():result.append(s.identity(int(p.parent.name)))
  except FileNotFoundError:pass
 return result
def phase(name,child=None,log=None,**kw):
 row=dict(epoch=time.time(),phase=name,owner=s.identity(os.getpid()),child=s.identity(child.pid) if child else None,active_log=str(log) if log else None,**kw);write('ENV25000_SCALING_STATE.json',row)
 s.q.base.status(stage=name,supervisor_pid=os.getpid(),training_pid=child.pid if child and str(CODE/'train_scaling_ppo.py') in child.args else None,active_code_root=str(D),active_log=str(log) if log else None,physics_dt_s=.0025,solver_position=32,solver_velocity=4,plan_stage='S0P E0 environment-count scaling test',active_expert='E0',sensor_profile='noise_bias_mild_v1')
def gpu():
 p=subprocess.run(['nvidia-smi','--query-gpu=utilization.gpu,memory.used,memory.total,power.draw,temperature.gpu','--format=csv,noheader,nounits'],capture_output=True,text=True,timeout=10)
 if p.returncode:return None
 try:return dict(zip(('GPU_busy_percent','memory_used_MiB','memory_total_MiB','power_W','temperature_C'),[float(x) for x in p.stdout.splitlines()[0].split(',')]))
 except ValueError:return None
def resources(rows):
 if not rows:return {'samples':0}
 return {'samples':len(rows),'sampled_not_continuous_peak':True,**{k:{'mean':statistics.mean(r[k] for r in rows),'min':min(r[k] for r in rows),'max':max(r[k] for r in rows)} for k in rows[0]}}
def freeze(run):
 f=read(R/'SOURCE_FREEZE.json')
 for n,h in f['sha256'].items():
  assert s.q.base.sha(D/n)==h;p=run/'scaling_source_snapshot'/n;p.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(D/n,p)
 s.q.base.atomic_json(run/'rolling_source_freeze.json',dict(candidate_root=str(D),sha256=f['sha256'],benchmark_only=True,physics_dt_s=.0025,solver_position=32,solver_velocity=4))
def physical(init,count,steps,name):
 global LIVE
 assert not trainers() and s.q.base.budget_state()['active_segment'] is None
 out=R/(name+'_PHYSICAL.json');log=D/(name+'.log');assert not out.exists() and not log.exists();before=s.q.ctl.CANONICAL.read_bytes();t0=time.time();samples=[]
 args=[s.q.base.PY,str(D/'pooled_native_probe.py'),'--dt','.0025','--checkpoint',str(init),'--num_envs',str(count),'--warmup','24','--steps',str(steps),'--profile_steps','0','--output',str(out),'--headless']
 with log.open('x') as f:p=subprocess.Popen(args,cwd=s.q.P,env=runtime(),stdin=subprocess.DEVNULL,stdout=f,stderr=subprocess.STDOUT,start_new_session=True)
 LIVE=p;phase('frozen_env25000_physical',child=p,log=log)
 while p.poll() is None:
  r=gpu()
  if r:samples.append(r)
  assert time.time()-t0<1800,'Review a still-live physical worker; no force kill'
  time.sleep(2)
 LIVE=None;assert not any(x in log.read_text(errors='replace') for x in ('[Error]','PhysX error:','Traceback (most recent call last)')), 'Actual engine error: preserve raw and reject'
 assert p.returncode==0 and out.exists() and not Path(str(out)+'.error').exists() and 'Traceback (most recent call last)' not in log.read_text(errors='replace')
 assert s.q.ctl.CANONICAL.read_bytes()==before
 r=read(out);assert r['num_envs']==count and r['actual_task_failed_environments']==0 and not r['nonfinite'] and r['max_closure_error_m']<=.002 and r['max_mimic_error_rad']<=.01
 assert r['physical_callback_count']==r['expected_callback_count']==steps*4 and r['actual_solver_readback']['all_position32_velocity4'] and r['actual_solver_readback']['enabled_closed_loops']==count*6
 assert r['initial_parameters']['actual_parameters_pass'] and r['final_parameters']['actual_parameters_pass']
 row={'epoch':time.time(),'raw_SHA256':s.q.base.sha(out),'metrics':{k:r[k] for k in ('num_envs','actual_physics_dt','actual_step_dt','environment_policy_steps_per_second','actual_task_failed_environments','nonfinite','max_closure_error_m','max_mimic_error_rad','physical_callback_count','actual_solver_readback')},'resources':resources(samples),'process_wall_seconds':time.time()-t0,'no_PPO_or_budget_charge':True};write(name+'_PASSED.json',row)
 if count==10:assert all(v is True for k,v in r['material_pool_independence'].items() if k!='two_distinct_actual_wheel_values')
def bench(init,count):
 global LIVE
 verify();assert not trainers() and s.q.base.budget_state()['active_segment'] is None and not read(s.q.ctl.STATE_PATH).get('active_training') and s.left()>120
 duration=min(1200,s.left());deadline=time.time()+duration;name='count'+str(count)+'_discard12_'+str(time.time_ns());logs=D/'discard_logs';logs.mkdir(exist_ok=True);log=D/(name+'.log');e=runtime();e['RM_RESCUE_DEADLINE']=str(deadline)
 args=[s.q.base.PY,str(CODE/'train_scaling_ppo.py'),'--headless','--num_envs',str(count),'--steps_per_env','24','--additional_iterations','12','--save_interval','4','--learning_rate','.0001','--seed','20260928','--run_name',name,'--log_root',str(logs),'--init_checkpoint',str(init)]
 with log.open('x') as f:p=subprocess.Popen(args,cwd=s.q.P,env=e,stdin=subprocess.DEVNULL,stdout=f,stderr=subprocess.STDOUT,start_new_session=True)
 LIVE=p;s.q.base.start_segment(p,'S0P_env_scaling_discard_'+str(count),log);s.q.ctl.S=read(s.q.ctl.STATE_PATH);s.q.ctl.S['active_training']=dict(pid=p.pid,source=s.q.base.checkpoint(init),phase='env_scaling_discard_'+str(count),log_root=str(logs),deadline=deadline,physics_dt_s=.0025,solver_position=32,num_envs=count,weights_discarded=True);s.q.ctl.persist();phase('env_scaling_complete_PPO_'+str(count),child=p,log=log,deadline_epoch=deadline,num_envs=count);samples=[];steady=[];startup=None
 while p.poll() is None:
  s.q.base.account_segment();r=gpu()
  if r:samples.append(r)
  roots=list(logs.glob('*_'+name))
  if len(roots)==1:
   run=roots[0]
   if (run/'SENSOR_RESUME_STARTUP_VERIFIED.json').exists():startup=read(run/'SENSOR_RESUME_STARTUP_VERIFIED.json')
   if startup and r:steady.append(r)
   if (run/'latest_complete.json').exists():
    receipt=read(run/'latest_complete.json');assert receipt['pid']==p.pid;write('SCALING_CURRENT_SAVE.json',dict(epoch=time.time(),num_envs=count,run=str(run),receipt=receipt,discarded=True))
  time.sleep(1)
 s.q.base.account_segment(finish=True);LIVE=None;s.q.ctl.S['active_training']=None;s.q.ctl.persist()
 assert p.returncode==0 and not any(x in log.read_text(errors='replace') for x in ('[Error]','PhysX error:','Traceback (most recent call last)'))
 run=s.q.w.rate.trainer_run(logs,p.pid);freeze(run);m=read(run/'run_manifest.json');receipt=read(run/'latest_complete.json');health=read(run/'CLOCK_TRAINING_HEALTH.json');info=s.fullsave(Path(receipt['checkpoint']));startup=read(run/'SENSOR_RESUME_STARTUP_VERIFIED.json')
 assert receipt['pid']==p.pid and m['source_map']==read(R/'SOURCE_FREEZE.json')['sha256'] and m['init_checkpoint_sha256']==s.q.base.sha(init) and m['num_envs']==count
 for n,h in m['src_sha256'].items():assert s.q.base.sha(run/'src_snapshot'/n)==h
 assert startup['actor_critic_std_exact'] and startup['optimizer_loaded_original_path'] and startup['sensor_streams_restored'] and startup['global_CPU_CUDA_streams_restored'] and startup['new_physical_episode'] and startup['new_environment_count']==count and not startup['per_environment_saved_arrays_restored'] and startup['initial30q_error_rad']==0
 text=re.sub(r'\x1b\[[0-9;]*m','',log.read_text(errors='replace'));rates=[tuple(float(x) for x in r) for r in re.findall(r'Steps per second:\s*([\d.]+)\s*Collection time:\s*([\d.]+)s\s*Learning time:\s*([\d.]+)s',text)];segs=[x for x in read(s.q.ctl.CANONICAL)['completed_segments'] if x['pid']==p.pid];assert len(segs)==1
 timed=rates[4:];row={'epoch':time.time(),'count':count,'source':s.q.base.checkpoint(init),'own_run':str(run),'checkpoint':info,'own_PID_receipt':receipt,'health':health,'startup':{k:startup[k] for k in ('actor_critic_std_exact','optimizer_loaded_original_path','stored_iteration','sensor_streams_restored','global_CPU_CUDA_streams_restored','new_physical_episode','source_environment_count','new_environment_count','per_environment_saved_arrays_restored','initial30q_error_rad')},'actual_logged_updates':len(rates),'actual_environment_steps':health['control_steps']*count,'warmup_updates_excluded':4,'timed_updates':len(timed),'timed_collection_learning_steps_s':count*24*len(timed)/sum(c+l for _,c,l in timed) if timed else None,'iteration_samples':rates,'resources_all':resources(samples),'resources_after_startup':resources(steady),'unique_completed_segment':segs,'preflight_weights_discarded':True,'learning_effect_not_isolated_env_count':True,'log_SHA256':s.q.base.sha(log)}
 write('COUNT'+str(count)+'_SAVED_EXIT.json',row)
 assert health['actual_task_reset_events']==health['failed_environments']==0 and health['max_closure_error_m']<=.002 and health['max_mimic_error_rad']<=.01 and health['actual_physics_callbacks']==health['expected_physics_callbacks']==1152 and health['control_steps']==288 and len(rates)==12
 write('COUNT'+str(count)+'_PASSED.json',row);return row
def guardian(owner,ticks):
 while True:
  actual=s.identity(owner);active=s.q.base.budget_state()['active_segment'];lost=not actual or actual['start_ticks']!=ticks or actual['state']=='Z'
  if active and (lost or s.left()<=0):
   p=s.identity(active['pid'])
   if p and str(CODE/'train_scaling_ppo.py') in p['argv']:
    try:run=s.q.w.rate.trainer_run(D/'discard_logs',p['pid'])
    except (AssertionError,FileNotFoundError):run=None
    if run and not (run/'STOP_AFTER_SAVE').exists():(run/'STOP_AFTER_SAVE').write_text('Own scaling fullsave: owner loss or canonical budget protection\n')
  if not active and (lost or (R/'ENV_SCALING_REVIEW_READY.json').exists() or (R/'ENV_SCALING_ATTENTION.json').exists()):return
  time.sleep(15)
def main():
 import torch;torch.set_num_threads(1);assert not (R/'SCALING_STARTED.json').exists();verify()
 s.q.helpers.acquire(s.q.P/'autonomy_controller.lock');s.q.helpers.acquire(s.q.ctl.CANONICAL.parent/'native_floor_supervisor.lock');assert not trainers() and s.q.base.budget_state()['active_segment'] is None and not read(s.q.ctl.STATE_PATH).get('active_training')
 assert not any(s.identity(pid) and s.identity(pid)['state']!='Z' for pid in (884890,885955,887270,903638,903671));init=source();s.fullsave(init)
 write('SCALING_STARTED.json',dict(epoch=time.time(),owner=s.identity(os.getpid()),source=s.q.base.checkpoint(init),same_two_original_locks_held=True,old_actual_authorities_exited=True,new_budget_seconds=0,only_count_scaling_benchmark=True))
 physical(init,10,300,'MATERIAL_SDK10')
 physical(init,25000,120,'NATIVE25000')
 with (D/'guardian.log').open('x') as f:g=subprocess.Popen([s.q.base.PY,str(Path(__file__)),'--guardian',str(os.getpid()),str(s.identity(os.getpid())['start_ticks'])],cwd=s.q.P,stdin=subprocess.DEVNULL,stdout=f,stderr=subprocess.STDOUT,start_new_session=True)
 write('SCALING_GUARDIAN_STARTED.json',s.identity(g.pid));rows=[bench(init,n) for n in (20000,25000)]
 ratio=rows[1]['timed_collection_learning_steps_s']/rows[0]['timed_collection_learning_steps_s'];write('ENV_SCALING_REVIEW_READY.json',dict(epoch=time.time(),rows=rows,ratio_25000_over_20000=ratio,num_envs_increased25percent=True,actual_speedup_percent=(ratio-1)*100,permanent_25000_adoption=False,new_training_weights_not_production_source=True,original_formal25211_preserved=True,all_courses_finished=False))
 phase('env25000_scaling_saved_review_ready')
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--guardian',nargs=2);a=p.parse_args()
 try:
  if a.guardian:guardian(int(a.guardian[0]),int(a.guardian[1]))
  else:main()
 except BaseException:
  write('ENV_SCALING_ATTENTION.json',dict(epoch=time.time(),error=traceback.format_exc(),own_child_still_alive=bool(LIVE and LIVE.poll() is None),actual_active_segment=s.q.base.budget_state()['active_segment'],all_weights_retained=True,no_blind_resume=True));raise
