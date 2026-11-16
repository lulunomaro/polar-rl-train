"""One declared causal probe: Cartesian VMC with native LQR yaw only.
Canonical controller files remain untouched. No direct torque backend or bound changes.
"""
from pathlib import Path
import sys,json,hashlib,os
P=Path(__file__).resolve().parent;E=P.parent;sys.path.insert(0,str(E))
import run_teacher
import controller as native_controller
original_class=run_teacher.NativeTeacher;original_gain=native_controller.get_K
current=[]
class ProbeTeacher(original_class):
 def __init__(self,*a,**kw):
  super().__init__(*a,**kw);current.append(self.controller)
def gain_without_extra_cartesian_pitch(a,b):
 K=original_gain(a,b)
 if current and current[0].step_climb.phase in ('lift','swing','plant'):
  K=K.copy();K[:,[2,7]]=0.
 return K
native_controller.get_K=gain_without_extra_cartesian_pitch;run_teacher.NativeTeacher=ProbeTeacher
case=dict(name='native_yaw_only_cartesian_probe',kind='stair',height=.2,start_x=0.,length=.3466,speed=.47,duration=10.,diagnostic_only=True,cartesian_lqr_pitch=False,cartesian_lqr_yaw=True)
out=P/case['name'];out.mkdir(exist_ok=False)
files=[E/'sim/controller.py',E/'sim/step_climb.py',E/'native_runtime.py',E/'native_contacts.py',E/'native_actuation.py',E/'native_full_mjcf_gains.npz',Path(__file__)]
(out/'PROBE_PROVENANCE.json').write_text(json.dumps(dict(method='In-process diagnostic gain view clears pitch/rate columns only during Cartesian phases; normal and capture LQR remain exact baseline',source_sha256={str(f):hashlib.sha256(f.read_bytes()).hexdigest()for f in files},default_controller_files_unchanged=True),indent=2)+'\n',encoding='utf8')
run_teacher.run(case,out)
