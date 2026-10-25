"""Checkpoint-boundary speed curriculum. Inherits the existing absolute deadline."""
from pathlib import Path
import os,json,time,signal,fcntl,subprocess,hashlib
import supervise_rescue as core

ROOT=Path(__file__).resolve().parents[2]
core.ROOT=ROOT;core.CODE=ROOT/'isaac/mod4';core.REPORTS=ROOT/'reports'
core.ENV=os.environ.copy()
BASE=json.loads((core.CODE/'env_before_speed.json').read_text())
core.ENV.update({k:str(v) for k,v in BASE.items()})
core.ENV.update(OMNI_KIT_ACCEPT_EULA='YES',PYTHONUNBUFFERED='1')
PLAN=json.loads((ROOT/'speed_handover.json').read_text())
DEADLINE=PLAN['deadline_epoch']
core.ENV['RM_RESCUE_DEADLINE']=str(DEADLINE)

def active(pid):
    return core.active(pid)

def safety_group(g):
    return (g['survival_fraction']>=.95 and g.get('max_tilt') is not None
      and g['max_tilt']<=15 and g['height_error']<=.03
      and g['wheel_effort_clip_fraction']<=.2 and g['leg_effort_clip_fraction']<=.2
      and g['longest_wheel_effort_clip_s']<=.5 and g['wheel_near_no_load']<=.01
      and g['base_force']<=1 and g['guide_force']<=1)

def safety(report,limit):
    gs=[g for g in report['groups'] if abs(g['command_vx'])<=limit+1e-6]
    return report['physics_pass'] and bool(gs) and all(safety_group(g) for g in gs)

def passed(report,limit):
    gs=[g for g in report['groups'] if abs(g['command_vx'])<=limit+1e-6]
    return safety(report,limit) and all(g['strict_pass_window']>=.8 and
       (g.get('profile')!='ramp_brake_reverse' or g['stop_abs_speed']<=.12) for g in gs)

def stop_saved(pid,folder):
    folder=Path(folder);stamp=time.time()
    stop=folder/'STOP_AFTER_SAVE';stop.touch()
    core.status(stage='checkpoint_handover',outgoing_pid=pid)
    while active(pid):
        if time.time()-stamp>1200:raise RuntimeError('save-boundary stop timed out; no second trainer started')
        time.sleep(5)
    ck=core.latest(folder)
    if ck is None or ck.stat().st_mtime<stamp:raise RuntimeError('outgoing process did not produce a new full checkpoint')
    info=core.valid_checkpoint(ck)
    core.status(handover_checkpoint=info)
    return ck

def evaluate(ck,limit,seed,name):
    output=core.REPORTS/(name+'.json')
    if output.exists():raise RuntimeError('refuse evaluation overwrite: '+str(output))
    p=core.spawn(['isaac/mod4/validate_speed.py','--headless','--checkpoint',str(ck),
        '--speed_limit',str(limit),'--ramp_suite','--seed',str(seed),
        '--num_envs','80','--steps','1500','--output',str(output)],output.with_suffix('.log'))
    return p,output

def write_env(limit):
    e=dict(BASE,RM_CMD_VX_MIN=str(-limit),RM_CMD_VX_MAX=str(limit))
    # Keep 10% standing and a uniform moving range: slow samples remain represented.
    assert e['RM_REL_STANDING']=='0.1' and e['RM_DR_OFF']=='1' and e['RM_KEEP_STD']=='1'
    core.ENV.update(e)
    (core.CODE/'env.json').write_text(json.dumps(e,indent=2))
    return e

def main():
    lock=open(ROOT/'continuation.lock','w');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
    core.STATE.update(json.loads((ROOT/'status.json').read_text()))
    core.STATE.pop('final_evaluation',None)
    preflight=json.loads((core.REPORTS/'speed_preflight_2m.json').read_text())
    if not safety(preflight,1.5):raise RuntimeError('1.5m/s preflight unsafe: retaining current trainer and parameters')
    step_smoke=json.loads((core.REPORTS/'speed_step15_smoke.json').read_text())
    if not safety(step_smoke,1.5):raise RuntimeError('1.5m/s abrupt command unsafe: no training handover')
    core.status(speed_preflight=str(core.REPORTS/'speed_preflight_2m.json'),deadline_epoch=DEADLINE)
    candidate=stop_saved(PLAN['outgoing_pid'],PLAN['outgoing_log_dir'])
    (ROOT/'speed_baseline_checkpoint.json').write_text(json.dumps(core.valid_checkpoint(candidate),indent=2))
    limit=1.5;attempt=3;evalproc=None;evalpath=None;last_eval={};final=None
    while time.time()<DEADLINE:
        for p in Path('/proc').glob('[0-9]*/cmdline'):
            try:args=p.read_bytes().split(b'\0')
            except OSError:continue
            if any(a.endswith(b'/train_mod4_ppo.py') for a in args):raise RuntimeError('another trainer exists '+str(p.parent))
        cfg=write_env(limit);log=ROOT/f'train_{attempt}.log'
        if log.exists():raise RuntimeError('refuse training log overwrite')
        start_iter=core.iteration(candidate);promotion=False;now=time.time()
        train=core.spawn(['isaac/mod4/train_mod4_ppo.py','--headless','--num_envs','20000',
          '--additional_iterations','100000','--steps_per_env','24','--save_interval','25',
          '--learning_rate','0.0001','--seed','20260928','--run_name',f'scut_speed_{limit:g}m',
          '--log_root',str(ROOT/'logs'),'--init_checkpoint',str(candidate)],log)
        core.status(stage='training',training_pid=train.pid,attempt=attempt,resume_checkpoint=str(candidate),
          speed_limit_m_s=limit,speed_curriculum='1.5m -> 2m; DR off; 10% standing',
          active_environment=cfg,deadline_epoch=DEADLINE,stage_started_iteration=start_iter)
        next_eval_iter=start_iter+100;next_eval_time=now
        while train.poll() is None:
            ck=core.latest(ROOT/'logs')
            if ck and ck.stat().st_mtime>now:
                candidate=ck
                core.STATE.update(latest_checkpoint=str(ck),iteration=core.iteration(ck),log_dir=str(ck.parent))
                if core.iteration(ck)>=next_eval_iter and time.time()>=next_eval_time and evalproc is None and time.time()<DEADLINE-900:
                    seed=20260927 if limit==1.5 else 20260928
                    evalproc,evalpath=evaluate(ck,limit,seed,f'speed_{limit:g}m_model{core.iteration(ck)}')
                    core.status(evaluation_pid=evalproc.pid,evaluation_path=str(evalpath))
                    next_eval_time=time.time()+3600
            if evalproc is not None and evalproc.poll() is not None:
                if evalproc.returncode==0 and evalpath.exists():
                    final=json.loads(evalpath.read_text());last_eval[limit]=final
                    core.status(latest_evaluation=final,speed_gate_passed=passed(final,limit),
                      speed_safety_passed=safety(final,limit),evaluation_error=None)
                    if limit==1.5 and passed(final,1.5) and safety(final,2.):
                        candidate=stop_saved(train.pid,core.STATE['log_dir']);promotion=True
                    # A failed performance gate does not reset training or change physics.
                else:core.status(evaluation_error=str(evalpath))
                evalproc=None
            core.status(last_health_check=time.time());time.sleep(20)
        train.wait();core.status(training_exit_code=train.returncode)
        latest=core.latest(ROOT/'logs')
        if latest:candidate=latest
        if promotion:
            limit=2.;attempt+=1;continue
        if train.returncode!=0 and time.time()<DEADLINE:
            raise RuntimeError('training failed; complete checkpoint preserved for audited recovery')
        break
    if evalproc is not None:
        evalproc.wait(timeout=1200)
        if evalproc.returncode==0 and evalpath.exists():core.STATE['latest_evaluation']=json.loads(evalpath.read_text())
    core.status(stage='final_evaluation')
    ep,out=evaluate(candidate,limit,20260926,'final_speed_nominal')
    if ep.wait(timeout=1500)!=0:raise RuntimeError('final speed evaluation failed')
    final=json.loads(out.read_text())
    core.status(stage='finished',final_checkpoint=core.valid_checkpoint(candidate),final_evaluation=final,
      latest_evaluation=final,outcome='speed_gate_pass_DR_pending' if passed(final,limit) else 'speed_gate_not_passed')

if __name__=='__main__':
    try:main()
    except BaseException:
        import traceback
        core.status(stage='attention_required',error=traceback.format_exc())
        raise
