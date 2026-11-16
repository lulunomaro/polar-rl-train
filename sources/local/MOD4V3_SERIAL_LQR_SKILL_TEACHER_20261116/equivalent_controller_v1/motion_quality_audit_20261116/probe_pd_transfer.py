"""Diagnostic only: same native controller, clocks, model and motor envelope;
remove the policy PD target transfer to test its effect. Not student/teacher acceptance.
"""
from pathlib import Path
import sys,json,hashlib
P=Path(__file__).resolve().parent;E=P.parent;sys.path.insert(0,str(E));import run_teacher
case=dict(name='native_direct_torque_counterfactual',kind='stair',height=.2,start_x=0.,length=.3466,speed=.47,duration=10.,actuation='direct_torque',diagnostic_only=True,valid_native_policy_contract=False)
out=P/case['name'];out.mkdir(exist_ok=False)
(out/'PROBE_PROVENANCE.json').write_text(json.dumps(dict(method='Direct motor torque diagnostic; original envelopes and clock preserved; native policy PD target bounds/action transfer bypassed, so never an accepted teacher/student score',source_sha256={str(E/f):hashlib.sha256((E/f).read_bytes()).hexdigest()for f in ['sim/controller.py','sim/step_climb.py','native_runtime.py','native_contacts.py','native_actuation.py','native_full_mjcf_gains.npz']},wrapper_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()),indent=2)+'\n',encoding='utf8')
run_teacher.run(case,out)
