"""M3: retain FULL nominal reference-static bias, including its common component.
Only M2's joint-common deletion is removed. No gain/PD/shaper/driver modification.
Fixed nominal model feedforward, NOT force feedback/full dynamic compensation.
"""
import math,time
import numpy as np
from controller_heading_v2 import GroundController as Base
from REFERENCE_STATIC_FF_DESIGN_V1.static_ff import NominalStaticReferenceFF

VARIANT='coord_soft_MOD4v2_reference_full_static_ff_v1'

class GroundController(Base):
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self.mode=VARIANT
        self.reference_ff=NominalStaticReferenceFF()
        self.reference_ff_design=dict(self.reference_ff.base_design,
            scope='M3 fixed nominal full static change at smooth C1 REFERENCE;not dynamic inverse/force feedback',
            differential_joint_torque_only=False,common_model_feedforward_retained=True,
            original_common_LQR_feedback_and_PD_retained=True,
            reference_proper_design_m_s2=[0.,0.,9.81],reference_rates_accelerations_assumed_zero=True,
            force_feedback_or_truth_or_episode_parameters=False,gas_curve_and_damping_not_measured=True,
            contact_identity_confirmed=False,force_input_ready=False,original_actuation_order_unchanged=True)
        self.reference_ff_diag={}
        self.reference_ff_aggregate=dict(calls=0,headroom_scaled_calls=0,min_scale=1.,
            raw_reference_static_delta_peak4_Nm=[0.]*4,projected_extra_peak6_Nm=[0.]*6,
            retained_reference_common_peak2_Nm=[0.,0.],max_added_joint_common_sum_abs_Nm=0.,
            full_reference_mapping_max_abs_error_Nm=0.,controller_uses_force_proxy=False,
            physical_force_zero_sum_claimed=False,common_component_deleted=False,
            nominal_reference_eval_total_wall_ms=0.,nominal_reference_eval_max_wall_ms=0.,hardware_WCET_qualified=False)

    def command(self,e,forward,yaw_rate):
        tau=super().command(e,forward,yaw_rate)
        if not self.valid_command:return tau
        qr=np.array([self.ref[3],self.ref[3]+self.ref[4],self.ref[5],self.ref[5]+self.ref[6]],float)
        started=time.perf_counter_ns()
        correction=np.asarray(self.reference_ff.correction(qr),float)
        eval_ms=(time.perf_counter_ns()-started)*1e-6
        if correction.shape!=(4,)or not np.isfinite(correction).all():
            raise ValueError('REFERENCE_FULL_STATIC_FF_NONFINITE_OR_SHAPE')
        common=.5*(correction[:2]+correction[2:])
        # Full reference equilibrium change. M2 discarded `common` here, even
        # though unequal left/right geometry makes joint-zero-sum != force balance.
        extra=np.zeros(6);extra[[0,1,3,4]]=correction
        scale=1.
        for i in (0,1,3,4):
            if abs(extra[i])>1e-12:
                room=float(self.effort[i]-math.copysign(1.,extra[i])*tau[i])
                scale=min(scale,max(0.,room/abs(float(extra[i]))))
        applied=scale*extra;out=tau+applied
        if not np.isfinite(out).all()or np.any(np.abs(out)>self.effort+1e-8):
            raise ValueError('REFERENCE_FULL_STATIC_FF_OUTPUT_BOUNDS')
        self.previous=out.copy()
        mapping_error=float(np.max(np.abs(applied[[0,1,3,4]]-scale*correction)))
        self.reference_ff_diag=dict(reference_q4_abs=qr.tolist(),nominal_static_delta4_Nm=correction.tolist(),
            retained_common_component2_Nm=common.tolist(),common_removed=False,scale=scale,
            extra_joint_tau6_Nm=applied.tolist(),model_role='full quasistatic reference design;not measured contact force',truth_inputs=False)
        a=self.reference_ff_aggregate;a['calls']+=1;a['headroom_scaled_calls']+=int(scale<1.-1e-12)
        a['min_scale']=min(a['min_scale'],scale)
        a['nominal_reference_eval_total_wall_ms']+=eval_ms
        a['nominal_reference_eval_max_wall_ms']=max(a['nominal_reference_eval_max_wall_ms'],eval_ms)
        for j in range(4):a['raw_reference_static_delta_peak4_Nm'][j]=max(a['raw_reference_static_delta_peak4_Nm'][j],abs(float(correction[j])))
        for j in range(6):a['projected_extra_peak6_Nm'][j]=max(a['projected_extra_peak6_Nm'][j],abs(float(applied[j])))
        for j in range(2):a['retained_reference_common_peak2_Nm'][j]=max(a['retained_reference_common_peak2_Nm'][j],abs(float(common[j])))
        a['max_added_joint_common_sum_abs_Nm']=max(a['max_added_joint_common_sum_abs_Nm'],abs(float(applied[0]+applied[3])),abs(float(applied[1]+applied[4])))
        a['full_reference_mapping_max_abs_error_Nm']=max(a['full_reference_mapping_max_abs_error_Nm'],mapping_error)
        return out
