"""Experimental stop-only centering gate; no new gains/observer/capture logic.
Uses previous commanded shaper state, NOT true angular velocity or contact.
At a zero operator yaw request, retains an already-active centering target until
previous shaped yaw is exactly zero. Thus release can be one 10ms tick after
the current shaper reaches zero; this label is explicit, not instantaneous sync.
Default off delegates exactly to the frozen legacy implementation.
"""
import math
import numpy as np
from spin_center_torque_v2 import GroundController as Legacy
from spin_base_v1 import GroundController as Base

class GroundController(Legacy):
    def __init__(self,gain,config=None):
        super().__init__(gain,config)
        self.decel_gate=(config or{}).get('center_through_yaw_decel',False)
        assert type(self.decel_gate)is bool

    def command(self,estimate,forward,yaw_rate):
        if not self.decel_gate:return super().command(estimate,forward,yaw_rate)
        # Frozen VelocityCenter equations, with only the active predicate split.
        x=estimate.state14;psi=float(x[1]);cs,sn=math.cos(psi),math.sin(psi);R=np.array([[cs,-sn],[sn,cs]])
        w=estimate.omega_body;pL,_=self.geo.pose(x[3],x[3]+x[4],'left');pR,_=self.geo.pose(x[5],x[5]+x[6],'right')
        pivot=.5*(pL+pR);vy=-float(np.cross(w,pivot)[1]);t=float(estimate.estimated_time_s);dt=0. if self.tprev is None else t-self.tprev
        if not 0<=dt<=.05:return np.zeros(6)
        self.pxy+=dt*(R@np.array([x[7],vy]));pivot_xy=self.pxy+R@pivot[:2]
        previous_shaped_w=float(self.shaper.w)
        requested_active=abs(yaw_rate)>4 and abs(forward)<.1
        retained=bool(self.active_prev and yaw_rate==0. and abs(forward)<.1 and math.isfinite(previous_shaped_w)and previous_shaped_w!=0.)
        active=bool(requested_active or retained)
        if active and not self.active_prev:self.target=pivot_xy.copy()
        correction=0.;error=np.zeros(2)
        if active and self.target is not None:
            error=pivot_xy-self.target;future=psi+x[8]*self.lead;projection=float(error@np.array([math.cos(future),math.sin(future)]))
            correction=float(np.clip(-self.center_kp*projection,-self.cap,self.cap))
        self.center_log=dict(time=t,estimated_root_xy=self.pxy.tolist(),estimated_pivot_xy=pivot_xy.tolist(),target_pivot_xy=None if self.target is None else self.target.tolist(),
            error_xy=error.tolist(),no_side_slip_vy=vy,operator_v=float(forward),centering_v=correction,applied_v=float(forward+correction),active=active,lead_s=self.lead,assumption='lateralnoslipproxy_notmeasurement')
        self.tprev=t;self.active_prev=active;self.internal_v_offset=correction
        # Do NOT feed a fake nonzero yaw request to the base controller: its
        # original stop shaper/yaw PI still receives the actual zero request.
        tau=Base.command(self,estimate,forward,yaw_rate);corr=0.;x=estimate.state14
        if self.center_log.get('active',False):
            err=np.asarray(self.center_log['error_xy']);psi=x[1]+x[8]*self.lead
            corr=float(np.clip(-self.kt*(err@np.array([math.cos(psi),math.sin(psi)])),-self.tcap,self.tcap))
            diff=.5*(tau[5]-tau[2]);bound=max(0.,5.775909774436091-abs(diff))
            common=float(np.clip(.5*(tau[2]+tau[5])+corr,-bound,bound));tau[2]=common-diff;tau[5]=common+diff
        self.center_log['centering_torque_Nm']=corr;self.center_log['internal_action']='commonwheeltorque_notvelocityreference';self.previous=tau.copy()
        self.center_log.update(decel_gate_enabled=True,gate_requested_active=bool(requested_active),gate_retained_from_previous_active=retained,
            gate_previous_shaped_w_rad_s=previous_shaped_w,gate_current_shaped_w_rad_s=float(self.shaper.w),
            gate_release_is_previous_shaper_not_measured_spin=True)
        return tau
