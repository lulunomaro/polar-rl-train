"""One small frozen smoke. Production evaluation gets priority; no PPO or ledger writes."""
from pathlib import Path
import json
import os
import signal
import subprocess
import sys
import time

ROOT = Path('/home/egde/rl_candidates/MOD4_fps_turn_candidate_20261003')
REPORTS = ROOT/'reports'
SOURCE = Path('/home/egde/rl_candidates/MOD4_scut_spin_rate_20261002/logs/2026-10-03_00-45-51_scut_spin_rate_continued/model_15583.pt')
PATTERNS = ('/validate_speed.py','/spin_probe.py','/spin_rate_probe.py','/spin_rate_fullscale_probe.py',
            '/spin_fullscale_probe.py','/sensor_fullscale_probe.py','/sensor_readback.py','/turn_probe.py')


def probes(exclude=None):
    found = []
    for proc in Path('/proc').iterdir():
        if not proc.name.isdigit() or int(proc.name) == exclude:
            continue
        try:
            argv = (proc/'cmdline').read_bytes().decode().split('\0')
            if any(any(a.endswith(p) for p in PATTERNS) for a in argv):
                found.append(int(proc.name))
        except (FileNotFoundError, ProcessLookupError, PermissionError):
            pass
    return found


def write(state, **kwargs):
    out = dict(stage=state,worker_pid=os.getpid(),updated_epoch=time.time(),
               source_checkpoint=str(SOURCE),ppo_performed=False,budget_modified=False,**kwargs)
    tmp = REPORTS/'small_preflight_retry1_status.partial'
    tmp.write_text(json.dumps(out, indent=2)); tmp.replace(REPORTS/'small_preflight_retry1_status.json')


assert not (REPORTS/'small_preflight_retry1_status.json').exists(), 'Inspect existing worker instead of duplicating'
assert SOURCE.is_file()
os.environ.update(ISAACSIM_ACCEPT_EULA='Y', OMNI_KIT_ACCEPT_EULA='YES', PYTHONUNBUFFERED='1')
limit = time.time()+1800
while probes():
    assert time.time()<limit, 'Existing evaluation busy; leave production alone'
    write('waiting_existing_evaluation',existing_probes=probes()); time.sleep(5)
out = REPORTS/'turn_model15583_white_seed20261003_3s_retry1.json'
assert not out.exists()
with out.with_suffix('.log').open('w') as log:
    child = subprocess.Popen([sys.executable,'isaac/mod4/turn_probe.py','--headless','--checkpoint',str(SOURCE),
                              '--steps','300','--num_envs','24','--seed','20261003',
                              '--dr-profile','white_v1','--output',str(out)],cwd=ROOT,stdout=log,stderr=subprocess.STDOUT)
    write('frozen_short_physics',evaluation_pid=child.pid,output=str(out))
    while child.poll() is None:
        if probes(exclude=child.pid):
            child.send_signal(signal.SIGINT)
            try: child.wait(timeout=60)
            except subprocess.TimeoutExpired: child.kill(); child.wait()
            write('yielded_to_existing_evaluation',output=str(out))
            sys.exit(0)
        time.sleep(2)
    if child.returncode != 0 or not out.exists():
        write('candidate_program_error',exit_code=child.returncode,output=str(out));sys.exit(1)
r=json.loads(out.read_text())
accept = (r['physical_smoke_pass'] and not r['nonfinite'] and
          r['initial_parameter_audit']['actual_parameters_pass'] and
          r['final_parameter_audit']['actual_parameters_pass'] and
          r['observations']['policy']==[24,35] and r['observations']['critic']==[24,38])
write('short_physics_complete',physical_preflight_pass=accept,output=str(out),
      turn_skill_graduated=False,scope='3s smoke only; no PPO or production switch')
print(json.dumps({'short_physics_pass':accept,'turn_skill_graduated':False,'output':str(out)}),flush=True)
