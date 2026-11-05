"""M2 candidate: nominal quasistatic DIFFERENTIAL reference feedforward.
Not force feedback: no ContactProxy/alpha/current output torque/contact/DR inputs.
The independent design helper must be delivered/reviewed before any physical run.
"""
import math,time
import numpy as np
from controller_heading_v2 import GroundController as Base
from REFERENCE_STATIC_FF_DESIGN_V1.static_ff import NominalStaticReferenceFF

VARIANT='coord_soft_MOD4v2_reference_static_ff_v1'

class GroundController(Base):
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self.mode=VARIANT
        self.reference_ff=NominalStaticReferenceFF()
        self.reference_ff_design=dict(self.reference_ff.base_design,
            scope='fixed public nominal model at smooth C1 REFERENCE,not instantaneous inverse dynamics',
            differential_joint_torque_only=True,original_common_LQR_and_PD_retained=True,
            reference_proper_design_m_s2=[0.,0.,9.81],reference_rates_accelerations_assumed_zero=True,
            force_feedback_or_truth_or_episode_parameters=False,
            gas_curve_and_damping_not_measured=True,contact_identity_confirmed=False,
            force_input_ready=False,original_actuation_order_unchanged=True)
        self.reference_ff_diag={}
        self.reference_ff_aggregate=dict(calls=0,headroom_scaled_calls=0,min_scale=1.,
            raw_reference_static_delta_peak4_Nm=[0.]*4,projected_extra_peak6_Nm=[0.]*6,
            max_removed_common_component2_Nm=[0.,0.],max_added_joint_common_residual_Nm=0.,
            controller_uses_force_proxy=False,physical_force_zero_sum_claimed=False,
            nominal_reference_eval_total_wall_ms=0.,nominal_reference_eval_max_wall_ms=0.,hardware_WCET_qualified=False)

    def command(self,e,forward,yaw_rate):
        tau=super().command(e,forward,yaw_rate)
        if not self.valid_command:return tau
        # Reference q is filtered/slew-bounded by existing C1,not measured q/qdd.
        qr=np.array([self.ref[3],self.ref[3]+self.ref[4],self.ref[5],self.ref[5]+self.ref[6]],float)
        started=time.perf_counter_ns()
        correction=np.asarray(self.reference_ff.correction(qr),float)
        eval_ms=(time.perf_counter_ns()-started)*1e-6
        if correction.shape!=(4,)or not np.isfinite(correction).all():
            raise ValueError('REFERENCE_STATIC_FF_NONFINITE_OR_SHAPE')
        common=.5*(correction[:2]+correction[2:]);diff=.5*(correction[:2]-correction[2:])
        extra=np.zeros(6);extra[[0,1]]=diff;extra[[3,4]]=-diff
        # Preserve JOINT common sagittal torque. Unequal left/right Jacobians mean
        # this is NOT a claim of zero summed Cartesian force/physical moment.
        scale=1.
        for i in (0,1,3,4):
            if abs(extra[i])>1e-12:
                room=float(self.effort[i]-math.copysign(1.,extra[i])*tau[i])
                scale=min(scale,max(0.,room/abs(float(extra[i]))))
        applied=scale*extra;out=tau+applied
        if not np.isfinite(out).all()or np.any(np.abs(out)>self.effort+1e-8):
            raise ValueError('REFERENCE_STATIC_FF_OUTPUT_BOUNDS')
        self.previous=out.copy()
        self.reference_ff_diag=dict(reference_q4_abs=qr.tolist(),nominal_static_delta4_Nm=correction.tolist(),
            removed_common_component2_Nm=common.tolist(),scale=scale,extra_joint_tau6_Nm=applied.tolist(),
            model_role='quasistatic reference-only design;not measured contact force',truth_inputs=False)
        a=self.reference_ff_aggregate;a['calls']+=1;a['headroom_scaled_calls']+=int(scale<1.-1e-12)
        a['min_scale']=min(a['min_scale'],scale)
        a['nominal_reference_eval_total_wall_ms']+=eval_ms
        a['nominal_reference_eval_max_wall_ms']=max(a['nominal_reference_eval_max_wall_ms'],eval_ms)
        for j in range(4):a['raw_reference_static_delta_peak4_Nm'][j]=max(a['raw_reference_static_delta_peak4_Nm'][j],abs(float(correction[j])))
        for j in range(6):a['projected_extra_peak6_Nm'][j]=max(a['projected_extra_peak6_Nm'][j],abs(float(applied[j])))
        for j in range(2):a['max_removed_common_component2_Nm'][j]=max(a['max_removed_common_component2_Nm'][j],abs(float(common[j])))
        a['max_added_joint_common_residual_Nm']=max(a['max_added_joint_common_residual_Nm'],abs(float(applied[0]+applied[3])),abs(float(applied[1]+applied[4])))
        return out
