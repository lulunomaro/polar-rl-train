"""Replace only the new controller in a frozen window, never a live PPO."""
from pathlib import Path
import json,os,shutil,signal,subprocess,time
import sys
R=Path('/home/egde/rl_candidates/MOD4_scut_spin_rate_20261002')
sys.path.insert(0,str(R/'isaac/mod4'))
from supervise_mild_trial import identity
import hashlib
ST=Path('/home/egde/rl_candidates/MOD4_AUTONOMY_SLEEP_20261003')
parent_pid=2399838;parent_ticks=13932464
def live(pid):
    p=identity(pid);return p and p['state']!='Z'
start=time.time()
while True:
    p=identity(parent_pid)
    assert p and p['start_ticks']==parent_ticks and p['cwd']==str(R)
    if (R/'reports/AUTONOMY_HANDOVER.json').exists():
        status=json.loads((R/'status.json').read_text())
        b=json.loads(Path(status['canonical_budget']).read_text())
        if status.get('supervisor_pid')==parent_pid and status['stage'].startswith('frozen_') and not b.get('active_segment'):
            os.kill(parent_pid,signal.SIGSTOP)
            status=json.loads((R/'status.json').read_text());b=json.loads(Path(status['canonical_budget']).read_text())
            if b.get('active_segment'):
                os.kill(parent_pid,signal.SIGCONT)
            else:break
    assert time.time()-start<900,'No isolated frozen update window'
    time.sleep(1)
try:
    began=time.time();child=status.get('evaluation_pid')
    if child:
        probe=identity(child)
        assert probe and probe['cwd']==str(R) and any(x.endswith(('/validate_speed.py','/spin_rate_probe.py')) for x in probe['argv'])
        assert status['evaluation_path'].startswith(str(R/'reports/auto_'))
        while live(child):
            assert time.time()-began<600,'Leave original controller to handle a stalled evaluation'
            time.sleep(1)
    b=json.loads(Path(status['canonical_budget']).read_text());assert not b.get('active_segment')
    state=json.loads((R/'reports/AUTONOMY_STATE.json').read_text());assert not state.get('active_training')
    assert identity(parent_pid)['start_ticks']==parent_ticks
    os.kill(parent_pid,signal.SIGKILL)
    while live(parent_pid):time.sleep(.2)
    shutil.copy2(R/'isaac/mod4/supervise_autonomy.py',R/'reports/supervise_autonomy_sleep_v1_retired.py')
    shutil.copy2(ST/'supervise_autonomy_v2.py',R/'isaac/mod4/supervise_autonomy.py')
    m=json.loads((R/'reports/SPIN_SOURCE_FREEZE.json').read_text())
    sha=hashlib.sha256((R/'isaac/mod4/supervise_autonomy.py').read_bytes()).hexdigest()
    m['sha256']['isaac/mod4/supervise_autonomy.py']=sha
    (R/'reports/SPIN_SOURCE_FREEZE.json').write_text(json.dumps(m,indent=2))
    log=R/'supervisor_autonomy_sleep_20261003_v2.log';assert not log.exists()
    with log.open('x') as out:
        p=subprocess.Popen(['/home/egde/anaconda3/envs/fangzhen-isaaclab/bin/python',str(R/'isaac/mod4/supervise_autonomy.py'),'--resume'],
            cwd=R,stdout=out,stderr=subprocess.STDOUT,start_new_session=True)
    time.sleep(2);assert p.poll() is None,log.read_text()
    receipt={'old_pid':parent_pid,'new_pid':p.pid,'source_sha256':sha,'no_PPO_interrupted':True,
      'budget_charged_unchanged':b['charged_training_seconds'],'preserved_completed_probe':status.get('evaluation_path'),
      'fix':'Block actual rejected cap instead of hardcoded six; instantiate guardian on resume',
      'epoch':time.time()}
    (R/'reports/AUTONOMY_CONTROLLER_V2.json').write_text(json.dumps(receipt,indent=2))
    print(json.dumps(receipt),flush=True)
except BaseException:
    if live(parent_pid):os.kill(parent_pid,signal.SIGCONT)
    raise
