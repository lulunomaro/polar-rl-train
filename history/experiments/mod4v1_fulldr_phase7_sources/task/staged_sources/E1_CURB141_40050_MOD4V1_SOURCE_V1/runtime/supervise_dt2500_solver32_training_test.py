"""User-authorized 4090 solver32 test: new-range preflight, then own bounded45min."""
from pathlib import Path
import sys,os,json,time,subprocess,traceback,shutil,argparse
D=Path(__file__).resolve().parent;R=D/'reports';CODE=D/'isaac/mod4'
N=Path('/home/egde/rl_candidates/MOD4_PHYSICS_DT1000_WORKER_REVIEW_20261007')
OLD=Path('/home/egde/rl_candidates/MOD4_E0_SENSOR_CONTINUOUS_EXECUTION_20261007')
sys.path.insert(0,str(N));import continue_clock1000_worker_manifest_review_once as q
LIVE=None
def write(n,v):q.base.atomic_json(R/n,v)
def identity(pid):
 i=q.helpers.identity(pid)
 if i:i['ppid']=int((Path('/proc')/str(pid)/'stat').read_text().rsplit(')',1)[1].split()[1])
 return i
def trainers():
 result=[]
 for p in Path('/proc').glob('[0-9]*/cmdline'):
  try:
   argv=[x.decode(errors='replace') for x in p.read_bytes().split(b'\0')]
   if any(Path(x).name in ('train_mod4_ppo.py','train_sensor_ppo.py','train_sensor_resume_ppo.py','train_history_ppo.py') for x in argv):result.append(identity(int(p.parent.name)))
  except (OSError,ValueError):pass
 return result
def verify():
 q.verify();a=q.w.read(q.ER/'PLAN_APPROVAL.json');assert a['approved'] and 'S0P' in a['allowed_stages'] and 'S2' in a['allowed_stages']
 assert a['approved_plan_sha256']=='812a4bedd04834a98a7c9391609d0056b47c47398e0ecdda9c61e61c6466d05b'
 auth=q.w.read(R/'HUMAN_NATIVE_TRAINING_TEST_AUTHORIZATION.json');assert auth['approved'] and auth['solver_position']==32 and auth['physics_dt_s']==.0025
 own=q.w.read(R/'SOURCE_FREEZE.json')['sha256'];old=q.w.read(OLD/'reports/SOURCE_FREEZE.json')['sha256']
 for n,h in own.items():assert q.base.sha(D/n)==h,n
 for n,h in old.items():
  assert q.base.sha(OLD/n)==h,n
  if n!='isaac/mod4/env.json':assert own[n]==h,n
 oldenv=q.w.read(OLD/'isaac/mod4/env.json');new=q.w.read(CODE/'env.json')
 diff={k:(oldenv.get(k),new.get(k)) for k in oldenv.keys()|new.keys() if oldenv.get(k)!=new.get(k)}
 assert diff=={'RM_PHYSICS_DT_S':('0.001','0.0025'),'RM_SOLVER_POS':('16','32')},diff
 assert q.w.read(R/'CONTROLLER_CPU_CONTRACT.json')['passed'] and q.w.read(R/'SENSOR_RESUME_CPU_CONTRACT.json')['passed']
def source():
 row=q.w.read(R/'SELECTED_VALIDATED_SOURCE.json');p=Path(row['checkpoint']['path']);assert q.base.sha(p)==row['checkpoint']['sha256'];return p
def runtime():
 e=q.w.runtime();e.update({k:str(v) for k,v in q.w.read(CODE/'env.json').items()});e.update(PYTHONPATH=str(D)+os.pathsep+str(CODE),RM_SENSOR_PROFILE='noise_bias_mild_v1',PYTHONUNBUFFERED='1');return e
def left():
 b=q.base.budget_state();a=b['active_segment'];return b['remaining_training_seconds']-(max(0,time.time()-a['accounted_through_epoch']) if a else 0)
def phase(name,**kw):
 write('SOLVER32_TRAINING_STATE.json',dict(epoch=time.time(),phase=name,owner=identity(os.getpid()),**kw))
 q.base.status(stage=name,supervisor_pid=os.getpid(),active_code_root=str(D),plan_stage='S0P solver32 training test with S2 D1+D2',active_expert='E0',architecture_variant='A0',physics_dt_s=.0025,solver_position=32,solver_velocity=4,sensor_profile='noise_bias_mild_v1',active_log=kw.get('active_log'))
def fullsave(p):
 import torch
 ck=torch.load(p,map_location='cpu',weights_only=False);info=q.base.checkpoint(p)
 assert ck['actor_state_dict']['mlp.0.weight'].shape==(256,35) and ck['critic_state_dict']['mlp.0.weight'].shape==(256,38)
 assert info['finite_tensors']==74 and ck['optimizer_state_dict']['state'] and ck['sensor_recipe']['profile']=='noise_bias_mild_v1'
 assert ck['sensor_global_rng_state']['cuda'] and ck['sensor_DR_state']['version']==1
 assert 'sensor_command_DR_rng_state' in ck and 'sensor_physical_DR_rng_state' in ck
 return info
def freeze_run(run):
 if (run/'rolling_source_freeze.json').exists():return
 frozen=q.w.read(R/'SOURCE_FREEZE.json')
 for n,h in frozen['sha256'].items():
  assert q.base.sha(D/n)==h;p=run/'solver32_source_snapshot'/n;p.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(D/n,p)
 q.base.atomic_json(run/'rolling_source_freeze.json',dict(candidate_root=str(D),sha256=frozen['sha256'],physics_dt_s=.0025,solver_position=32,solver_velocity=4,provisional_longrun_test=True,closure_contract_m=.002,original_208_except_two_env_fields_exact=True))
def frozen20k(init):
 global LIVE
 verify();assert not trainers() and q.base.budget_state()['active_segment'] is None
 out=R/'NATIVE20K_PHYSICAL.json';log=D/'native20k.log';assert not out.exists() and not log.exists();before=q.ctl.CANONICAL.read_bytes();start=time.time()
 args=[q.base.PY,str(D/'native_dt2500_solver32_probe.py'),'--dt','.0025','--checkpoint',str(init),'--num_envs','20000','--warmup','24','--steps','120','--profile_steps','0','--output',str(out),'--headless']
 with log.open('x') as f:child=subprocess.Popen(args,cwd=q.P,env=runtime(),stdin=subprocess.DEVNULL,stdout=f,stderr=subprocess.STDOUT,start_new_session=True)
 LIVE=child;phase('frozen_solver32_native20k',child=identity(child.pid),active_log=str(log));child.wait(timeout=1800);LIVE=None
 assert child.returncode==0 and out.exists() and not Path(str(out)+'.error').exists() and 'Traceback (most recent call last)' not in log.read_text(errors='replace')
 r=q.w.read(out);assert before==q.ctl.CANONICAL.read_bytes()
 assert r['actual_physics_dt']==.0025 and r['actual_step_dt']==.01 and r['decimation']==4
 assert r['actual_task_failed_environments']==0 and not r['nonfinite'] and r['max_closure_error_m']<=.002 and r['max_mimic_error_rad']<=.01
 assert r['physical_callback_count']==480 and r['initial_parameters']['actual_parameters_pass'] and r['final_parameters']['actual_parameters_pass']
 assert r['actual_solver_readback']['all_position32_velocity4'] and r['actual_solver_readback']['enabled_closed_loops']==120000
 write('NATIVE20K_PASSED.json',dict(epoch=time.time(),output=str(out),output_sha256=q.base.sha(out),process_wall_seconds=time.time()-start,metrics={k:r[k] for k in ('actual_physics_dt','actual_step_dt','decimation','environment_policy_steps_per_second','actual_task_failed_environments','nonfinite','max_closure_error_m','max_mimic_error_rad','physical_callback_count','actual_solver_readback')},no_PPO=True))
def train(init,count,updates,duration,label,discard):
 global LIVE
 verify();assert not trainers() and q.base.budget_state()['active_segment'] is None and not q.w.read(q.ctl.STATE_PATH).get('active_training')
 assert left()>120;deadline=time.time()+min(duration,left());logs=D/('discard_logs' if discard else 'learning_logs');logs.mkdir(exist_ok=True);name=label+'_'+str(time.time_ns());log=D/(name+'.log')
 entry='train_sensor_ppo.py' if count==128 else 'train_sensor_resume_ppo.py';e=runtime();e['RM_RESCUE_DEADLINE']=str(deadline)
 args=[q.base.PY,str(CODE/entry),'--headless','--num_envs',str(count),'--steps_per_env','24','--max_iterations',str(updates),'--save_interval','1' if discard else '25','--learning_rate','.0001','--seed','20260928','--run_name',name,'--log_root',str(logs),'--init_checkpoint',str(init)]
 with log.open('x') as f:child=subprocess.Popen(args,cwd=q.P,env=e,stdin=subprocess.DEVNULL,stdout=f,stderr=subprocess.STDOUT,start_new_session=True)
 LIVE=child;q.base.start_segment(child,'S0P_dt2500_solver32_'+name,log);q.ctl.S=q.w.read(q.ctl.STATE_PATH);q.ctl.S['active_training']=dict(pid=child.pid,source=q.base.checkpoint(init),phase=label,log_root=str(logs),deadline=deadline,physics_dt_s=.0025,solver_position=32,sensor_profile='noise_bias_mild_v1');q.ctl.persist()
 phase('solver32_complete_PPO_preflight' if discard else 'bounded_solver32_formal_training_test',child=identity(child.pid),source=q.base.checkpoint(init),deadline_epoch=deadline,active_log=str(log))
 while child.poll() is None:
  q.base.account_segment()
  roots=list(logs.glob('*_'+name))
  if len(roots)==1:
   run=roots[0]
   if (run/'latest_complete.json').exists():
    receipt=q.w.read(run/'latest_complete.json');assert receipt['pid']==child.pid;freeze_run(run)
    write('SOLVER32_CURRENT_SAVE.json',dict(epoch=time.time(),own_run=str(run),receipt=receipt,discarded_preflight=discard))
   if (run/'SENSOR_RESUME_STARTUP_VERIFIED.json').exists():
    startup=q.w.read(run/'SENSOR_RESUME_STARTUP_VERIFIED.json');assert startup['source_sha256']==q.base.sha(init)
    write(label+'_STARTUP_VERIFIED.json',startup)
  time.sleep(1 if discard else 5)
 q.base.account_segment(finish=True);LIVE=None;q.ctl.S['active_training']=None;q.ctl.persist()
 assert child.returncode==0 and 'Traceback (most recent call last)' not in log.read_text(errors='replace'),('Worker failure: preserve own saves',label)
 run=q.w.rate.trainer_run(logs,child.pid);freeze_run(run);receipt=q.w.read(run/'latest_complete.json');p=Path(receipt['checkpoint']);info=fullsave(p);m=q.w.read(run/'run_manifest.json');health=q.w.read(run/'CLOCK_TRAINING_HEALTH.json')
 assert m['source_map']==q.w.read(R/'SOURCE_FREEZE.json')['sha256'] and m['init_checkpoint_sha256']==q.base.sha(init)
 env=m['env'];assert env['RM_PHYSICS_DT_S']=='0.0025' and env['RM_SOLVER_POS']=='32' and env['RM_SOLVER_VEL']=='4' and env['RM_KEEP_STD']=='1'
 for n,h in m['src_sha256'].items():assert q.base.sha(run/'src_snapshot'/n)==h,n
 segment=[x for x in q.w.read(q.ctl.CANONICAL)['completed_segments'] if x['pid']==child.pid];assert len(segment)==1
 row=dict(epoch=time.time(),checkpoint=info,run=str(run),own_PID_bound_receipt=receipt,health=health,actual_updates=health['control_steps']//24,actual_environment_steps=health['control_steps']*count,unique_completed_segment=segment,discarded_preflight=discard,sensor_RNG_restored_before_new_physical_episode=(count==20000),small_128env_discards_use_fresh_sensor_streams=(count==128))
 write(label+'_SAVED_EXIT.json',row)
 assert health['physics_dt_s']==.0025 and health['actual_task_reset_events']==0 and health['failed_environments']==0 and health['max_closure_error_m']<=.002 and health['max_mimic_error_rad']<=.01 and health['actual_physics_callbacks']==health['expected_physics_callbacks'],('Actual task/model/data failure: own fullsave retained',health)
 if discard:assert health['control_steps']==24*updates
 if count==20000:
  startup=q.w.read(run/'SENSOR_RESUME_STARTUP_VERIFIED.json');assert startup['source_sha256']==q.base.sha(init) and startup['new_physical_episode'] and not startup['PhysX_exact_resume_claimed']
 write(label+'_PASSED.json',row);return p,row
def guardian(owner,ticks):
 while True:
  actual=identity(owner);a=q.base.budget_state()['active_segment'];lost=not actual or actual['state']=='Z' or actual['start_ticks']!=ticks
  if a and (lost or left()<=0):
   child=identity(a['pid'])
   if child and any(str(CODE/n) in child['argv'] for n in ('train_sensor_ppo.py','train_sensor_resume_ppo.py')):
    for logs in (D/'discard_logs',D/'learning_logs'):
     try:run=q.w.rate.trainer_run(logs,child['pid']);break
     except (AssertionError,FileNotFoundError):run=None
    if run and not (run/'STOP_AFTER_SAVE').exists():(run/'STOP_AFTER_SAVE').write_text('Own fullsave: owner loss or canonical budget protection\n')
  if not a and (lost or (R/'SOLVER32_REVIEW_READY.json').exists() or (R/'SOLVER32_ATTENTION.json').exists()):return
  time.sleep(15)
def main():
 import torch;torch.set_num_threads(1)
 assert not (R/'SOLVER32_STARTED.json').exists();verify()
 q.helpers.acquire(q.P/'autonomy_controller.lock');q.helpers.acquire(q.ctl.CANONICAL.parent/'native_floor_supervisor.lock')
 assert not trainers() and q.base.budget_state()['active_segment'] is None and not q.w.read(q.ctl.STATE_PATH).get('active_training')
 for pid in (856048,856091,856092):assert not identity(pid),'Old authority or PID reuse: inspect before takeover'
 init=source();info=fullsave(init);before=q.ctl.CANONICAL.read_bytes()
 write('SOLVER32_INSTALL_BOUNDARY.json',dict(epoch=time.time(),source=info,old_authorities_exited=True,active_empty=True,same_original_two_locks_held=True,no_budget_mutation_at_install=True,preflight_weights_not_sources=True))
 write('SOLVER32_STARTED.json',dict(epoch=time.time(),owner=identity(os.getpid()),source=info,planned_formal_seconds=2700,new_budget_seconds=0,physics_dt_s=.0025,solver_position=32,solver_velocity=4,provisional_training_test_not_final_adoption=True))
 assert before==q.ctl.CANONICAL.read_bytes();frozen20k(init)
 with (D/'guardian.log').open('x') as f:g=subprocess.Popen([q.base.PY,str(Path(__file__)),'--guardian',str(os.getpid()),str(identity(os.getpid())['start_ticks'])],cwd=q.P,stdin=subprocess.DEVNULL,stdout=f,stderr=subprocess.STDOUT,start_new_session=True)
 write('SOLVER32_GUARDIAN_STARTED.json',identity(g.pid))
 pre=[]
 for count,updates in ((128,2),(20000,4)):
  _,row=train(init,count,updates,900,'solver32_discard_'+str(count),True);pre.append(row)
 write('SOLVER32_COMPLETE_PPO_PREFLIGHT_PASSED.json',dict(epoch=time.time(),receipts=pre,weights_discarded=True,full_1920000_environment_steps=True,no_mechanical_throughput_threshold=True))
 p,row=train(init,20000,10000,2700,'solver32_formal45',False)
 write('SOLVER32_REVIEW_READY.json',dict(epoch=time.time(),formal=row,own_saved_source=p.as_posix(),new_policy_behavior_pending=True,next='Actual solver margin and PPO throughput review plus same-clock flat/spin/world retention; retain1ms fallback and original thresholds.',permanent_adoption=False,all_courses_finished=False))
 phase('solver32_formal_saved_review_ready',child=None,source=row['checkpoint'])
if __name__=='__main__':
 parser=argparse.ArgumentParser();parser.add_argument('--guardian',nargs=2);args=parser.parse_args()
 try:
  if args.guardian:guardian(int(args.guardian[0]),int(args.guardian[1]))
  else:main()
 except BaseException:
  write('SOLVER32_ATTENTION.json',dict(epoch=time.time(),error=traceback.format_exc(),own_child_still_alive=bool(LIVE and LIVE.poll() is None),active_segment=q.base.budget_state()['active_segment'],all_weights_retained=True,no_blind_resume=True));raise
