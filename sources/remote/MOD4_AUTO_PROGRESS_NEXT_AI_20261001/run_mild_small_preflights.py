"""Serialized frozen preflights. Never stops production, runs PPO, or edits its budget."""
from pathlib import Path
import json
import os
import signal
import subprocess
import time
import traceback
import fcntl
from admission_gate import assess

HERE=Path(__file__).resolve().parent
SOURCE=Path('/home/egde/rl_candidates/MOD4_native_floor_continue10h_20260930')
CANDIDATE=Path('/home/egde/rl_candidates/MOD4_mild_dr_trial_20261001')
PY='/home/egde/anaconda3/envs/fangzhen-isaaclab/bin/python'
STATE={}

def status(**values):
    STATE.update(values,updated_epoch=time.time())
    temp=HERE/'small_preflight_status.partial'
    temp.write_text(json.dumps(STATE,indent=2))
    temp.replace(HERE/'small_preflight_status.json')

def evaluators():
    result=[]
    for p in Path('/proc').glob('[0-9]*/cmdline'):
        try:
            argv=p.read_bytes().split(b'\0')
            if any(a.endswith((b'/validate_speed.py',b'/mild_parameter_probe.py')) for a in argv):
                result.append(int(p.parent.name))
        except OSError:pass
    return result

def run(root,args,out):
    if out.exists():return json.loads(out.read_text())
    while evaluators():
        status(stage='waiting_for_existing_evaluation',existing_evaluation_pids=evaluators())
        time.sleep(10)
    log=out.with_suffix('.log')
    if log.exists():raise RuntimeError('Prior incomplete preflight; inspect log before retry: '+str(log))
    environment={k:v for k,v in os.environ.items() if not k.startswith('RM_')}
    environment.update({k:str(v) for k,v in json.loads((root/'isaac/mod4/env.json').read_text()).items()})
    environment.update(ISAACSIM_ACCEPT_EULA='Y',OMNI_KIT_ACCEPT_EULA='YES',PYTHONUNBUFFERED='1')
    with log.open('x') as stream:
        p=subprocess.Popen([PY]+args,cwd=root,env=environment,stdout=stream,stderr=subprocess.STDOUT,start_new_session=True)
    status(stage=out.stem,child_pid=p.pid,child_output=str(out),child_root=str(root))
    started=time.time()
    while p.poll() is None:
        # The existing supervisor has priority. Do not let two probes persist.
        other=[pid for pid in evaluators() if pid!=p.pid]
        if other or time.time()-started>2400:
            p.send_signal(signal.SIGINT)
            try:p.wait(timeout=45)
            except subprocess.TimeoutExpired:
                p.terminate()
                p.wait(timeout=45)
            raise RuntimeError('Preflight interrupted safely: other evaluator or timeout '+str(other))
        time.sleep(10)
    status(child_pid=None,last_returncode=p.returncode)
    if p.returncode or not out.exists():raise RuntimeError('Preflight failed; read '+str(log))
    return json.loads(out.read_text())

try:
    lock=(HERE/'small_preflight.lock').open('a')
    fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
    receipt=json.loads((HERE/'confirmation_launch.json').read_text())
    confirmation=Path(receipt['output'])
    status(supervisor_pid=os.getpid(),production_modified=False,budget_modified=False,
           candidate_checkpoint=receipt['checkpoint'],stage='waiting_confirmation')
    while not confirmation.exists():
        if not Path(f'/proc/{receipt["pid"]}/cmdline').exists():
            raise RuntimeError('Confirmation ended without a report')
        time.sleep(10)
    nominal=assess(json.loads(confirmation.read_text()))
    status(alternate_seed_nominal_admission=nominal)
    if not nominal['eligible_for_mild_dr_trial']:
        raise RuntimeError('Candidate alternate-seed nominal admission failed; keep production nominal')
    parameter=run(CANDIDATE,['isaac/mod4/mild_parameter_probe.py','--headless','--num_envs','80',
                           '--output',str(HERE/'mild_parameter_readback_v3.json')],HERE/'mild_parameter_readback_v3.json')
    if not parameter['pass']:raise RuntimeError('Actual parameter/physical preflight did not pass')
    status(parameter_readback_pass=True)
    ck=receipt['checkpoint']['path']
    def frozen(root,name,seed,profile=None):
        out=HERE/(name+'.json')
        argv=['isaac/mod4/validate_speed.py','--headless','--checkpoint',ck,'--speed_limit','1.5',
              '--ramp_suite','--seed',str(seed),'--num_envs','80','--steps','1500','--output',str(out)]
        if profile is not None:argv += ['--dr-profile',profile]
        return run(root,argv,out)
    dr=frozen(CANDIDATE,'mild_paired_model9425_seed20261001_retry1',20261001,'white_v1')
    dr_admission=assess(dr)
    status(mild_paired_admission=dr_admission)
    if not dr_admission['eligible_for_mild_dr_trial']:
        raise RuntimeError('Frozen mild DR has failures; preserve nominal production and diagnose')
    paired_nominal=frozen(CANDIDATE,'nominal_paired_model9425_seed20261001',20261001,'nominal')
    same_reset=(paired_nominal['reset_joint_pos_before_physics']==dr['reset_joint_pos_before_physics']
                and paired_nominal['reset_root_before_physics']==dr['reset_root_before_physics'])
    status(paired_initial_reset_exactly_equal=same_reset,paired_nominal_admission=assess(paired_nominal))
    assert same_reset,'Same-seed pair began in different poses; diagnose RNG before claiming a paired result'
    assert assess(paired_nominal)['eligible_for_mild_dr_trial'],'Paired nominal admission failed'
    nominal2=frozen(SOURCE,'nominal_confirmation_model9425_seed20260927',20260927)
    nominal2_admission=assess(nominal2)
    status(original_seed_nominal_admission=nominal2_admission)
    assert nominal2_admission['eligible_for_mild_dr_trial'],'Same-candidate second nominal seed failed'
    status(stage='small_frozen_preflights_pass',small_preflights_pass=True,
           remaining_required='Budget-safe save boundary handover, 128env 2-PPO and 20k physical/material preflights; no DR production yet')
except Exception:
    status(stage='preflight_needs_review',error=traceback.format_exc(),child_pid=None,
           production_action='Original nominal training continues untouched')
    raise
