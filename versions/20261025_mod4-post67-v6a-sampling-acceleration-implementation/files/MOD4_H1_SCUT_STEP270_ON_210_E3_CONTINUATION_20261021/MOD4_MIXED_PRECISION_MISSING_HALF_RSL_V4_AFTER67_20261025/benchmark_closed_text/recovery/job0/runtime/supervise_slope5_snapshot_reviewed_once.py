"""Unique snapshot-list repair; old402 failures retained, no SDK/native/small replay."""
from pathlib import Path
import argparse,json,os,subprocess,time,traceback
import supervise_slope5_independent_scope_once as prior
from clock_training_health import learning_health_pass
D=Path(__file__).resolve().parent;R=D/'reports';CODE=D/'isaac/mod4';s=prior.s
read=prior.read;write=prior.write;identity=prior.identity;freeze_run=prior.freeze_run;fullsave=prior.fullsave;verify=prior.verify;runtime=prior.runtime;phase=prior.phase
OLD402=Path('/home/egde/rl_candidates/MOD4_S3_E1_SLOPE5_INDEPENDENT_20261011')
def trainers():
 found=prior.trainers()
 for p in Path('/proc').glob('[0-9]*/cmdline'):
  try:
   if any(Path(x.decode(errors='replace')).name=='train_slope5_snapshot_reviewed_resume_ppo.py' for x in p.read_bytes().split(b'\0')):found.append(identity(int(p.parent.name)))
  except (OSError,ValueError):pass
 return found
def wait_existing():
 prior.wait_existing();st=read(OLD402/'reports/E1_STATE.json');att=read(OLD402/'reports/E1_ATTENTION.json');assert not att['own_child_still_alive'] and att['active_segment'] is None
 for loc in (st['owner'],st['child'],read(OLD402/'reports/E1_GUARDIAN_STARTED.json')):
  a=identity(loc['pid']);assert not a or a['state']=='Z' or a['start_ticks']!=loc['start_ticks']
 assert not trainers() and s.q.base.budget_state()['active_segment'] is None
def train(init,count,updates,duration,label,discard):
    verify();assert not trainers() and s.q.base.budget_state()['active_segment'] is None and not read(s.q.ctl.STATE_PATH).get('active_training')
    assert s.left()>120;deadline=time.time()+min(duration,s.left());logs=D/('discard_logs' if discard else 'learning_logs');logs.mkdir(exist_ok=True);name=label+'_'+str(time.time_ns());log=D/(name+'.log')
    e=runtime();e['RM_RESCUE_DEADLINE']=str(deadline);entry='train_slope5_fresh_preflight_ppo.py' if count==128 else 'train_slope5_snapshot_reviewed_resume_ppo.py'
    args=[s.q.base.PY,str(CODE/entry),'--headless','--num_envs',str(count),'--steps_per_env','24','--max_iterations',str(updates),'--save_interval','1' if discard else '25','--learning_rate','.0001','--seed','20260928','--run_name',name,'--log_root',str(logs),'--init_checkpoint',str(init)]
    with log.open('x') as f:p=subprocess.Popen(args,cwd=s.q.P,env=e,stdin=subprocess.DEVNULL,stdout=f,stderr=subprocess.STDOUT,start_new_session=True)
    s.LIVE=p;s.q.base.start_segment(p,'S3_E1_'+name,log);s.q.ctl.S=read(s.q.ctl.STATE_PATH)
    s.q.ctl.S['active_training']=dict(pid=p.pid,source=s.q.base.checkpoint(init),phase=label,log_root=str(logs),deadline=deadline,physics_dt_s=.0025,solver_position=32,feedback_delay_profile='control_0_10ms_v1',discarded_preflight=discard);s.q.ctl.persist()
    phase('E1_complete_PPO_preflight' if discard else 'bounded_E1_SLOPE5_independent_learning',child=identity(p.pid),source=s.q.base.checkpoint(init),deadline_epoch=deadline,active_log=str(log))
    while p.poll() is None:
        s.q.base.account_segment();roots=list(logs.glob('*_'+name))
        if len(roots)==1:
            run=roots[0]
            if (run/'latest_complete.json').exists():
                rec=read(run/'latest_complete.json');assert rec['pid']==p.pid;freeze_run(run);write('E1_CURRENT_SAVE.json',dict(epoch=time.time(),own_run=str(run),receipt=rec,discarded_preflight=discard))
            if (run/'CLOCK_TRAINING_HEALTH.json').exists():write('E1_ACTIVE_HEALTH.json',read(run/'CLOCK_TRAINING_HEALTH.json'))
        time.sleep(1 if discard else 5)
    s.q.base.account_segment(finish=True);s.LIVE=None;s.q.ctl.S['active_training']=None;s.q.ctl.persist()
    assert p.returncode==0 and 'Traceback (most recent call last)' not in log.read_text(errors='replace')
    run=s.q.w.rate.trainer_run(logs,p.pid);freeze_run(run);rec=read(run/'latest_complete.json');ck=fullsave(Path(rec['checkpoint']),count=count);m=read(run/'run_manifest.json');h=read(run/'CLOCK_TRAINING_HEALTH.json')
    assert rec['pid']==p.pid and m['source_map']==read(R/'SOURCE_FREEZE.json')['sha256'] and m['init_checkpoint_sha256']==s.q.base.sha(init)
    assert m['feedback_delay_recipe']['profile']=='control_0_10ms_v1' and m['physical_action_delay_recipe']['profile']=='physical_target_0_2500_5000us_v1' and m['env']['RM_PHYSICS_DT_S']=='0.0025' and m['env']['RM_SOLVER_POS']=='32'
    for n,v in m['src_sha256'].items():assert s.q.base.sha(run/'src_snapshot'/n)==v,n
    if count==20000:
        terrain=read(run/'E1_TERRAIN_RESUME_STARTUP_VERIFIED.json');assert terrain['source_sha256']==s.q.base.sha(init) and terrain['actual_CUDA_terrain_bookkeeping_disk_roundtrip_exact'] and terrain['complete_D1_D7_optimizer_global_named_streams_verified'] and terrain['E1_episode_incremented_once'] and not terrain['PhysX_exact_resume_claimed']
        assert not terrain['terrain_state_restored_exact'] and terrain['explicit_G3_to_SLOPE_geometry_transition'] and terrain['explicitly_new_E1_terrain'] and not terrain['explicit_G2_to_G3_geometry_transition']
        cp=read(run/'CHASSIS_PD_RESUME_STARTUP_VERIFIED.json');assert cp['source_sha256']==s.q.base.sha(init) and cp['actual_CUDA_chassis_PD_disk_roundtrip_exact'] and cp['COM_PD_episode_incremented_once'] and cp['complete_D1_D6_optimizer_global_named_streams_verified'] and not cp['PhysX_exact_resume_claimed']
        gas=read(run/'GAS_DAMPING_RESUME_STARTUP_VERIFIED.json');assert gas['source_sha256']==s.q.base.sha(init) and gas['actual_CUDA_gas_state_disk_roundtrip_exact'] and gas['gas_episode_incremented_once'] and gas['complete_D1_D5_optimizer_global_named_streams_verified'] and not gas['PhysX_exact_resume_claimed']
        spring=read(run/'SPRING_PRESSURE_RESUME_STARTUP_VERIFIED.json');assert spring['source_sha256']==s.q.base.sha(init) and spring['actual_CUDA_spring_state_disk_roundtrip_exact'] and spring['spring_episode_incremented_once'] and spring['complete_D1_D4_optimizer_global_named_streams_verified'] and not spring['PhysX_exact_resume_claimed']
        startup=read(run/'ACTION_DELAY_RESUME_STARTUP_VERIFIED.json');assert startup['source_sha256']==s.q.base.sha(init) and startup['action_episode_incremented_once'] and startup['complete_D3_sensor_feedback_optimizer_global_named_streams_verified'] and not startup['PhysX_exact_resume_claimed']
    a=read(run/'RETENTION_COMMAND_ACTUAL.json');assert a['actual_controls']==h['control_steps']
    if count==20000:
        v=read(run/'E1_COMMAND_RETENTION_STARTUP_VERIFIED.json');assert v['saved_source_episode_plus_one_verified'] and v['actual_CUDA_command_state_and_private_rng_disk_roundtrip_exact'] and v['old_full_D1_D7_optimizer_global_named_streams_verified'] and v['E1_episode_incremented_once']
    assert m['gas_damping_recipe']['profile']=='gas_damping_independent_episode_090_110_v1'
    seg=[x for x in read(s.q.ctl.CANONICAL)['completed_segments'] if x['pid']==p.pid];assert len(seg)==1
    assert Path(rec['checkpoint']).is_relative_to(D/('discard_logs' if discard else 'learning_logs'))
    row=dict(epoch=time.time(),expert='E1_SLOPE',source_sha256=s.q.base.sha(init),source_count=len(read(R/'SOURCE_FREEZE.json')['sha256']),checkpoint=ck,run=str(run),own_PID_bound_receipt=rec,health=h,actual_updates=h['control_steps']//24,actual_environment_steps=h['control_steps']*count,unique_completed_segment=seg,discarded_preflight=discard,small128_uses_fresh_sensor_feedback_action_pressure_gas_streams=count==128,ordinary_events_preserved=True,new_physical_episode=True)
    write(label+'_SAVED_EXIT.json',row);assert learning_health_pass(h),('Integrity failure, own source retained',h)
    if discard:assert h['control_steps']==24*updates
    write(label+'_PASSED.json',row);return Path(ck['path']),row
def guardian(owner,ticks):
 while True:
  a=identity(owner);lost=not a or a['state']=='Z' or a['start_ticks']!=ticks
  segment=s.q.base.budget_state()['active_segment'];state=read(R/'E1_STATE.json') if (R/'E1_STATE.json').exists() else {}
  loc=state.get('child');child=identity(loc['pid']) if loc else None
  own=bool(child and loc['start_ticks']==child['start_ticks'] and state['owner']['pid']==owner and any(str(CODE/n) in child['argv'] for n in ('train_slope5_fresh_preflight_ppo.py','train_slope5_snapshot_reviewed_resume_ppo.py')))
  if segment and own and segment['pid']==child['pid'] and (lost or s.left()<=0):
   for root in (D/'discard_logs',D/'learning_logs'):
    try:run=s.q.w.rate.trainer_run(root,child['pid']);break
    except (AssertionError,FileNotFoundError):run=None
   if run and not (run/'STOP_AFTER_SAVE').exists():(run/'STOP_AFTER_SAVE').write_text('Own SLOPE complete save: guardian budget/parent protection\n')
  if not own and (lost or (R/'E1_REVIEW_READY.json').exists() or (R/'E1_ATTENTION.json').exists()):return
  time.sleep(15)
def main():
 import torch;torch.set_num_threads(1)
 assert not (R/'E1_DISPATCH_STARTED.json').exists();verify();wait_existing();init=prior.source()
 s.q.helpers.acquire(s.q.P/'autonomy_controller.lock');s.q.helpers.acquire(s.q.ctl.CANONICAL.parent/'native_floor_supervisor.lock');wait_existing()
 small=read(R/'REUSED_SLOPE_SMALL128.json');assert small['discarded_preflight'] and small['actual_updates']==2 and small['actual_environment_steps']==6144
 for row in read(R/'REUSED_SLOPE_NATIVE.json')['results'].values():assert row['passed'] and row['no_PPO'] and s.q.base.sha(Path(row['path']))==row['sha256']
 write('E1_DISPATCH_STARTED.json',dict(epoch=time.time(),owner=identity(os.getpid()),expert='E1_SLOPE',new_snapshot_list_literal_repair=True,SDK_native_small_exact_reused=True,old402_failed_before_PPO_retained=True,formal_seconds=300,new_budget_seconds=0))
 with (D/'guardian.log').open('x') as out:g=subprocess.Popen([s.q.base.PY,str(Path(__file__)),'--guardian',str(os.getpid()),str(identity(os.getpid())['start_ticks'])],cwd=s.q.P,stdin=subprocess.DEVNULL,stdout=out,stderr=subprocess.STDOUT,start_new_session=True)
 write('E1_GUARDIAN_STARTED.json',identity(g.pid))
 _,big=train(init,20000,4,900,'slope_snapshot_reviewed_discard20k',True)
 fresh=prior.fresh_resume(big)
 write('E1_COMPLETE_PPO_PREFLIGHT_PASSED.json',dict(epoch=time.time(),small=small,big=big,fresh_same_scope=fresh,weights_discarded=True,SDK_native_small_exact_reused=True,old402_failed_snapshot_literal_preserved=True))
 saved,row=train(init,20000,10000,min(300,s.left()),'e1_SLOPE5_independent_observation',False)
 assert s.q.base.sha(init)==prior.SOURCE_SHA and saved.is_relative_to(D/'learning_logs')
 write('E1_SLOPE_OWNERSHIP_FINAL_VERIFIED.json',dict(epoch=time.time(),own_checkpoint=row['checkpoint'],source_SHA_preserved=True,E0_Wave_CURB_not_optimizer_or_save_targets=True))
 prior.publish(saved);write('E1_REVIEW_READY.json',dict(epoch=time.time(),own_saved_source=str(saved),expert='E1_SLOPE',all_courses_finished=False,requires_actual135_fourcase_review=True,automatic_more_PPO_disallowed=True));phase('E1_SLOPE5_independent_saved_review_ready',child=None)
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--guardian',nargs=2);a=p.parse_args()
 try:
  if a.guardian:guardian(int(a.guardian[0]),int(a.guardian[1]))
  else:main()
 except BaseException:write('E1_ATTENTION.json',dict(epoch=time.time(),error=traceback.format_exc(),own_child_still_alive=bool(s.LIVE and s.LIVE.poll() is None),active_segment=s.q.base.budget_state()['active_segment'],all_weights_retained=True,no_blind_resume=True));raise
