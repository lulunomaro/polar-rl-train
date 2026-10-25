"""Bounded SCUT continuation; all old runs remain read-only."""
from pathlib import Path
import fcntl
import json
import os
import time
import supervise_rescue as core

ROOT=Path(__file__).resolve().parents[2]
SOURCE=Path('/home/egde/rl_candidates/MOD4_scut_rescue_20260929/logs/2026-09-29_02-37-12_scut_flat_rescue/model_4175.pt')
EXPECTED='fe857432e905e3598ddc4b66f847dd6d1680e84138b7d6909f4ab2a151a5f1c8'
core.ROOT=ROOT;core.CODE=ROOT/'isaac/mod4';core.REPORTS=ROOT/'reports'
core.ENV=os.environ.copy();core.ENV.update({k:str(v) for k,v in json.loads((core.CODE/'env.json').read_text()).items()})
core.ENV.update(OMNI_KIT_ACCEPT_EULA='YES',PYTHONUNBUFFERED='1')
core.ENV.pop('RM_RESCUE_DEADLINE',None)


def main():
    lock=open(ROOT/'continuation.lock','w');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
    # Refuse duplicate trainers without touching another task.
    for p in Path('/proc').glob('[0-9]*/cmdline'):
        try:args=p.read_bytes().split(b'\0')
        except OSError:continue
        if any(a.endswith(b'/train_mod4_ppo.py') for a in args):
            raise RuntimeError(f'an existing MOD4 trainer is active: {p.parent.name}')
    info=core.valid_checkpoint(SOURCE)
    if info['sha256']!=EXPECTED:raise RuntimeError('source hash changed')
    core.status(stage='validating',resume_checkpoint=str(SOURCE),handover_checkpoint=info,budget_seconds=36000)
    baseline=core.evaluate(SOURCE,'baseline4175_contact_audit')
    if not baseline['physics_pass']:raise RuntimeError('baseline physical contract failed')
    core.status(baseline=baseline)
    rc=core.run(['isaac/mod4/train_mod4_ppo.py','--headless','--num_envs','128',
        '--additional_iterations','2','--steps_per_env','24','--save_interval','1',
        '--learning_rate','0.0001','--seed','20260928','--run_name','contact_history_smoke',
        '--log_root',str(ROOT/'smoke_logs'),'--init_checkpoint',str(SOURCE)],core.REPORTS/'ppo_smoke.log')
    saved=core.latest(ROOT/'smoke_logs')
    if rc or saved is None or core.iteration(saved)<=4175:raise RuntimeError('PPO smoke failed')
    core.status(smoke_checkpoint=core.valid_checkpoint(saved))
    deadline=time.time()+36000
    core.ENV['RM_RESCUE_DEADLINE']=str(deadline)
    core.status(started_epoch=time.time(),deadline_epoch=deadline,target_iteration=1000000)
    candidate=SOURCE;evalproc=None;next_eval=time.time()+3600
    for attempt in range(2):
        if time.time()>=deadline:break
        train=core.spawn(['isaac/mod4/train_mod4_ppo.py','--headless','--num_envs','20000',
            '--additional_iterations','100000','--steps_per_env','24','--save_interval','25',
            '--learning_rate','0.0001','--seed','20260928','--run_name','scut_contact_continue10h',
            '--log_root',str(ROOT/'logs'),'--init_checkpoint',str(candidate)],ROOT/f'train_{attempt}.log')
        core.status(stage='training',training_pid=train.pid,attempt=attempt,resume_checkpoint=str(candidate))
        while train.poll() is None:
            latest=core.latest(ROOT/'logs')
            if latest:
                core.STATE.update(latest_checkpoint=str(latest),iteration=core.iteration(latest),log_dir=str(latest.parent))
                if time.time()>=next_eval and evalproc is None and time.time()<deadline-600:
                    evalproc,evalpath=core.evaluate(latest,f'paired_model_{core.iteration(latest)}',blocking=False)
                    next_eval=time.time()+3600
            if evalproc is not None and evalproc.poll() is not None:
                if evalproc.returncode==0 and evalpath.exists():
                    core.STATE['latest_evaluation']=json.loads(evalpath.read_text())
                else:core.STATE['evaluation_error']=str(evalpath)
                evalproc=None
            core.status(last_health_check=time.time())
            time.sleep(20)
        core.status(training_exit_code=train.returncode)
        latest=core.latest(ROOT/'logs')
        if latest:candidate=latest
        if train.returncode==0:break
        if attempt==1 or not latest:raise RuntimeError('training failed; checkpoints retained')
        core.valid_checkpoint(candidate)
    if evalproc is not None:evalproc.wait(timeout=900)
    core.status(stage='final_evaluation')
    final=core.evaluate(candidate,'final_nominal')
    core.status(stage='finished',final_checkpoint=core.valid_checkpoint(candidate),
        final_evaluation=final,latest_evaluation=final,
        outcome='nominal_pass_DR_pending' if final['strict_pass'] else 'nominal_gate_not_passed')


if __name__=='__main__':
    try:main()
    except BaseException:
        import traceback
        core.status(stage='attention_required',error=traceback.format_exc())
        raise
