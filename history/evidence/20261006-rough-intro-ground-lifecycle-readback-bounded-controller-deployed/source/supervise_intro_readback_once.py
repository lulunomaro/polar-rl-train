"""Own both existing locks for the new trainable task readback, without PPO."""
import sys,subprocess,os,json,time
from pathlib import Path
H=Path(__file__).resolve().parent;F=Path('/home/egde/rl_candidates/MOD4_PHYSICAL_DR_STAGE1_20261006')
sys.path.insert(0,str(F));import supervise_physical_dr_stage1 as old
old.helpers.acquire(old.P/'autonomy_controller.lock');old.helpers.acquire(old.ctl.CANONICAL.parent/'native_floor_supervisor.lock')
old.verify();old.ctl.idle()
assert old.w.read(old.w.STATE)['phase']=='physical_dr_stage1_review_ready'
state=H/'reports/INTRO_READBACK_STATE.json';assert not state.exists(),'Entry already executed'
freeze=old.w.read(H/'reports/SOURCE_FREEZE.json')
for n,sha in freeze['sha256'].items():assert old.base.sha(H/n)==sha,n
before=old.ctl.CANONICAL.read_bytes();out=H/'reports/INTRO_ACTUAL_READBACK.json'
with (H/'intro_readback.log').open('x') as log:
    child=subprocess.Popen([old.base.PY,str(H/'isaac/mod4/rough_intro_probe.py'),'--headless','--output',str(out),'--num_envs','10','--steps','300'],cwd=old.P,env={**os.environ,'ISAACSIM_ACCEPT_EULA':'Y','OMNI_KIT_ACCEPT_EULA':'YES','PYTHONUNBUFFERED':'1'},stdin=subprocess.DEVNULL,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
owner=old.helpers.identity(os.getpid())
old.base.atomic_json(state,dict(phase='new_intro_task_readback',owner=owner,child=old.helpers.identity(child.pid),ppo_performed=False))
code=child.wait();result=old.w.read(out) if out.exists() else None
error=out.with_suffix('.error.json');assert old.ctl.CANONICAL.read_bytes()==before
old.base.atomic_json(state,dict(phase='intro_task_readback_ready' if result and result['pass_'] and not error.exists() else 'intro_readback_repair_hold',owner=owner,child_exit_code=code,error=str(error) if error.exists() else None,output=str(out),ppo_performed=False,canonical_bytes_unchanged=True,finished_epoch=time.time()))
