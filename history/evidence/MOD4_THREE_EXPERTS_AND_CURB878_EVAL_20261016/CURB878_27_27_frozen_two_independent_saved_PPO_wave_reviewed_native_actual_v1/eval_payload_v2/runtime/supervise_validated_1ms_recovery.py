"""Restore the proven 1ms D1+D2 range; preserve per-episode supervision v2."""
from pathlib import Path
import os,sys,time,json,subprocess,traceback,argparse,shutil
D=Path(__file__).resolve().parent;R=D/'reports';CODE=D/'isaac/mod4'
sys.path.insert(0,str(D));sys.path.insert(0,str(CODE))
import supervise_dt2500_solver32_training_test as s
sys.path.insert(0,str(CODE))
from clock_training_health import learning_health_pass
from reviewed_source_guard import verify_original_records
FAILED=Path('/home/egde/rl_candidates/MOD4_EPISODE_SUPERVISION_REPAIR_20261007')
ORIGINAL=Path('/home/egde/rl_candidates/MOD4_E0_SENSOR_STABLE_CONTINUATION_20261007')
SOURCE_SHA='5abd2a912f5c717849c25de09448581c226e6c9e79581f4a44e0e4a8f27261c1'

def verify():
 verify_original_records(s.q,D);read=s.q.w.read
 a=read(s.q.ER/'PLAN_APPROVAL.json');assert a['approved'] and 'S2' in a['allowed_stages']
 own=read(R/'SOURCE_FREEZE.json')['sha256'];old=read(FAILED/'reports/SOURCE_FREEZE.json')['sha256'];one=read(ORIGINAL/'reports/SOURCE_FREEZE.json')['sha256']
 for n,h in own.items():assert s.q.base.sha(D/n)==h,n
 for n,h in old.items():
  assert s.q.base.sha(FAILED/n)==h,n
  if n!='isaac/mod4/env.json':assert own[n]==h,n
 for n,h in one.items():
  assert s.q.base.sha(ORIGINAL/n)==h,n
  if n in own and n!='isaac/mod4/clock_training_health.py':assert own[n]==h,n
 assert own['isaac/mod4/env.json']==one['isaac/mod4/env.json']
 cfg=read(CODE/'env.json');assert cfg['RM_PHYSICS_DT_S']=='0.001' and cfg['RM_SOLVER_POS']=='16' and cfg['RM_SOLVER_VEL']=='4'
 assert cfg['RM_MILD_DR_PROFILE']=='white_v3' and cfg['RM_SENSOR_PROFILE']=='noise_bias_mild_v1' and cfg['RM_KEEP_STD']=='1'
 assert read(R/'HEALTH_1MS_CPU_PASSED.json')['passed'] and read(R/'SOURCE24827_RESUME_CPU_PASSED.json')['passed']
 assert read(R/'SAME_1MS_RANGE_EVIDENCE_REUSED.json')['complete_original_PPO_reused']

s.verify=verify
s.q.verify=s.q.w.verify=s.q.ctl.verify=lambda:verify_original_records(s.q,D)

def phase(name,**kw):
 s.write('RECOVERY_STATE.json',dict(epoch=time.time(),phase=name,owner=s.identity(os.getpid()),physics_dt_s=.001,solver=[16,4],**kw))
 s.q.base.status(stage=name,supervisor_pid=os.getpid(),active_code_root=str(D),plan_stage='S2 E0 D1+D2 validated1ms recovery',active_expert='E0',architecture_variant='A0',physics_dt_s=.001,solver_position=16,solver_velocity=4,sensor_profile='noise_bias_mild_v1',active_log=kw.get('active_log'),normal_episode_resets_continue_learning=True)

def freeze_run(run):
 f=s.q.w.read(R/'SOURCE_FREEZE.json')
 if (run/'rolling_source_freeze.json').exists():assert s.q.w.read(run/'rolling_source_freeze.json')['sha256']==f['sha256'];return
 for n,h in f['sha256'].items():
  assert s.q.base.sha(D/n)==h
  p=run/'validated1ms_source_snapshot'/n;p.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(D/n,p)
 s.q.base.atomic_json(run/'rolling_source_freeze.json',dict(candidate_root=str(D),sha256=f['sha256'],physics_dt_s=.001,solver_position=16,solver_velocity=4,original1ms_runtime_except_health_v2_exact=True,closure_contract_m=.002))

def train(init,label,duration):
 verify();assert not s.trainers() and s.q.base.budget_state()['active_segment'] is None and not s.q.w.read(s.q.ctl.STATE_PATH).get('active_training')
 deadline=time.time()+min(duration,s.left());logs=D/'learning_logs';logs.mkdir(exist_ok=True);name=label+'_'+str(time.time_ns());log=D/(name+'.log')
 env=s.runtime();env['RM_RESCUE_DEADLINE']=str(deadline)
 args=[s.q.base.PY,str(CODE/'train_sensor_resume_ppo.py'),'--headless','--num_envs','20000','--steps_per_env','24','--max_iterations','10000','--save_interval','25','--learning_rate','.0001','--seed','20260928','--run_name',name,'--log_root',str(logs),'--init_checkpoint',str(init)]
 with log.open('x') as f:p=subprocess.Popen(args,cwd=s.q.P,env=env,stdin=subprocess.DEVNULL,stdout=f,stderr=subprocess.STDOUT,start_new_session=True)
 s.LIVE=p;s.q.base.start_segment(p,'S2_validated1ms_recovery_'+name,log);s.q.ctl.S=s.q.w.read(s.q.ctl.STATE_PATH)
 s.q.ctl.S['active_training']=dict(pid=p.pid,source=s.q.base.checkpoint(init),phase=label,log_root=str(logs),deadline=deadline,physics_dt_s=.001,solver_position=16,sensor_profile='noise_bias_mild_v1');s.q.ctl.persist()
 phase('bounded_S2_validated1ms_recovery_learning',child=s.identity(p.pid),source=s.q.base.checkpoint(init),deadline_epoch=deadline,active_log=str(log))
 while p.poll() is None:
  s.q.base.account_segment();roots=list(logs.glob('*_'+name))
  if len(roots)==1:
   run=roots[0]
   if (run/'latest_complete.json').exists():
    rec=s.q.w.read(run/'latest_complete.json');assert rec['pid']==p.pid;freeze_run(run)
    s.write('RECOVERY_CURRENT_SAVE.json',dict(epoch=time.time(),own_run=str(run),receipt=rec))
   for src,dst in (('SENSOR_RESUME_STARTUP_VERIFIED.json','RECOVERY_STARTUP_VERIFIED.json'),('CLOCK_TRAINING_HEALTH.json','RECOVERY_ACTIVE_HEALTH.json')):
    if (run/src).exists():s.write(dst,s.q.w.read(run/src))
  time.sleep(5)
 s.q.base.account_segment(finish=True);s.LIVE=None;s.q.ctl.S['active_training']=None;s.q.ctl.persist()
 assert p.returncode==0 and 'Traceback (most recent call last)' not in log.read_text(errors='replace'),'Worker failure: retain all own saves'
 run=s.q.w.rate.trainer_run(logs,p.pid);freeze_run(run);rec=s.q.w.read(run/'latest_complete.json');ck=s.fullsave(Path(rec['checkpoint']));m=s.q.w.read(run/'run_manifest.json');h=s.q.w.read(run/'CLOCK_TRAINING_HEALTH.json')
 assert rec['pid']==p.pid and m['source_map']==s.q.w.read(R/'SOURCE_FREEZE.json')['sha256'] and m['init_checkpoint_sha256']==s.q.base.sha(init)
 for n,sha in m['src_sha256'].items():assert s.q.base.sha(run/'src_snapshot'/n)==sha,n
 assert m['env']['RM_PHYSICS_DT_S']=='0.001' and m['env']['RM_SOLVER_POS']=='16' and h['physics_dt_s']==.001
 startup=s.q.w.read(run/'SENSOR_RESUME_STARTUP_VERIFIED.json');assert startup['source_sha256']==s.q.base.sha(init) and startup['new_physical_episode'] and not startup['PhysX_exact_resume_claimed']
 segments=[x for x in s.q.w.read(s.q.ctl.CANONICAL)['completed_segments'] if x['pid']==p.pid];assert len(segments)==1
 row=dict(epoch=time.time(),checkpoint=ck,run=str(run),own_PID_bound_receipt=rec,health=h,actual_updates=h['control_steps']//24,actual_environment_steps=h['control_steps']*20000,unique_completed_segment=segments,ordinary_events_preserved=True,new_physical_episode=True)
 s.write(label+'_SAVED_EXIT.json',row);assert learning_health_pass(h),('Actual integrity failure retained',h)
 s.write(label+'_PASSED.json',row);return Path(ck['path']),row

def sdk(init):
 assert not (R/'SDK_STARTED.json').exists();before=s.q.ctl.CANONICAL.read_bytes();output=R/'HEALTH_1MS_SDK.json';log=D/'sdk.log'
 args=[s.q.base.PY,str(D/'health_1ms_sdk_probe.py'),'--dt','.001','--checkpoint',str(init),'--num_envs','10','--warmup','24','--steps','300','--profile_steps','0','--output',str(output),'--headless']
 with log.open('x') as f:p=subprocess.Popen(args,cwd=s.q.P,env=s.runtime(),stdin=subprocess.DEVNULL,stdout=f,stderr=subprocess.STDOUT,start_new_session=True)
 s.LIVE=p;s.write('SDK_STARTED.json',dict(epoch=time.time(),child=s.identity(p.pid),source_sha256=s.q.base.sha(init),no_PPO=True));phase('frozen_1ms_health_boundary_SDK',child=s.identity(p.pid),active_log=str(log))
 p.wait(timeout=900);s.LIVE=None;assert p.returncode==0 and output.exists() and not Path(str(output)+'.error').exists()
 r=s.q.w.read(output);h=r['supervision_fixture']['health']
 assert r['actual_physics_dt']==.001 and r['decimation']==10 and r['actual_solver_readback']['all_position16_velocity4']
 assert r['supervision_fixture']['ordinary_verified'] and r['supervision_fixture']['integrity_verified']
 assert h['ordinary_episode_reset_events']==1 and h['integrity_task_reset_events']==1 and h['actual_physics_callbacks']==h['expected_physics_callbacks']==3240
 assert not r['nonfinite'] and r['max_closure_error_m']<=.002 and r['max_mimic_error_rad']<=.01
 assert r['initial_parameters']['actual_parameters_pass'] and r['final_parameters']['actual_parameters_pass']
 assert before==s.q.ctl.CANONICAL.read_bytes()
 s.write('HEALTH_1MS_SDK_PASSED.json',dict(epoch=time.time(),passed=True,output_sha256=s.q.base.sha(output),max_closure_m=r['max_closure_error_m'],actual_callbacks=h['actual_physics_callbacks'],no_PPO_or_budget_mutation=True,injected_flags_not_physical_failure_measurement=True))

def main():
 import torch;torch.set_num_threads(1)
 assert not (R/'RECOVERY_STARTED.json').exists();verify()
 s.q.helpers.acquire(s.q.P/'autonomy_controller.lock');s.q.helpers.acquire(s.q.ctl.CANONICAL.parent/'native_floor_supervisor.lock')
 assert not s.trainers() and s.q.base.budget_state()['active_segment'] is None and not s.q.w.read(s.q.ctl.STATE_PATH).get('active_training')
 for name in ('REPAIR_STARTED.json','SOLVER32_GUARDIAN_STARTED.json'):
  old=s.q.w.read(FAILED/'reports'/name);old=old.get('owner',old);actual=s.identity(old['pid']);assert not actual or actual['state']=='Z' or actual['start_ticks']!=old['start_ticks']
 failed=s.q.w.read(FAILED/'reports/episode_repaired_block2_SAVED_EXIT.json');segments=[x for x in s.q.w.read(s.q.ctl.CANONICAL)['completed_segments'] if x['pid']==failed['own_PID_bound_receipt']['pid']];assert segments==failed['unique_completed_segment']
 assert not s.identity(failed['own_PID_bound_receipt']['pid'])
 src=s.q.w.read(R/'VALIDATED_SOURCE.json');init=Path(src['checkpoint']['path']);assert s.q.base.sha(init)==SOURCE_SHA;info=s.fullsave(init)
 before=s.q.ctl.CANONICAL.read_bytes();s.write('RECOVERY_INSTALL_BOUNDARY.json',dict(epoch=time.time(),owner=s.identity(os.getpid()),source=info,two_original_locks_held=True,old_children_exited=True,active_empty=True,failed_segment_already_exactly_settled=segments,new_budget_seconds=0,old_integrity_failed26700_retained=True,no_PPO_preflight_repeat=True))
 s.write('RECOVERY_STARTED.json',dict(epoch=time.time(),owner=s.identity(os.getpid()),source=info,first_block_seconds=2700,subsequent_block_seconds=7200,maximum_same_scope_window_seconds=17100,physics_dt_s=.001,solver=[16,4],new_budget_seconds=0,D3_not_installed=True))
 assert before==s.q.ctl.CANONICAL.read_bytes();sdk(init)
 with (D/'guardian.log').open('x') as f:g=subprocess.Popen([s.q.base.PY,str(Path(__file__)),'--guardian',str(os.getpid()),str(s.identity(os.getpid())['start_ticks'])],cwd=s.q.P,stdin=subprocess.DEVNULL,stdout=f,stderr=subprocess.STDOUT,start_new_session=True)
 s.write('RECOVERY_GUARDIAN_STARTED.json',s.identity(g.pid))
 for block,duration in enumerate((2700,7200,7200),1):
  if s.left()<=120:break
  init,row=train(init,'validated1ms_recovery_block'+str(block),duration)
  s.write('RECOVERY_BLOCK_'+str(block)+'_DECISION.json',dict(epoch=time.time(),integrity_pass=True,ordinary_events=row['health']['ordinary_episode_reset_events'],next_same_scope_block=block<3,own_complete_save_available_for_D3_boundary=True,behavior_review_separate=True,no_graduation_claim=True))
 # Guardian's established own-save exit contract uses these exact filenames.
 s.write('SOLVER32_REVIEW_READY.json',dict(epoch=time.time(),own_saved_source=str(init),physical_clock_s=.001,all_courses_finished=False,next='Approved D3 at verified own saved boundary; no repeated timestep scan'))
 phase('S2_validated1ms_saved_review_ready',child=None)

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--guardian',nargs=2);a=p.parse_args()
 try:
  if a.guardian:s.guardian(int(a.guardian[0]),int(a.guardian[1]))
  else:main()
 except BaseException:
  s.write('SOLVER32_ATTENTION.json',dict(epoch=time.time(),error=traceback.format_exc(),own_child_still_alive=bool(s.LIVE and s.LIVE.poll() is None),active_segment=s.q.base.budget_state()['active_segment'],all_weights_retained=True,no_blind_resume=True));raise
