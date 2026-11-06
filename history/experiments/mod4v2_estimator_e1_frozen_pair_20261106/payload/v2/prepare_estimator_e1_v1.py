"""First separately named observer-module candidate; old torque M1..M3 remain frozen.
Generate only one innovation-weight replacement, then new software test and frozen pair.
"""
from pathlib import Path
import ast,copy,hashlib,json,textwrap
R=Path(__file__).resolve().parent;D=R/'ESTIMATOR_CAUCHY_E1_V1'
HEADER='''from __future__ import annotations
import copy,math
from sensor_core_jump_v1 import *
from observer_audit_v1 import AuditedStateEstimator,ObserverSidecar

def cauchy_innovation_weight(innovation,limit):
    if not math.isfinite(innovation)or not math.isfinite(limit):raise ValueError('Nonfinite innovation scale')
    if limit<=0.:return 1. # preserve explicit disabled-innovation-gate convention
    inverse=1./math.hypot(1.,float(innovation)/float(limit))
    return inverse*inverse

class CauchyEstimatorE1(AuditedStateEstimator):
'''
TAIL='''
class MatchingE1Sidecar(ObserverSidecar):
    def __init__(self,original):
        super().__init__(original)
        self.audit=CauchyEstimatorE1(copy.deepcopy(original.geom),original.offset.copy(),accel_correction=original.accel_correction,
            wheel_std=original.wheel_std,accel_std=original.accel_std,accel_reference=original.accel_reference,
            innovation_limit=original.innovation_limit,upright_prior=original.upright_prior)
    def summary(self):
        s=super().summary();s['witness_reference_variant']='E1 not original-baseline';s['not_baseline_equivalence_claim']=True
        return s
'''
def main():
 if D.exists()or(R/'estimator_cauchy_e1.py').exists():raise RuntimeError('New E1 prefix exists,no repeated generation')
 source=(R/'observer_audit_v1.py').read_text(encoding='utf-8');tree=ast.parse(source)
 cls=next(n for n in tree.body if isinstance(n,ast.ClassDef)and n.name=='AuditedStateEstimator')
 old=next(n for n in cls.body if isinstance(n,ast.FunctionDef)and n.name=='update');new=copy.deepcopy(old)
 targets=[n for n in ast.walk(new)if isinstance(n,ast.AugAssign)and isinstance(n.target,ast.Name)and n.target.id=='confidence']
 if len(targets)!=1:raise RuntimeError('Expected exactly one original innovation multiplier')
 prior=copy.deepcopy(targets[0].value);targets[0].value=ast.parse('cauchy_innovation_weight(innovation,self.innovation_limit)',mode='eval').body
 restored=copy.deepcopy(new)
 target2=next(n for n in ast.walk(restored)if isinstance(n,ast.AugAssign)and isinstance(n.target,ast.Name)and n.target.id=='confidence');target2.value=prior
 if ast.dump(old,include_attributes=False)!=ast.dump(restored,include_attributes=False):raise RuntimeError('Unintended observer algorithm change')
 ast.fix_missing_locations(new);module=HEADER+textwrap.indent(ast.unparse(new),'    ')+'\n'+TAIL
 compile(module,str(R/'estimator_cauchy_e1.py'),'exec')
 D.mkdir(exist_ok=False);(R/'estimator_cauchy_e1.py').write_text(module,encoding='utf-8')
 (D/'SOURCE_DERIVATION.json').write_text(json.dumps(dict(stage='first observation-module repair E1,max3;not reopening old torque3of3',
  source=str(R/'observer_audit_v1.py'),source_sha256=hashlib.sha256(source.encode()).hexdigest(),single_innovation_multiplier_replacement=True,
  old='max(0,1-innovation/limit) if limit>0 else1',new='1/(1+(innovation/limit)^2) if limit>0 else1',
  original_norm_gate_and_accel_gain_and_other_estimator_math_unchanged=True,existing_innovation_limit_reused_no_grid=True,
  explicit_nonfinite_scale_guard=True,shared_sources_modified=False,new_extra_observer_K_or_torque_gain=False,
  observer_feedback_will_change_system=True,not_diagnostic_only=True,models=0,physics=0,old_raw_or_QA=0),indent=2),encoding='utf-8')
 print('E1_SOURCE_READY one observer innovation multiplier;system feedback changes;old torque3of3 frozen;0 model/physics')
if __name__=='__main__':main()
