"""Generate isolated audit subclass from exact original update AST; no imports/SDK/physics."""
from pathlib import Path
import ast,copy,hashlib,json,textwrap
R=Path(__file__).resolve().parent;SRC=R.parent/'mod4v1_lqr_mpc_robust_20261102/sensor_core_jump_v1.py'
D=R/'OBSERVER_AUDIT_V1'
HELPERS='''
from __future__ import annotations
import copy
import sensor_core_jump_v1 as core
from sensor_core_jump_v1 import *

class AuditedStateEstimator(core.StateEstimator):
    def _capture(self,p,dt,first,omega,proper,pivot,candidate,norm,confidence,gravity_innovation,predicted_up,error):
        self.pre_fusion_audit=dict(kind='NEW_FUSION',stamp_s=float(p.time_s),arrival_s=float(p.arrival_s),dt_s=float(dt),first=bool(first),
            gravity_candidate_norm_m_s2=float(norm),gravity_innovation_m_s2=float(gravity_innovation),
            gravity_correction_weight=float(confidence),gyro_body=omega.tolist(),alpha_from_public_gyro=self.alpha.tolist(),
            proper_origin_from_public_imu=proper.tolist(),wheel_accel_proxy_m_s2=float(self.wheel_acc),
            candidate_body_m_s2=candidate.tolist(),predicted_up_body=predicted_up.tolist(),unit_cross_error_body=error.tolist(),
            actual_contact_identity=False,truth_or_DR_parameter_inputs=False)

class ObserverSidecar:
    def __init__(self,original):
        self.audit=AuditedStateEstimator(copy.deepcopy(original.geom),original.offset.copy(),
            accel_correction=original.accel_correction,wheel_std=original.wheel_std,accel_std=original.accel_std,
            accel_reference=original.accel_reference,innovation_limit=original.innovation_limit,upright_prior=original.upright_prior)
        self.calls=0;self.failures=[];self.max_difference=0.;self.last=None;self.fresh=0;self.held=0
        self.weights=[];self.gravity_innovations=[];self.roll_gaps=[];self.kalman_bias=[]
    def observe(self,packet,actual):
        self.calls+=1
        try:
            witness=self.audit.update(packet)
            fields=('state14','roll','omega_body','proper_acc_origin','velocity_variance','measured_wheel_forward2',
                'sensor_age_s','estimated_time_s','slip_innovation','contact_confidence')
            differences={key:float(np.max(np.abs(np.asarray(getattr(actual,key))-np.asarray(getattr(witness,key)))))for key in fields}
            delta=max(differences.values());self.max_difference=max(self.max_difference,delta)
            diag=copy.deepcopy(self.audit.pre_fusion_audit)
            if diag is None:self.held+=1
            else:
                self.fresh+=1;self.weights.append(diag['gravity_correction_weight']);self.gravity_innovations.append(diag['gravity_innovation_m_s2'])
            base=self.audit.last;age=max(0.,float(packet.arrival_s)-float(base.estimated_time_s))
            roll,pitch=float(base.roll),float(base.state14[2]);wx,wy,wz=map(float,base.omega_body)
            roll_rate=wx+math.tan(pitch)*(wy*math.sin(roll)+wz*math.cos(roll))
            roll_gap=age*roll_rate;self.roll_gaps.append(roll_gap);self.kalman_bias.append(float(self.audit.vb[1]))
            self.last=dict(pre_fusion=diag,output_difference_by_field=differences,max_output_difference=delta,
                original_estimate_returned_to_controller=True,shadow_output_returned_to_controller=False,
                sensor_age_s=age,held_roll_to_first_order_arrival_gap_rad=roll_gap,
                first_order_roll_is_diagnostic_not_replacement=True,kalman_accel_bias_state_m_s2=float(self.audit.vb[1]),
                estimated_output_epoch_s=float(actual.estimated_time_s),roll_epoch_is_sensor_stamp=True)
        except Exception as exc:
            self.failures.append(dict(call=self.calls,type=type(exc).__name__,message=str(exc)))
            self.last=dict(observer_error=str(exc),shadow_output_returned_to_controller=False)
        return self.last
    def summary(self):
        def stat(a):return dict(n=len(a),mean=None if not a else float(np.mean(a)),minimum=None if not a else min(a),maximum=None if not a else max(a))
        return dict(calls=self.calls,new_fusion_calls=self.fresh,held_calls=self.held,observer_failures=self.failures,
            maximum_estimate_output_difference=self.max_difference,original_output_identity_preserved=True,sidecar_control_connections=0,
            gravity_correction_weight=stat(self.weights),gravity_weight_exact_zero_count=sum(v==0. for v in self.weights),
            gravity_innovation_m_s2=stat(self.gravity_innovations),first_order_roll_epoch_gap_rad=stat(self.roll_gaps),
            maximum_abs_first_order_roll_gap_rad=None if not self.roll_gaps else max(abs(v)for v in self.roll_gaps),
            kalman_accel_bias_state_m_s2=stat(self.kalman_bias),truth_or_DR_parameter_inputs=False,
            no_extra_model_or_forward_or_physics=True,force_or_hardware_calibration_authority=False)
    def attach(self,estimator):
        old=estimator.update
        def observed(packet):
            actual=old(packet)
            self.observe(packet,actual)
            return actual
        estimator.update=observed
'''
def main():
 if D.exists()or(R/'observer_audit_v1.py').exists():raise RuntimeError('Audit source prefix exists')
 source=SRC.read_text(encoding='utf-8');tree=ast.parse(source)
 cls=next(x for x in tree.body if isinstance(x,ast.ClassDef)and x.name=='StateEstimator')
 original=next(x for x in cls.body if isinstance(x,ast.FunctionDef)and x.name=='update')
 node=copy.deepcopy(original)
 start=ast.parse('self.pre_fusion_audit=None').body[0]
 hook=ast.parse('self._capture(p,dt,first,omega,proper,pivot,gravity_candidate,norm,confidence,innovation,predicted_up,error)').body[0]
 indices=[i for i,x in enumerate(node.body)if isinstance(x,ast.Assign)and isinstance(x.value,ast.Call)and isinstance(x.value.func,ast.Name)and x.value.func.id=='quat_step']
 if len(indices)!=1:raise RuntimeError('Expected one original quaternion fusion assignment')
 node.body.insert(indices[0],hook);node.body.insert(0,start);ast.fix_missing_locations(node)
 stripped=copy.deepcopy(node);stripped.body=[x for x in stripped.body if ast.dump(x)!=ast.dump(start)and ast.dump(x)!=ast.dump(hook)]
 if ast.dump(stripped,include_attributes=False)!=ast.dump(original,include_attributes=False):raise RuntimeError('Original estimator AST changed')
 # Insert generated method inside subclass, before separate sidecar class.
 method=textwrap.indent(ast.unparse(node),'    ')+'\n'
 module=HELPERS.replace('\nclass ObserverSidecar:', '\n'+method+'\nclass ObserverSidecar:',1)
 compile(module,str(R/'observer_audit_v1.py'),'exec')
 D.mkdir(exist_ok=False)
 (R/'observer_audit_v1.py').write_text(module,encoding='utf-8')
 (D/'SOURCE_DERIVATION.json').write_text(json.dumps(dict(source=str(SRC),source_sha256=hashlib.sha256(source.encode()).hexdigest(),
  original_update_AST_equal_after_removing_two_diagnostic_statements=True,original_source_modified=False,
  new_statements=['clear only audit field at call entry','snapshot pre-fusion locals before original quat_step'],
  models=0,forward=0,physics=0,old_raw_reads=0),indent=2),encoding='utf-8')
 print('AUDIT_SOURCE_PREPARED original update AST preserved except two diagnostic statements;no model/physics')
if __name__=='__main__':main()
