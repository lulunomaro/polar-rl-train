"""Validate in isolation, hand over at a saved checkpoint, run a finite flat budget."""
from pathlib import Path
import datetime
import fcntl
import hashlib
import json
import os
import signal
import subprocess
import time

ROOT=Path('/home/egde/rl_candidates/MOD4_scut_rescue_20260929')
CODE=ROOT/'isaac/mod4'
PY='/home/egde/anaconda3/envs/fangzhen-isaaclab/bin/python'
OLD=Path('/home/egde/fangzhen_linux/runs4090/logs/2026-09-29_01-43-41_flat_v7_4090_20k_scut_warm1850')
OLD_PID=329297
TARGET=4350
DEADLINE=datetime.datetime(2026,9,29,1,43,41).timestamp()+10*3600
ENV=os.environ.copy();ENV.update({k:str(v) for k,v in json.loads((CODE/'env.json').read_text()).items()})
ENV.update(OMNI_KIT_ACCEPT_EULA='YES',PYTHONUNBUFFERED='1',RM_RESCUE_DEADLINE=str(DEADLINE))
REPORTS=ROOT/'reports';REPORTS.mkdir(exist_ok=True)
STATE={}


def status(**kw):
    STATE.update(kw);STATE['updated_at']=time.time()
    p=ROOT/'status.json';tmp=p.with_suffix('.tmp');tmp.write_text(json.dumps(STATE,indent=2));os.replace(tmp,p)
    print(json.dumps(kw),flush=True)


def latest(folder):
    paths=list(folder.glob('**/model_*.pt'))
    return max(paths,key=lambda p:(int(p.stem.split('_')[-1]),p.stat().st_mtime)) if paths else None


def iteration(p):return int(p.stem.split('_')[-1])


def valid_checkpoint(p):
    import torch
    d=torch.load(p,map_location='cpu',weights_only=False)
    if 'optimizer_state_dict' not in d:raise ValueError('checkpoint lacks optimizer')
    if not any(k in d for k in ['model_state_dict','actor_state_dict']):raise ValueError('checkpoint lacks model')
    for key in ['actor_state_dict','critic_state_dict','model_state_dict']:
        for value in d.get(key,{}).values():
            if torch.is_tensor(value) and not torch.isfinite(value).all():raise ValueError('nonfinite checkpoint')
    return {'path':str(p),'iteration_filename':iteration(p),'iteration_stored':d.get('iter'),
            'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'keys':list(d)}


def spawn(args, logfile):
    f=open(logfile,'w')
    return subprocess.Popen([PY]+args,cwd=ROOT,env=ENV,stdout=f,stderr=subprocess.STDOUT,start_new_session=True)


def run(args, logfile, timeout=900):
    p=spawn(args,logfile);status(validation_pid=p.pid)
    try:code=p.wait(timeout=timeout)
    except subprocess.TimeoutExpired:
        p.send_signal(signal.SIGINT);raise RuntimeError('isolated validation timed out; main training not switched')
    return code


def evaluate(ck, name, blocking=True, steps=1500):
    output=REPORTS/(name+'.json')
    args=['isaac/mod4/validate_rescue.py','--headless','--checkpoint',str(ck),
          '--num_envs','64','--steps',str(steps),'--output',str(output)]
    if blocking:
        run(args,REPORTS/(name+'.log'))
        if not output.exists():raise RuntimeError('evaluation did not produce a report: '+name)
        return json.loads(output.read_text())
    return spawn(args,REPORTS/(name+'.log')),output


def active(pid):
    p=Path('/proc')/str(pid)/'stat'
    return p.exists() and p.read_text().split(') ')[1][0]!='Z'


def main():
    lock=open(ROOT/'supervisor.lock','w');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
    status(stage='validating',source_run=str(OLD),target_iteration=TARGET,deadline_epoch=DEADLINE)
    smoke=json.loads((REPORTS/'reset_smoke_ground_fixed.json').read_text())
    if not smoke['physics_pass']:raise RuntimeError('physical reset smoke failed; keeping old training running')
    source=latest(OLD);status(preflight_checkpoint=valid_checkpoint(source))
    code=run(['isaac/mod4/train_mod4_ppo.py','--headless','--num_envs','128',
              '--additional_iterations','2','--steps_per_env','24','--save_interval','1',
              '--learning_rate','0.0001','--seed','20260928','--run_name','rescue_optimizer_smoke',
              '--log_root',str(ROOT/'smoke_logs'),'--init_checkpoint',str(source)],REPORTS/'ppo_smoke.log')
    saved=latest(ROOT/'smoke_logs')
    if saved is None or iteration(saved)<=iteration(source):raise RuntimeError('PPO smoke did not complete two iterations')
    status(ppo_smoke_checkpoint=valid_checkpoint(saved))
    baseline=evaluate(source,'baseline_repaired_environment_3s',steps=300)
    if baseline['nonfinite']:raise RuntimeError('policy evaluation nonfinite; keeping old training')
    status(stage='waiting_for_saved_boundary',baseline=baseline)
    # Observe the next freshly completed save. The outgoing task stays running meanwhile.
    seen=latest(OLD);until=time.time()+1000
    while time.time()<until:
        candidate=latest(OLD)
        if iteration(candidate)>iteration(seen):
            try:info=valid_checkpoint(candidate)
            except Exception:time.sleep(1);continue
            break
        if not active(OLD_PID):
            candidate=latest(OLD);info=valid_checkpoint(candidate);break
        time.sleep(2)
    else:raise RuntimeError('no new safe handover checkpoint; leaving source process alone')
    if active(OLD_PID):
        cmd=Path(f'/proc/{OLD_PID}/cmdline').read_bytes().replace(b'\0',b' ').decode()
        if 'flat_v7_4090_20k_scut_warm1850' not in cmd:raise RuntimeError('source PID changed; refuse to signal')
        status(stage='checkpoint_handover',handover_checkpoint=info)
        os.kill(OLD_PID,signal.SIGINT)
        for _ in range(120):
            if not active(OLD_PID):break
            time.sleep(1)
        if active(OLD_PID):raise RuntimeError('source still alive; refusing double training')
    status(handover_checkpoint=info)
    runlogs=ROOT/'logs';attempt=0;evalproc=None;next_eval=iteration(candidate)+200
    while time.time()<DEADLINE and iteration(candidate)<TARGET:
        train=spawn(['isaac/mod4/train_mod4_ppo.py','--headless','--num_envs','20000',
                     '--target_iteration',str(TARGET),'--steps_per_env','24','--save_interval','25',
                     '--learning_rate','0.0001','--seed','20260928','--run_name','scut_flat_rescue',
                     '--log_root',str(runlogs),'--init_checkpoint',str(candidate)],ROOT/f'train_{attempt}.log')
        status(stage='training',training_pid=train.pid,resume_checkpoint=str(candidate),attempt=attempt)
        while train.poll() is None:
            current=latest(runlogs)
            if current:
                STATE.update(latest_checkpoint=str(current),iteration=iteration(current),log_dir=str(current.parent))
                # Existing terminal monitor can follow this stable read-only pointer.
                pointer=ROOT/'current_run'
                if not pointer.exists():pointer.symlink_to(current.parent,target_is_directory=True)
                if iteration(current)>=next_eval and evalproc is None:
                    evalproc,evalpath=evaluate(current,f'paired_model_{iteration(current)}',blocking=False)
                    next_eval=iteration(current)+200
            if evalproc is not None and evalproc.poll() is not None:
                if evalpath.exists():STATE['latest_evaluation']=json.loads(evalpath.read_text())
                else:STATE['evaluation_error']=str(evalpath)+': missing report; see log'
                evalproc=None
            status(last_health_check=time.time())
            time.sleep(30)
        status(training_exit_code=train.returncode)
        current=latest(runlogs)
        if current:candidate=current
        if train.returncode==0:break
        if attempt>=1 or not current:raise RuntimeError('training failed; saved checkpoints retained')
        valid_checkpoint(candidate);attempt+=1
    if evalproc is not None:evalproc.wait(timeout=900)
    status(stage='final_evaluation')
    final=evaluate(candidate,'final_nominal')
    status(stage='finished',final_checkpoint=valid_checkpoint(candidate),final_evaluation=final,
           outcome='nominal_gate_passed_DR_pending' if final['strict_pass'] else 'nominal_gate_not_passed')


if __name__=='__main__':
    try:main()
    except BaseException:
        import traceback
        error=traceback.format_exc();status(stage='attention_required',error=error);print(error,flush=True)
        raise
