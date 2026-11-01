"""Resume only the remaining authorized compute budget after the host reboot."""
from pathlib import Path
import fcntl
import hashlib
import json
import os
import re
import time
import supervise_rescue as core

ROOT=Path(__file__).resolve().parents[2]
core.ROOT=ROOT;core.CODE=ROOT/'isaac/mod4';core.REPORTS=ROOT/'reports'
core.ENV=os.environ.copy();core.ENV.update({k:str(v) for k,v in json.loads((core.CODE/'env.json').read_text()).items()})
core.ENV.update(OMNI_KIT_ACCEPT_EULA='YES',PYTHONUNBUFFERED='1')


def main():
    lock=open(ROOT/'continuation.lock','w');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
    for p in Path('/proc').glob('[0-9]*/cmdline'):
        try:args=p.read_bytes().split(b'\0')
        except OSError:continue
        if any(a.endswith(b'/train_mod4_ppo.py') for a in args):raise RuntimeError('trainer exists: '+p.parent.name)
    marker=ROOT/'budget_resume_20260929.json'
    if marker.exists():raise RuntimeError('resume already initialized; audit ledger before another launch')
    old=json.loads((ROOT/'status.json').read_text())
    (ROOT/'status_before_reboot_resume_20260929.json').write_text(json.dumps(old,indent=2))
    times=[float(x) for x in re.findall(r'Iteration time:\s*([\d.]+)s',(ROOT/'train_0.log').read_text())]
    used=sum(times);remaining=max(0.,36000-used)
    candidate=core.latest(ROOT/'logs');info=core.valid_checkpoint(candidate)
    if info['iteration_filename']!=4725:raise RuntimeError('latest checkpoint changed; re-audit')
    now=time.time();deadline=now+remaining
    ledger={'authorized_training_seconds':36000,'prior_logged_training_seconds':used,'remaining_seconds':remaining,
        'resume_started_epoch':now,'deadline_epoch':deadline,'source':info,
        'accounting':'sum of completed iteration times includes compute after last surviving checkpoint; downtime excluded per reboot continuation request'}
    marker.write_text(json.dumps(ledger,indent=2))
    core.STATE.update({k:v for k,v in old.items() if k not in ['error','training_exit_code','final_evaluation','final_checkpoint','outcome']})
    core.ENV['RM_RESCUE_DEADLINE']=str(deadline)
    core.status(stage='resuming',resume_checkpoint=str(candidate),handover_checkpoint=info,deadline_epoch=deadline,
        resume_started_epoch=now,budget_ledger=str(marker),remaining_training_seconds_at_resume=remaining,
        gate_version='window_contact_v2_dual_reporting_20260929')
    evalproc=None;next_eval=now
    for attempt in [1,2]:
        if time.time()>=deadline:break
        log=ROOT/f'train_{attempt}.log'
        if log.exists():raise RuntimeError('refuse overwrite '+str(log))
        train=core.spawn(['isaac/mod4/train_mod4_ppo.py','--headless','--num_envs','20000',
            '--additional_iterations','100000','--steps_per_env','24','--save_interval','25',
            '--learning_rate','0.0001','--seed','20260928','--run_name','scut_contact_reboot_resume',
            '--log_root',str(ROOT/'logs'),'--init_checkpoint',str(candidate)],log)
        core.status(stage='training',training_pid=train.pid,attempt=attempt,resume_checkpoint=str(candidate))
        while train.poll() is None:
            latest=core.latest(ROOT/'logs')
            if latest:
                core.STATE.update(latest_checkpoint=str(latest),iteration=core.iteration(latest),log_dir=str(latest.parent))
                if latest.stat().st_mtime>now and time.time()>=next_eval and evalproc is None and time.time()<deadline-600:
                    evalproc,evalpath=core.evaluate(latest,f'resumed_model_{core.iteration(latest)}',blocking=False)
                    next_eval=time.time()+3600
            if evalproc is not None and evalproc.poll() is not None:
                if evalproc.returncode==0 and evalpath.exists():core.STATE['latest_evaluation']=json.loads(evalpath.read_text())
                else:core.STATE['evaluation_error']=str(evalpath)
                evalproc=None
            core.status(last_health_check=time.time());time.sleep(20)
        core.status(training_exit_code=train.returncode)
        latest=core.latest(ROOT/'logs')
        if latest:candidate=latest
        if train.returncode==0:break
        if attempt==2 or not latest:raise RuntimeError('training failed; checkpoint retained')
        core.valid_checkpoint(candidate)
    if evalproc is not None:evalproc.wait(timeout=900)
    core.status(stage='final_evaluation')
    final=core.evaluate(candidate,'final_nominal_after_reboot')
    core.status(stage='finished',final_checkpoint=core.valid_checkpoint(candidate),final_evaluation=final,
        latest_evaluation=final,outcome='window_gate_pass_DR_pending' if final['strict_pass'] else 'window_gate_not_passed')


if __name__=='__main__':
    try:main()
    except BaseException:
        import traceback
        core.status(stage='attention_required',error=traceback.format_exc())
        raise
