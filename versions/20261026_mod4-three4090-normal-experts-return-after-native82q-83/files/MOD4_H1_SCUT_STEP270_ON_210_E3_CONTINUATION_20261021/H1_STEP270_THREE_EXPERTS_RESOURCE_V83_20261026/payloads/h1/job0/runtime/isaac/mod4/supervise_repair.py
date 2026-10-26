"""Adopt the live trainer, then resume at a complete save with an extended budget."""
from pathlib import Path
import os, json, time, fcntl, subprocess, traceback, hashlib
import supervise_rescue as core

ROOT=Path(__file__).resolve().parents[2]
BUDGET=json.loads((ROOT/'budget_extension_20260930.json').read_text())
OLD=Path(BUDGET['old_root'])
DEADLINE=BUDGET['deadline_epoch']
core.ROOT=ROOT;core.CODE=ROOT/'isaac/mod4';core.REPORTS=ROOT/'reports'
core.ENV=os.environ.copy()
core.ENV.update(OMNI_KIT_ACCEPT_EULA='YES',PYTHONUNBUFFERED='1',RM_RESCUE_DEADLINE=str(DEADLINE))

def configure(limit):
    cfg=json.loads((core.CODE/'env.json').read_text())
    cfg.update(RM_CMD_VX_MIN=str(-limit),RM_CMD_VX_MAX=str(limit))
    assert cfg['RM_DR_OFF']=='1' and cfg['RM_GYRO_CURRICULUM']=='0'
    core.ENV.update({k:str(v) for k,v in cfg.items()})
    (core.CODE/'env.json').write_text(json.dumps(cfg,indent=2))
    return cfg

def trainers():
    found=[]
    for p in Path('/proc').glob('[0-9]*/cmdline'):
        try:a=p.read_bytes().split(b'\0')
        except OSError:continue
        if any(x.endswith(b'/train_mod4_ppo.py') for x in a):found.append(int(p.parent.name))
    return found

def launch_train(ck,limit,attempt):
    if trainers():raise RuntimeError('Refusing second trainer: '+str(trainers()))
    cfg=configure(limit)
    path=ROOT/f'train_repair_{attempt}.log'
    if path.exists():raise RuntimeError('refuse log overwrite')
    proc=core.spawn(['isaac/mod4/train_mod4_ppo.py','--headless','--num_envs','20000',
      '--additional_iterations','100000','--steps_per_env','24','--save_interval','25',
      '--learning_rate','0.0001','--seed','20260928','--run_name',f'scut_straight_{limit:g}m_repair',
      '--log_root',str(ROOT/'logs'),'--init_checkpoint',str(ck)],path)
    core.status(stage='training',training_pid=proc.pid,attempt=attempt,active_log=str(path),
      resume_checkpoint=core.valid_checkpoint(ck),speed_limit_m_s=limit,active_environment=cfg,
      trainer_deadline_epoch=DEADLINE,gyro_curriculum_enabled=False)
    return proc

def evaluate(ck,limit,name,seed=20260927):
    path=core.REPORTS/(name+'.json')
    if path.exists():raise RuntimeError('refuse evaluation overwrite')
    proc=core.spawn(['isaac/mod4/validate_speed.py','--headless','--checkpoint',str(ck),
        '--speed_limit',str(limit),'--ramp_suite','--seed',str(seed),'--num_envs','80',
        '--steps','1500','--output',str(path)],path.with_suffix('.log'))
    core.status(evaluation_pid=proc.pid,evaluation_path=str(path))
    return proc,path

def safe_group(g):
    return (g.get('survival_fraction',0)>=.95 and g.get('max_tilt') is not None
      and g['max_tilt']<=15 and g['height_error']<=.03
      and g['wheel_effort_clip_fraction']<=.2 and g['leg_effort_clip_fraction']<=.2
      and g['longest_wheel_effort_clip_s']<=.5 and g['wheel_near_no_load']<=.01
      and g['base_force']<=1 and g['guide_force']<=1)

def gate(r,limit):
    groups=[g for g in r.get('groups',[]) if abs(g['command_vx'])<=limit+1e-6]
    required={(0.,'constant'),(.3,'constant'),(.6,'constant'),(1.,'constant'),
              (-limit,'constant'),(limit,'constant'),(-1.5,'ramp_brake_reverse'),(1.5,'ramp_brake_reverse')}
    seen={(g['command_vx'],g['profile']) for g in groups}
    return (r.get('seconds')==15 and r.get('physics_pass',False) and not r.get('nonfinite',True)
      and required<=seen and all(safe_group(g) and g['strict_pass_window']>=.8
      and (g['profile']!='ramp_brake_reverse' or g['stop_abs_speed']<=.12) for g in groups))

def main():
    lock=open(ROOT/'supervisor.lock','w');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
    # Also retain the old workspace's coordination lock after its supervisor exits.
    oldlock=open(OLD/'continuation.lock','a');fcntl.flock(oldlock,fcntl.LOCK_EX|fcntl.LOCK_NB)
    source=json.loads((ROOT/'source_status.json').read_text())
    pid=BUDGET['original_trainer_pid'];folder=Path(BUDGET['original_log_dir'])
    ck=core.latest(folder)
    core.STATE.update(latest_evaluation=source.get('latest_evaluation'))
    core.status(stage='budget_extended_waiting_repair',deadline_epoch=DEADLINE,
      old_deadline_epoch=BUDGET['previous_deadline_epoch'],training_pid=pid,log_dir=str(folder),
      active_log=str(OLD/'train_3.log'),latest_checkpoint=str(ck),iteration=core.iteration(ck),
      trainer_deadline_epoch=BUDGET['previous_deadline_epoch'],speed_limit_m_s=1.5,
      gyro_curriculum_enabled=True,source_root=str(OLD),budget_file=str(ROOT/'budget_extension_20260930.json'))
    requested=None
    while core.active(pid):
        ck=core.latest(folder)
        core.status(latest_checkpoint=str(ck),iteration=core.iteration(ck),last_health_check=time.time())
        ready=ROOT/'REPAIR_READY.json'
        if ready.exists() and requested is None:
            data=json.loads(ready.read_text())
            if not data.get('preflight_pass'):raise RuntimeError('repair not validated')
            for n,h in data['code_sha256'].items():
                if hashlib.sha256((core.CODE/n).read_bytes()).hexdigest()!=h:raise RuntimeError('ready code changed '+n)
            cmd=Path(f'/proc/{pid}/cmdline').read_bytes()
            if b'scut_speed_1.5m' not in cmd:raise RuntimeError('outgoing PID identity changed')
            requested=time.time();(folder/'STOP_AFTER_SAVE').touch()
            core.status(stage='checkpoint_handover',handover_requested_epoch=requested)
        if requested and time.time()-requested>1200:raise RuntimeError('save boundary timed out')
        if time.time()>=BUDGET['previous_deadline_epoch'] and requested is None:
            core.status(stage='attention_required',error='old deadline approaching without repair preflight')
        time.sleep(10)
    ck=core.latest(folder);core.valid_checkpoint(ck)
    if requested is None:raise RuntimeError('outgoing trainer ended before verified handover')
    if ck.stat().st_mtime<requested:raise RuntimeError('no fresh complete save after request')
    core.status(handover_checkpoint=core.valid_checkpoint(ck))
    limit=1.5;attempt=0;streak=0;evalproc=None;next_eval=time.time()+1800
    while time.time()<DEADLINE:
        started=time.time();proc=launch_train(ck,limit,attempt);promotion=False
        while proc.poll() is None:
            current=core.latest(ROOT/'logs')
            if current and current.stat().st_mtime>=started:
                ck=current
                core.STATE.update(latest_checkpoint=str(ck),iteration=core.iteration(ck),log_dir=str(ck.parent))
                if evalproc is None and time.time()>=next_eval and time.time()<DEADLINE-900:
                    evalproc,evalpath=evaluate(ck,limit,f'repair_{limit:g}m_model{core.iteration(ck)}')
                    next_eval=time.time()+3600
            if evalproc is not None and evalproc.poll() is not None:
                if evalproc.returncode==0 and evalpath.exists():
                    r=json.loads(evalpath.read_text());passed=gate(r,limit);streak=streak+1 if passed else 0
                    extrap=r.get('physics_pass',False) and all(safe_group(g) for g in r['groups'])
                    core.status(latest_evaluation=r,speed_gate_passed=passed,consecutive_passes=streak,
                      speed_safety_passed=extrap,evaluation_error=None)
                    if limit==1.5 and streak>=2 and extrap:
                        (ck.parent/'STOP_AFTER_SAVE').touch();promotion=True
                else:core.status(evaluation_error=str(evalpath))
                evalproc=None;core.STATE['evaluation_pid']=None
            core.status(last_health_check=time.time());time.sleep(15)
        proc.wait();core.status(training_exit_code=proc.returncode)
        current=core.latest(ROOT/'logs')
        if current:ck=current
        if proc.returncode!=0:raise RuntimeError('training error; checkpoint preserved; inspect before recovery')
        if promotion:limit=2.;streak=0;attempt+=1;next_eval=time.time()+3600;continue
        break
    if evalproc is not None:evalproc.wait(timeout=1500)
    core.status(stage='final_evaluation')
    ep,out=evaluate(ck,limit,'final_speed_nominal',seed=20260926)
    if ep.wait(timeout=1800)!=0:raise RuntimeError('final evaluation failed')
    r=json.loads(out.read_text())
    core.status(stage='finished',final_checkpoint=core.valid_checkpoint(ck),final_evaluation=r,
      latest_evaluation=r,outcome='nominal_pass_DR_pending' if gate(r,limit) else 'nominal_gate_not_passed')

if __name__=='__main__':
    try:main()
    except BaseException:
        error=traceback.format_exc();core.status(stage='attention_required',error=error);raise
