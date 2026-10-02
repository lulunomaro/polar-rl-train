"""Four frozen 15s baselines, with existing evaluations taking priority. Never PPO."""
from pathlib import Path
import json
import os
import signal
import subprocess
import sys
import time
import hashlib

ROOT = Path('/home/egde/rl_candidates/MOD4_fps_turn_candidate_20261003')
REPORTS = ROOT/'reports'
SOURCE = Path('/home/egde/rl_candidates/MOD4_scut_spin_rate_20261002/logs/2026-10-03_00-45-51_scut_spin_rate_continued/model_15583.pt')
PATTERNS = ('/validate_speed.py','/spin_probe.py','/spin_rate_probe.py','/spin_rate_fullscale_probe.py',
            '/spin_fullscale_probe.py','/sensor_fullscale_probe.py','/sensor_readback.py','/turn_probe.py')


def probes(exclude=None):
    result=[]
    for p in Path('/proc').iterdir():
        if not p.name.isdigit() or int(p.name)==exclude:continue
        try:
            argv=(p/'cmdline').read_bytes().decode().split('\0')
            if any(any(a.endswith(pattern) for pattern in PATTERNS) for a in argv):result.append(int(p.name))
        except (FileNotFoundError,ProcessLookupError,PermissionError):pass
    return result


def status(stage, **kw):
    data=dict(stage=stage,worker_pid=os.getpid(),updated_epoch=time.time(),source=str(SOURCE),
              ppo_performed=False,budget_modified=False,production_modified=False,**kw)
    p=REPORTS/'long_baselines_status.partial';p.write_text(json.dumps(data,indent=2))
    p.replace(REPORTS/'long_baselines_status.json')


assert not (REPORTS/'long_baselines_status.json').exists(), 'Inspect the existing worker instead of duplicating'
assert hashlib.sha256(SOURCE.read_bytes()).hexdigest()=='c24b436ac7a8e1776fd4c6978365d1348bde6b8fd1dd263f0b9416fe21ca0657'
os.environ.update(ISAACSIM_ACCEPT_EULA='Y',OMNI_KIT_ACCEPT_EULA='YES',PYTHONUNBUFFERED='1')
started=time.time();reports={}
for seed in (20261003,20261004):
    for profile in ('nominal','white_v1'):
        while probes():
            assert time.time()-started<4*3600, 'Leave busy production alone; resume only after reviewing reports'
            status('waiting_existing_evaluation',seed=seed,profile=profile,existing_probes=probes());time.sleep(5)
        output=REPORTS/f'turn15583_{profile}_seed{seed}_15s.json'
        assert not output.exists()
        with output.with_suffix('.log').open('w') as log:
            child=subprocess.Popen([sys.executable,'isaac/mod4/turn_probe.py','--headless','--checkpoint',str(SOURCE),
                '--steps','1500','--num_envs','96','--seed',str(seed),'--dr-profile',profile,
                '--output',str(output)],cwd=ROOT,stdout=log,stderr=subprocess.STDOUT)
            status('frozen_15s_baseline',seed=seed,profile=profile,evaluation_pid=child.pid,output=str(output))
            while child.poll() is None:
                competing=probes(exclude=child.pid)
                if competing:
                    child.send_signal(signal.SIGINT)
                    try:child.wait(timeout=60)
                    except subprocess.TimeoutExpired:child.kill();child.wait()
                    status('yielded_to_existing_evaluation',output=str(output),existing_probes=competing)
                    sys.exit(0)
                time.sleep(2)
            if child.returncode!=0 or not output.exists():
                status('candidate_program_error',output=str(output),exit_code=child.returncode);sys.exit(1)
        reports[(seed,profile)]=json.loads(output.read_text())
pair_checks={}
passed=True
for seed in (20261003,20261004):
    a,b=reports[(seed,'nominal')],reports[(seed,'white_v1')]
    same_initial=(a['reset_joint_pos_before_physics']==b['reset_joint_pos_before_physics'] and
                  a['reset_root_before_physics']==b['reset_root_before_physics'])
    pair_checks[str(seed)]={'initial_root_q_exactly_equal':same_initial}
    passed &= same_initial
rows=[]
for (seed,profile),r in reports.items():
    # Severe individual failures are retained and veto admission, even if a group mean passes.
    severe=(max(r['per_environment']['peak_tilt'])>15 or not all(r['alive']) or r['nonfinite'])
    accepted=(r['physical_smoke_pass'] and r['turn_skill_pass'] and not severe and
              r['initial_parameter_audit']['actual_parameters_pass'] and r['final_parameter_audit']['actual_parameters_pass'])
    passed &= accepted
    rows.append(dict(seed=seed,profile=profile,accepted=accepted,severe_individual_failure=severe,
                     original_skill_pass=r['turn_skill_pass'],source_checkpoint=r['checkpoint'],
                     file=str(REPORTS/f'turn15583_{profile}_seed{seed}_15s.json')))
receipt=dict(candidate_mature4_low_speed_arcs_multiseed_pass=bool(passed),pairs=pair_checks,reports=rows,
             production_latest_checkpoint_tested=False,not_FPS_world_motion=True,not_spin_translation=True,
             no_new_PPO=True,budget_added=False,
             next_action='If existing low-speed arcs are sufficient, first integrate and verify controls; do not add PPO just because a new course exists. Rebase and check latest production weights before deployment.')
(REPORTS/'TURN_EXISTING_SKILL_BASELINES.json').write_text(json.dumps(receipt,indent=2))
status('frozen_baselines_complete',admission=bool(passed),receipt=str(REPORTS/'TURN_EXISTING_SKILL_BASELINES.json'))
print(json.dumps(receipt),flush=True)
