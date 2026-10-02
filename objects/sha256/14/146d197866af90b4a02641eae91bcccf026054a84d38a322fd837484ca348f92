"""Run on Ubuntu once transferred beside the two new supervision/probe files.

Prepare the new workspace only. Launch supervision separately after deployment.
The old task, assets and policies are immutable. No credentials are stored.
"""
from pathlib import Path
import ast
import hashlib
import json
import os
import shutil
import subprocess
import time

SOURCE=Path('/home/egde/rl_candidates/MOD4_contact_integrated_repair_20260930')
ROOT=Path('/home/egde/rl_candidates/MOD4_native_floor_continue10h_20260930')
FIX=Path('/home/egde/rl_candidates/MOD4_NATIVE_FLOOR_FIX_NEXT_AI_20260930')
EXPECTED='af03769591164a48b478ad5635c864069541c04789ff359786215f1e1b6c914f'
HERE=Path(__file__).resolve().parent

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()

assert SOURCE.resolve()!=ROOT.resolve() and ROOT.parent==SOURCE.parent
assert (ROOT/'TRAINING_BUDGET_10H.json').is_file(), 'Register the explicit budget first'
budget=json.loads((ROOT/'TRAINING_BUDGET_10H.json').read_text())
assert budget['authorized_training_seconds']==36000 and not budget.get('active_segment')
assert sha(SOURCE/'isaac/mod4/mod4_task.py')==EXPECTED, 'source changed since audit'
for proc in Path('/proc').glob('[0-9]*/cmdline'):
    try:
        argv=proc.read_bytes().split(b'\0')
        if any(x.endswith(b'/train_mod4_ppo.py') for x in argv):
            raise RuntimeError('Existing trainer; refuse deployment or double start')
    except OSError:pass
if (ROOT/'status.json').exists():
    state=json.loads((ROOT/'status.json').read_text())
    for k in ['training_pid','supervisor_pid','validation_pid','evaluation_pid']:
        if state.get(k) and Path(f"/proc/{state[k]}/cmdline").exists():
            raise RuntimeError('new task already running; do not rerun bootstrap')
for name in ['isaac','train','cad','scripts','incoming']:
    if not (ROOT/name).exists():shutil.copytree(SOURCE/name,ROOT/name,symlinks=True)
code=ROOT/'isaac/mod4'
manifest=ROOT/'NATIVE_FLOOR_PATCH_MANIFEST.json'
if not manifest.exists():
    subprocess.run(['/usr/bin/python3',str(FIX/'apply_native_floor_fix.py'),'--task-root',str(ROOT)],check=True)
for name in ['supervise_native_floor.py','native_floor_20k_probe.py']:
    target=code/name
    if target.exists():assert sha(target)==sha(HERE/name), 'refuse revision drift'
    else:shutil.copy2(HERE/name,target)
    ast.parse(target.read_text())
# Monitor code is a separate copy. Existing trainer/task remains untouched.
tui=code/'tui_rescue.py'
if (HERE/'tui_rescue.py').exists():
    assert sha(tui) in [sha(SOURCE/'isaac/mod4/tui_rescue.py'),sha(HERE/'tui_rescue.py')], 'unexpected target monitor revision'
    shutil.copy2(HERE/'tui_rescue.py',tui)
text=tui.read_text()
text=text.replace('接触冲量采样修复','原生平面修复 · 10小时续训')
text=text.replace('LogMonitor(str(log), 4350, 20000, 24)','LogMonitor(str(log), int(state.get("target_iteration") or 100000), 20000, 24)')
ast.parse(text);tui.write_text(text,encoding='utf8',newline='\n')
cfg=json.loads((code/'env.json').read_text())
original=json.loads((SOURCE/'isaac/mod4/env.json').read_text())
diff={k:{'before':original.get(k),'after':cfg.get(k)} for k in set(cfg)|set(original) if cfg.get(k)!=original.get(k)}
assert diff=={'RM_FLAT_NATIVE_PLANE':{'before':None,'after':'1'}}, diff
unchanged=['mod4_env.py','contact_capture.py','validate_speed.py','train_mod4_ppo.py','rescue_training.py']
for name in unchanged:assert sha(code/name)==sha(SOURCE/'isaac/mod4'/name),name
receipt={'root':str(ROOT),'source':str(SOURCE),'prepared_at_epoch':time.time(),
    'environment_changes':diff,'sha256':{name:sha(code/name) for name in unchanged+['mod4_task.py','ground_plane_candidate.py','supervise_native_floor.py','native_floor_20k_probe.py']},
    'external_robot_usd':cfg['RM_MOD4_USD'],'training_started':False,
    'source_checkpoint':budget['checkpoint'],'source_checkpoint_sha256':budget['checkpoint_sha256']}
(ROOT/'DEPLOYMENT_RECEIPT.json').write_text(json.dumps(receipt,indent=2))
state={'stage':'prepared','updated_at':time.time(),'authorized_training_seconds':36000,
       'num_envs':20000,'steps_per_env':24,'ground':'native Z-plane at z=0','speed_limit_m_s':1.5,
       'resume_checkpoint':budget['checkpoint'],'latest_checkpoint':budget['checkpoint'],
       'iteration':8648,'training_pid':None,'active_log':str(ROOT/'supervisor_native_floor.log')}
(ROOT/'status.json').write_text(json.dumps(state,indent=2))
print(json.dumps(receipt,indent=2))
