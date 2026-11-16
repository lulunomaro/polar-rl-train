"""One counterfactual for causal diagnosis; explicitly NOT native-contract acceptance."""
import json
from pathlib import Path
import native_runtime,run_teacher,native_actuation,play_mod4v3
from native_geometry import Mod4MomentumModel
P=Path(__file__).resolve().parent
play_mod4v3.LEG_DELTA_BOUNDS=(0.,play_mod4v3.LEG_DELTA_BOUNDS[1])
native_actuation.LOW=0.
# The old free-leg hold workspace was computed for the old minimum. The physical
# minimum remains intact, and is sustainable under this diagnostic target range.
Mod4MomentumModel.minimum_static_length=lambda self,theta,pitch:self.minimum_length
case=dict(name='step200_PD_minimum_clean_counterfactual',kind='stair',height=.2,length=.3466,speed=.4,duration=10.,contract_valid=False,diagnostic_only=True,PD_target_delta_min_rad=0.,motor_envelope_unchanged=True)
out=P/'diagnosis_step200/PD_MINIMUM_CLEAN_COUNTERFACTUAL';out.mkdir(exist_ok=False)
d=run_teacher.run(case,out);d['counterfactual_physical_stair_pass']=d['pass_stair'];d['pass_teacher_stair']=False;d['contract_valid']=False;d['count_in_native_acceptance']=False
(out/'RESULT.json').write_text(json.dumps(d,ensure_ascii=False,indent=2)+chr(10),encoding='utf8')
model=json.loads((out/'MODEL_CHECK.json').read_text());model['PD_target_delta_min_rad']=0.;model['counterfactual_only']=True;model['native_contract_valid']=False;(out/'MODEL_CHECK.json').write_text(json.dumps(model,indent=2)+chr(10))
print('DIAGNOSTIC_ONLY_RESULT',d['counterfactual_physical_stair_pass'],d['phase_transitions'])
