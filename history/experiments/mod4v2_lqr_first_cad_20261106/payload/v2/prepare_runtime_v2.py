"""One-time source adaptation of existing controllers, DR and actuator loop.
No physics/old QA. Numerical gains are supplied by fresh v2 synthesis, not copied.
"""
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parent
V1=ROOT.parent/'mod4v1_lqr_mpc_robust_20261102'
OLD=ROOT.parent/'traditional_control_20261101'

def source(path):return Path(path).read_text(encoding='utf-8')
def replace(text,a,b,count=1):
 if text.count(a)!=count:raise ValueError('Source shape changed: '+a)
 return text.replace(a,b)

files={}
dr=source(OLD/'dr_components.py').split('\ndef _self_test():')[0]
dr=replace(dr,'.2206394410901294','.1706394410901294')
dr=dr.replace('400 N','300 N').replace('400N','300N').replace('nominal400','nominal300')
dr=dr.replace('[-1.0843, .85]','MOD4v2 mechanical branch (caller projection)')
dr=dr.replace('mod4.mujoco300N.full_D0_D7.v1','mod4v2.mujoco300N.full_D0_D7.v2')
files['dr_v2.py']='# Derived from traditional_control_20261101/dr_components.py; runtime part only.\n# Only gas reference guard/schema labels changed to HW300N60; RNG/delays/PD unchanged.\n'+dr
base=source(V1/'FLAT_STABILITY_FIX_V1/controller.py')
base=replace(base,'.06369999796152115','.0625')
base=base.replace("All numeric K, trim, actuator bounds and plant remain MOD4v1's own frozen P25.","Fresh MOD4v2 dynamics/trim/K; same existing controller structure and public bounds.")
files['controller_base_v2.py']=base
coord=source(V1/'FLAT_STABILITY_FIX_V1/controller_v2.py')
coord=replace(coord,'from FLAT_STABILITY_FIX_V1.controller import GroundController as First','from controller_base_v2 import GroundController as First')
files['controller_coord_v2.py']=coord
roll=source(V1/'RM_ROBUSTNESS_V1/controller_roll_follow_v1.py')
roll=replace(roll,'from FLAT_STABILITY_FIX_V1.controller_v2 import GroundController as Base','from controller_coord_v2 import GroundController as Base')
roll=replace(roll,'if np.max(np.abs(q)) > 2.9 or not -1.05 <= q[1]-q[0] <= .82:','if not -1.0863195404360622 <= q[1]-q[0] <= .49192233306644084:')
files['controller_roll_v2.py']='# v2: continuous active coordinates; physical relative branch replaces v1 operational caps.\n'+roll
heading=source(V1/'RM_ROBUSTNESS_V1/controller_heading_follow_v2.py')
heading=replace(heading,'from RM_ROBUSTNESS_V1.controller_roll_follow_v1 import GroundController as C1','from controller_roll_v2 import GroundController as C1')
heading=replace(heading,"VARIANT = 'coord_soft_roll_follow_heading_v2'","VARIANT = 'coord_soft_MOD4v2_fresh_LQR_heading'")
files['controller_heading_v2.py']=heading
for name in files:
 if (ROOT/name).exists():raise FileExistsError(name)
for name,text in files.items():(ROOT/name).write_text(text,encoding='utf-8')
with (ROOT/'RUNTIME_REUSE_MAP.json').open('x',encoding='utf-8') as f:
 json.dump(dict(source_root=str(V1),source_DR=str(OLD/'dr_components.py'),new_files=list(files),
  source_code_reused=True,old_gains_copied=False,physics_steps=0,
  changes=['300N springref guard .1706394410901294; same distributions/queues',
  'wheel envelope radius .0625 matching actual P0 cylinder',
  'new relative mechanical bounds; no old +/-2.9 active reference cap',
  'private imports only; no v1 file modified']),f,indent=2)
print('V2_RUNTIME_FILES_WRITTEN '+','.join(files),flush=True)
