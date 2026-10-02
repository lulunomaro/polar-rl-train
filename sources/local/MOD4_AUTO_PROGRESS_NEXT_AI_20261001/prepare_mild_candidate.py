"""Prepare isolated code only. Does NOT pause or launch production."""
from pathlib import Path
import ast
import hashlib
import json
import shutil
import time

SOURCE=Path('/home/egde/rl_candidates/MOD4_native_floor_continue10h_20260930')
ROOT=Path('/home/egde/rl_candidates/MOD4_mild_dr_trial_20261001')
HERE=Path(__file__).resolve().parent
EXPECTED='24091dc31a157322d81c7e259934a2ba57b4efb461a1e2ad711134aab387e3c0'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(SOURCE/'isaac/mod4/mod4_task.py')==EXPECTED
if (ROOT/'PREPARED.json').exists():
    print((ROOT/'PREPARED.json').read_text())
    raise SystemExit(0)
ROOT.mkdir(exist_ok=True)
for name in ('isaac','train','cad'):
    if not (ROOT/name).exists():shutil.copytree(SOURCE/name,ROOT/name,symlinks=True)
for name in ('incoming','scripts'):
    if (SOURCE/name).exists() and not (ROOT/name).exists():
        (ROOT/name).symlink_to(SOURCE/name,target_is_directory=True)
code=ROOT/'isaac/mod4'
shutil.copy2(HERE/'mild_dr.py',code/'mild_dr.py')
path=code/'mod4_task.py'
text=path.read_text()
old='''        scaled = super()._clip_effort(effort) * self.episode_scale * self.step_scale
        return scaled'''
new='''        scaled = super()._clip_effort(effort) * self.episode_scale * self.step_scale
        if os.environ.get("RM_MILD_DR_PROFILE", "") == "white_v1":
            # Vary unsaturated output gain while preserving the actual torque-speed envelope.
            return super()._clip_effort(scaled)
        return scaled'''
assert text.count(old)==1
text=text.replace(old,new)
anchor='''                                    enable_external_forces_every_iteration=True)'''
assert text.count(anchor)==1
text=text.replace(anchor,anchor+'''
        from mild_dr import configure
        configure(self)''')
text=text.replace('''        "dr_off": DR_OFF,''','''        "dr_off": DR_OFF,
        "dr_profile": os.environ.get("RM_MILD_DR_PROFILE", "nominal"),''')
ast.parse(text)
path.write_text(text,encoding='utf8')
cfg=json.loads((code/'env.json').read_text())
cfg['RM_MILD_DR_PROFILE']='white_v1'
(code/'env.json').write_text(json.dumps(cfg,indent=2))
for name in ['mild_dr.py','mod4_task.py']:ast.parse((code/name).read_text())
manifest={'root':str(ROOT),'source':str(SOURCE),'prepared_epoch':time.time(),
    'source_task_sha256':EXPECTED,'sha256':{name:sha(code/name) for name in ['mod4_task.py','mild_dr.py','env.json']},
    'training_started':False,'budget_owner':str(SOURCE/'TRAINING_BUDGET_10H.json'),
    'scope':'candidate for parameter readback and paired evaluation only; no production handover yet'}
(ROOT/'PREPARED.json').write_text(json.dumps(manifest,indent=2))
print(json.dumps(manifest))
