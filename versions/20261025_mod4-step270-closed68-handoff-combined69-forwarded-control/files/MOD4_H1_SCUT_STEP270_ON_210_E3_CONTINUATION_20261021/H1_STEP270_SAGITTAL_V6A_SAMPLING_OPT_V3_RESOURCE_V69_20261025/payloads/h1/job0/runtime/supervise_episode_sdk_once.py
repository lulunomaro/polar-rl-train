from pathlib import Path
import sys,json,time,subprocess,traceback
D=Path(__file__).resolve().parent;R=D/'reports';sys.path.insert(0,str(D));import supervise_episode_repair as w
s=w.s
try:
 assert not (R/'SDK_STARTED.json').exists();w.verify_repair()
 s.q.helpers.acquire(s.q.P/'autonomy_controller.lock');s.q.helpers.acquire(s.q.ctl.CANONICAL.parent/'native_floor_supervisor.lock')
 assert not s.trainers() and s.q.base.budget_state()['active_segment'] is None and not s.q.w.read(s.q.ctl.STATE_PATH).get('active_training')
 before=s.q.ctl.CANONICAL.read_bytes();init=Path('/home/egde/rl_candidates/MOD4_DT2500_SOLVER32_TRAINING_TEST_20261007/reports/solver32_formal45_PASSED.json');source=s.q.w.read(init)['checkpoint'];assert s.q.base.sha(Path(source['path']))==w.SOURCE_SHA
 s.write('SDK_STARTED.json',dict(epoch=time.time(),owner=s.identity(__import__('os').getpid()),no_PPO=True,source=source))
 args=[s.q.base.PY,str(D/'supervision_sdk_probe.py'),'--dt','.0025','--checkpoint',source['path'],'--num_envs','10','--warmup','24','--steps','300','--profile_steps','0','--output',str(R/'SUPERVISION_SDK.json'),'--headless']
 with (D/'sdk.log').open('x') as f:p=subprocess.Popen(args,cwd=s.q.P,env=s.runtime(),stdin=subprocess.DEVNULL,stdout=f,stderr=subprocess.STDOUT,start_new_session=True)
 s.write('SDK_CHILD.json',s.identity(p.pid));p.wait(timeout=900)
 assert p.returncode==0 and not Path(str(R/'SUPERVISION_SDK.json')+'.error').exists() and 'Traceback (most recent last)' not in (D/'sdk.log').read_text(errors='replace')
 r=s.q.w.read(R/'SUPERVISION_SDK.json');fixture=r['supervision_fixture'];h=fixture['health']
 assert fixture['ordinary_verified'] and fixture['integrity_verified'] and fixture['actual_SDK_manager_fault_injection_only']
 assert h['ordinary_episode_reset_events']==1 and h['integrity_task_reset_events']==1 and h['termination_events_by_reason']['bad_orientation']==1 and h['termination_events_by_reason']['closure']==1
 assert h['actual_physics_callbacks']==h['expected_physics_callbacks']==1296 and not r['nonfinite'] and r['max_closure_error_m']<=.002 and r['max_mimic_error_rad']<=.01
 assert before==s.q.ctl.CANONICAL.read_bytes()
 s.write('SUPERVISION_SDK_PASSED.json',dict(epoch=time.time(),passed=True,output_sha256=s.q.base.sha(R/'SUPERVISION_SDK.json'),fixture=fixture,actual_max_closure_m=r['max_closure_error_m'],no_PPO_or_budget_change=True,physics_failure_not_claimed=True,actual_manager_and_reset_lifecycle_verified=True))
except BaseException:
 s.write('SDK_ATTENTION.json',dict(epoch=time.time(),error=traceback.format_exc(),no_PPO=True));raise
