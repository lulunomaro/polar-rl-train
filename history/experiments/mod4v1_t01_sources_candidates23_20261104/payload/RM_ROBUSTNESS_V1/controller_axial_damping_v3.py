"""C3: source-derived leg-length D-on-measurement through own public Jacobians.

SPR2 chassis_task.c:898-973 separates axial leg-length force from LQR angular
balance; chassis_task.h:33-35 sets a separate length PID. Retain our common
P25 balance/C1 references/C2 heading and add only the missing radial damping.
No foreign dimensions, K, force signs, gravity/gas feedforward or gains copied.
"""
import math
import numpy as np
from RM_ROBUSTNESS_V1.controller_heading_follow_v2 import GroundController as C2

VARIANT = 'coord_soft_roll_follow_heading_axial_damping_v3'
NOMINAL_MASS_KG = 14.294140288606286  # fixed public MOD4 design, never sampled DR


class GroundController(C2):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.mode = VARIANT
        r, J = self._fk(self.q0, 'left')
        g = (r[[0,2]]@J[[0,2],:])/float(np.linalg.norm(r[[0,2]]))
        g2 = float(g@g)
        self.radial_K = self.leg_kp/g2
        self.radial_D_existing = self.leg_kd/g2
        # Nominal half-mass is an explicit design approximation, not measured load.
        self.radial_D_target = 2.*.8*math.sqrt(.5*NOMINAL_MASS_KG*self.radial_K)
        self.radial_D_add = max(0., self.radial_D_target-self.radial_D_existing)
        self.radial_force_cap = .5*NOMINAL_MASS_KG*9.81
        self.axial_diag = dict(calls=0, headroom_limited_calls=0,
            added_damping_Ns_m=self.radial_D_add,
            design_effective_stiffness_N_m=self.radial_K,
            design_existing_damping_Ns_m=self.radial_D_existing,
            design_total_damping_target_Ns_m=self.radial_D_target,
            target_damping_ratio=.8, nominal_half_mass_approximation=True,
            max_abs_damping_force_N=0., max_abs_requested_leg_addition_Nm=0.,
            extra_truth_inputs=False, sampled_sensor_power_not_physical_passivity_proof=True)

    def command(self, e, forward, yaw_rate):
        tau = super().command(e, forward, yaw_rate)
        if not self.valid_command:
            return tau
        x = np.asarray(e.state14, float)
        delta = np.zeros(6); rates = np.zeros(6)
        length_rates, forces = [], []
        for side, qi, di, motors in (('left',3,10,[0,1]), ('right',5,12,[3,4])):
            q = np.array([x[qi],x[qi]+x[qi+1]])
            qd = np.array([x[di],x[di]+x[di+1]])
            r, J = self._fk(q, side)
            length = float(np.linalg.norm(r[[0,2]]))
            if length < .05:
                raise ValueError('AXIAL_DAMPING_LENGTH_DOMAIN')
            g = (r[[0,2]]@J[[0,2],:])/length
            ld = float(g@qd)
            force = float(np.clip(-self.radial_D_add*ld,
                                  -self.radial_force_cap,self.radial_force_cap))
            delta[motors] = g*force
            rates[motors] = qd
            length_rates.append(ld); forces.append(force)
        # One nonnegative scale preserves the sensor-domain dissipative direction.
        alpha = 1.
        for i in (0,1,3,4):
            if delta[i] != 0.:
                room = self.effort[i]-math.copysign(1.,delta[i])*tau[i]
                alpha = min(alpha,max(0.,float(room/abs(delta[i]))))
        tau += alpha*delta
        self.previous = tau.copy()
        d = self.axial_diag
        d['calls'] += 1; d['headroom_limited_calls'] += int(alpha < 1.)
        d['max_abs_damping_force_N'] = max(d['max_abs_damping_force_N'],max(map(abs,forces)))
        d['max_abs_requested_leg_addition_Nm'] = max(d['max_abs_requested_leg_addition_Nm'],float(np.max(np.abs(alpha*delta))))
        self.control_diagnostic['axial_damping'] = dict(
            added_damping_Ns_m=self.radial_D_add, measured_length_rates_m_s=length_rates,
            damping_force_before_headroom_N=forces, common_headroom_scale=alpha,
            delta_tau6_Nm=alpha*delta, sampled_sensor_power_W=float(alpha*delta@rates))
        return tau
