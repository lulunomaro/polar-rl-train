
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

    def update(self, p: SensorPacket):
        self.pre_fusion_audit = None
        p.validate()
        stamp = float(p.time_s)
        if self.prev_stamp is not None and stamp <= self.prev_stamp + 1e-10:
            if abs(stamp - self.prev_stamp) < 1e-09 and self.last is not None:
                return self._predict_view(self.last, p.arrival_s)
            raise ValueError('Out-of-order sensor packet')
        first = self.prev_stamp is None
        dt = 0.0 if first else stamp - self.prev_stamp
        if not first and (not 0.0 < dt <= 0.1):
            raise ValueError('Sensor timeout')
        omega = np.asarray(p.gyro_body, float)
        if self.prev_omega is not None:
            self.alpha += dt / (0.06 + dt) * ((omega - self.prev_omega) / dt - self.alpha)
        proper = compensate_lever_arm(p.accel_proper_body, omega, self.alpha, self.offset)
        if self.q is None:
            unit = proper / max(float(np.linalg.norm(proper)), 1e-09)
            roll = math.atan2(unit[1], unit[2])
            pitch = math.atan2(-unit[0], math.hypot(unit[1], unit[2]))
            if self.upright_prior or abs(float(np.linalg.norm(proper)) - G) > 0.3 * G:
                roll = pitch = 0.0
            self.q = quat_from_rpy(roll, pitch, 0.0)
            self.last_yaw_wrapped = 0.0
        wheel = []
        positions = []
        for j, side in enumerate(('left', 'right')):
            v, position, _, _ = self.geom.wheel_kinematics(p.joint_pos4[2 * j], p.joint_pos4[2 * j + 1], p.joint_vel4[2 * j], p.joint_vel4[2 * j + 1], p.wheel_vel2[j], omega, side)
            wheel.append(v)
            positions.append(position)
        wheel = np.asarray(wheel)
        wheel_mean = float(np.mean(wheel))
        raw_acc = 0.0 if first else (wheel_mean - self.prev_wheel) / dt
        self.wheel_acc += dt / (0.12 + dt) * (np.clip(raw_acc, -8, 8) - self.wheel_acc)
        pivot = np.mean(positions, axis=0)
        pivot_rotation = np.cross(self.alpha, pivot) + np.cross(omega, np.cross(omega, pivot)) if self.accel_reference == 'wheel_midpoint' else np.zeros(3)
        expected = np.array([self.wheel_acc, omega[2] * self.vb[0], 0.0])
        gravity_candidate = proper + pivot_rotation - expected
        norm = float(np.linalg.norm(gravity_candidate))
        confidence = max(0.0, 1.0 - abs(norm - G) / (G * 0.35))
        predicted_up = rotation(self.q).T[:, 2]
        innovation = float(np.linalg.norm(gravity_candidate - G * predicted_up))
        confidence *= max(0.0, 1.0 - innovation / self.innovation_limit) if self.innovation_limit > 0 else 1.0
        error = np.cross(gravity_candidate / max(norm, 1e-09), predicted_up)
        self._capture(p, dt, first, omega, proper, pivot, gravity_candidate, norm, confidence, innovation, predicted_up, error)
        self.q = quat_step(self.q, omega + self.accel_correction * confidence * np.clip(error, -0.3, 0.3), dt)
        angles = rpy(self.q)
        self.yaw += wrap(float(angles[2]) - self.last_yaw_wrapped)
        self.last_yaw_wrapped = float(angles[2])
        gravity_body = rotation(self.q).T @ np.array([0.0, 0.0, -G])
        linear = proper + gravity_body
        if self.accel_reference == 'wheel_midpoint' and self.ground_kinematic_constraint_enabled:
            origin_v_transverse = -np.cross(omega, pivot)
            linear[0] += omega[2] * origin_v_transverse[1] - omega[1] * origin_v_transverse[2]
        F = np.array([[1.0, -dt], [0.0, 1.0]])
        self.vb = F @ self.vb + np.array([dt * linear[0], 0.0])
        self.P = F @ self.P @ F.T + np.diag([(self.accel_std * dt) ** 2, (0.015 * dt) ** 2])
        innovation = wheel_mean - self.vb[0]
        disagreement = float(abs(wheel[0] - wheel[1]))
        R = self.wheel_std ** 2 * (1.0 + min(30.0, (disagreement / 0.15) ** 2))
        S = float(self.P[0, 0] + R)
        K = self.P[:, 0] / S if self.wheel_measurement_enabled else np.zeros(2)
        self.vb += K * innovation
        I = np.eye(2)
        H = np.array([[1.0, 0.0]])
        A = I - K[:, None] @ H
        self.P = A @ self.P @ A.T + R * np.outer(K, K)
        self.distance += self.vb[0] * dt
        roll, pitch = (float(angles[0]), float(angles[1]))
        pitchdot = omega[1] * math.cos(roll) - omega[2] * math.sin(roll)
        yawdot = (omega[1] * math.sin(roll) + omega[2] * math.cos(roll)) / max(math.cos(pitch), 0.15)
        lq = p.joint_pos4
        lv = p.joint_vel4
        x = np.array([self.distance, self.yaw, pitch, lq[0], lq[1] - lq[0], lq[2], lq[3] - lq[2], self.vb[0], yawdot, pitchdot, lv[0], lv[1] - lv[0], lv[2], lv[3] - lv[2]])
        contact = float(np.clip(confidence * (1.0 - min(1.0, disagreement / 0.7)), 0, 1))
        e = Estimate(x, roll, omega.copy(), proper.copy(), float(self.P[0, 0]), wheel.copy(), max(0.0, p.arrival_s - stamp), stamp, float(innovation), contact)
        self.prev_stamp = stamp
        self.prev_omega = omega.copy()
        self.prev_wheel = wheel_mean
        self.last = e
        return self._predict_view(e, p.arrival_s)

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
