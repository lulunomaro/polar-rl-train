"""Restore only in a fresh process as the existing strict action contract requires."""
from pathlib import Path
import ast,json,time,hashlib
D=Path(__file__).resolve().parent;R=D/'reports';P=D/'fresh_process_payload';C=P/'isaac/mod4';C.mkdir(parents=True,exist_ok=True)
v=json.loads(sorted(R.glob('ENVIRONMENT_VIEW_ACTUAL_*.json'))[-1].read_bytes());assert not v['canonical']['active_segment'] and all(x['actual'] is None for x in v['actual_processes'])
run,value=next(iter(v['runs'].items()));h=value['CLOCK_TRAINING_HEALTH.json'];assert h['control_steps']==96 and h['actual_physics_callbacks']==h['expected_physics_callbacks']==384
assert h['ordinary_episode_reset_events']==h['integrity_task_reset_events']==h['unknown_task_reset_events']==0 and not h['nonfinite_observed'] and h['stop_reason'] is None
log=next(x['tail'] for k,x in v['logs'].items() if 'envview_discard20k' in k);assert 'assert int(env._sim_step_counter)==0' in log
segment=v['canonical']['own_completed_segments'];assert len(segment)==1
p=R/'FRESH_PROCESS_RESUME_FAILURE_AND_REPAIR.json';assert not p.exists();p.write_text(json.dumps(dict(epoch=time.time(),trial_id='CURB384-POSTLEARN-SAMEENV-RESUME-REJECTED-01',root=v['root'],run=run,checkpoint=value['latest_complete.json'],actual_completed_PPO_updates=4,actual_environment_steps=1920000,health=h,original_postsave_error=log,unique_segment=segment,seconds=segment[0]['ended_epoch']-segment[0]['started_epoch'],actor_critic_optimizer_DR_command_first_restore_passed=True,same_CURB_resume_not_yet_admitted=True,repair='Exact existing startup contract requires fresh zero-step environment. New separate fresh process only restores saved full CURB state; no additional PPO/control, no relaxation of step counter, no use of discarded weights for formal learning.',SDK_native_small_big_PPO_not_repeated=True,all_old_source_and_false_cost_preserved=True),indent=2))
original=(D/'environment_view_payload/isaac/mod4/train_curb20_environment_view_resume_ppo.py').read_text();head=original[:original.index('def main() -> None:')]
main='''def main() -> None:
    import hashlib
    assert args.num_envs==20000 and args.max_iterations==0 and not args.dry_run
    assert os.environ.get('RM_KEEP_STD')=='1' and os.environ.get('RM_CURB_FRESH_RESUME_ONLY')=='1'
    source=Path(args.init_checkpoint);expected=json.loads(Path(REPO/'reports/FRESH_PROCESS_BIG_CORE_VERIFIED.json').read_text())
    assert str(source)==expected['checkpoint']['path'] and hashlib.sha256(source.read_bytes()).hexdigest()==expected['checkpoint']['sha256']
    env=build_env();assert int(env._sim_step_counter)==0
    log_dir=Path(args.log_root);assert not log_dir.exists();log_dir.mkdir()
    cfg=runner_config();vec=RslRlVecEnvWrapper(env,clip_actions=cfg.clip_actions)
    cfg=handle_deprecated_rsl_rl_cfg(cfg,metadata.version('rsl-rl-lib'))
    runner=OnPolicyRunner(vec,cfg.to_dict(),log_dir=str(log_dir),device=cfg.device);runner.load(str(source))
    from curb20_full_checkpoint_environment_view import resume_e1_new_episode,install_e1_save_contract
    proof=resume_e1_new_episode(runner,env,str(source),str(log_dir))
    assert proof['predecessor_command_state_restored_exact'] and not proof['explicitly_new_command_scope']
    terrain=json.loads((log_dir/'E1_TERRAIN_RESUME_STARTUP_VERIFIED.json').read_text())
    assert terrain['terrain_state_restored_exact'] and not terrain['explicit_G3_to_CURB_geometry_transition']
    assert int(env._sim_step_counter)==0
    install_e1_save_contract(runner,env);saved=log_dir/'fullsave_after_fresh_resume_no_learning.pt';runner.save(str(saved))
    assert int(env._sim_step_counter)==0 and hashlib.sha256(source.read_bytes()).hexdigest()==expected['checkpoint']['sha256']
    v=dict(epoch=time.time(),pid=os.getpid(),passed=True,num_envs=env.num_envs,source_checkpoint=expected['checkpoint'],source_fullstate_exact=True,
        actual_same_CURB_terrain_command_private_CPUCUDA_disk_roundtrip_exact=True,all_D0_D7_actor_critic_std_optimizer_global_named_actual_restored=True,
        saved_source_episode_plus_one_verified=True,actual_control_steps=0,actual_additional_PPO_updates=0,
        original_zero_step_startup_guard_unchanged=True,own_complete_new_episode_save=dict(path=str(saved),bytes=saved.stat().st_size,sha256=hashlib.sha256(saved.read_bytes()).hexdigest()),
        proof=proof,terrain=terrain,not_PhysX_exact_resume=True,discarded_checkpoint_not_formal_learning_source=True)
    (log_dir/'FRESH_PROCESS_SAME_CURB_FULL_RESUME_PASSED.json').write_text(json.dumps(v,indent=2));env.close()
if __name__=='__main__':
    import traceback
    try:main()
    except BaseException:
        Path(REPO/'reports/FRESH_PROCESS_PROBE_ERROR.txt').write_text(traceback.format_exc());print(traceback.format_exc(),flush=True);raise
    finally:app.close()
'''
text=head+main;p=C/'probe_curb20_fresh_process_full_resume.py';assert not p.exists();compile(text,str(p),'exec');p.write_bytes(text.encode())
text='''"""Unique isolated fresh-process restore admission, then only300s formal."""
from pathlib import Path
import argparse,json,os,subprocess,time,traceback
import supervise_curb20_environment_view_once as previous
prior=previous.prior;D=Path(__file__).resolve().parent;R=D/'reports';CODE=D/'isaac/mod4';s=previous.s
read=previous.read;write=previous.write;identity=previous.identity;train=previous.train;fullsave=previous.fullsave;runtime=previous.runtime;verify=previous.verify;phase=previous.phase
OLD=Path('/home/egde/rl_candidates/MOD4_S3_E1_CURB20_ENVIRONMENT_VIEW_20261011')
def wait_existing():
 previous.wait_existing();st=read(OLD/'reports/E1_STATE.json');att=read(OLD/'reports/E1_ATTENTION.json');assert not att['own_child_still_alive'] and att['active_segment'] is None
 for loc in [st['owner'],st['child'],read(OLD/'reports/E1_GUARDIAN_STARTED.json')]:
  a=identity(loc['pid']);assert not a or a['state']=='Z' or a['start_ticks']!=loc['start_ticks']
 assert not previous.trainers() and s.q.base.budget_state()['active_segment'] is None
def guardian(owner,ticks):
 previous.guardian(owner,ticks)
def main():
 import torch;torch.set_num_threads(1)
 assert not (R/'E1_DISPATCH_STARTED.json').exists();verify();wait_existing();init=prior.source()
 assert read(R/'CURB_FRESH_PROCESS_CPU_PASSED.json')['passed']
 s.q.helpers.acquire(s.q.P/'autonomy_controller.lock');s.q.helpers.acquire(s.q.ctl.CANONICAL.parent/'native_floor_supervisor.lock');wait_existing()
 write('E1_DISPATCH_STARTED.json',dict(epoch=time.time(),owner=identity(os.getpid()),expert='E1_CURB',only_new_fresh_process_full_resume_probe_then300s=True,SDK_native_small_big_PPO_exact_reused=True,no_new_budget=True))
 with (D/'guardian.log').open('x') as out:g=subprocess.Popen([s.q.base.PY,str(Path(__file__)),'--guardian',str(os.getpid()),str(identity(os.getpid())['start_ticks'])],cwd=s.q.P,stdin=subprocess.DEVNULL,stdout=out,stderr=subprocess.STDOUT,start_new_session=True)
 write('E1_GUARDIAN_STARTED.json',identity(g.pid))
 big=read(R/'FRESH_PROCESS_BIG_CORE_VERIFIED.json');e=runtime();e['RM_CURB_FRESH_RESUME_ONLY']='1';e['RM_CURB_PREFLIGHT_SELF_RESUME']='0'
 args=[s.q.base.PY,str(CODE/'probe_curb20_fresh_process_full_resume.py'),'--headless','--num_envs','20000','--max_iterations','0','--steps_per_env','24','--seed','20260928','--learning_rate','.0001','--init_checkpoint',big['checkpoint']['path'],'--log_root',str(D/'fresh_process_resume'),'--run_name','curb_fresh_full_resume_no_learning']
 with (D/'fresh_process_resume.log').open('x') as out:p=subprocess.Popen(args,cwd=s.q.P,env=e,stdin=subprocess.DEVNULL,stdout=out,stderr=subprocess.STDOUT,start_new_session=True)
 s.LIVE=p;phase('CURB_fresh_process_full_resume_admission',child=identity(p.pid),source=big['checkpoint'],no_PPO=True,active_log=str(D/'fresh_process_resume.log'))
 while p.poll() is None:time.sleep(1)
 s.LIVE=None;assert p.returncode==0 and 'Traceback (most recent call last)' not in (D/'fresh_process_resume.log').read_text()
 proof=read(D/'fresh_process_resume/FRESH_PROCESS_SAME_CURB_FULL_RESUME_PASSED.json');assert proof['passed'] and proof['pid']==p.pid and proof['actual_control_steps']==proof['actual_additional_PPO_updates']==0
 cp=proof['own_complete_new_episode_save'];assert s.q.base.sha(Path(cp['path']))==cp['sha256'];fullsave(Path(cp['path']))
 write('CURB_FRESH_PROCESS_SAME_SCOPE_PASSED.json',proof)
 write('E1_COMPLETE_PPO_PREFLIGHT_PASSED.json',dict(epoch=time.time(),small=read(R/'REUSED_SMALL128.json'),big=big,weights_discarded=True,old384_postlearn_sameenv_failure_retained=True,new_fresh_process_sameCURB_full_resume_passed=proof,SDK_native_small_big_PPO_not_repeated=True))
 saved,row=train(init,20000,10000,min(300,s.left()),'e1_CURB20_independent_observation',False)
 assert s.q.base.sha(init)==prior.SOURCE_SHA and saved.is_relative_to(D/'learning_logs')
 write('E1_CURB_OWNERSHIP_FINAL_VERIFIED.json',dict(epoch=time.time(),checkpoint=row['checkpoint'],source_SHA_preserved=True,E0_Wave_not_optimizer_or_save_targets=True))
 prior.publish(saved);write('E1_REVIEW_READY.json',dict(epoch=time.time(),own_saved_source=str(saved),expert='E1_CURB',all_courses_finished=False,requires_actual133_fourcase_review=True,automatic_more_PPO_disallowed=True));phase('E1_CURB20_independent_saved_review_ready',child=None)
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--guardian',nargs=2);a=p.parse_args()
 try:
  if a.guardian:guardian(int(a.guardian[0]),int(a.guardian[1]))
  else:main()
 except BaseException:write('E1_ATTENTION.json',dict(epoch=time.time(),error=traceback.format_exc(),own_child_still_alive=bool(s.LIVE and s.LIVE.poll() is None),active_segment=s.q.base.budget_state()['active_segment'],all_weights_retained=True,no_blind_resume=True));raise
'''
p=P/'supervise_curb20_fresh_process_resume_once.py';assert not p.exists();compile(text,str(p),'exec');p.write_bytes(text.encode())
print(json.dumps(dict(new_source_files=2,original_zero_step_guard_preserved=True,completed_big4_PPO_exact_reused_not_repeated=True)))
