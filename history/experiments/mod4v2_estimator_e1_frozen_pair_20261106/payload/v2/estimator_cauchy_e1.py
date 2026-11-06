from __future__ import annotations
import copy,math
from sensor_core_jump_v1 import *
from observer_audit_v1 import AuditedStateEstimator,ObserverSidecar

def cauchy_innovation_weight(innovation,limit):
    if not math.isfinite(innovation)or not math.isfinite(limit):raise ValueError('Nonfinite innovation scale')
    if limit<=0.:return 1. # preserve explicit disabled-innovation-gate convention
    inverse=1./math.hypot(1.,float(innovation)/float(limit))
    return inverse*inverse

class CauchyEstimatorE1(AuditedStateEstimator):
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
        confidence *= cauchy_innovation_weight(innovation, self.innovation_limit)
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

class MatchingE1Sidecar(ObserverSidecar):
    def __init__(self,original):
        super().__init__(original)
        self.audit=CauchyEstimatorE1(copy.deepcopy(original.geom),original.offset.copy(),accel_correction=original.accel_correction,
            wheel_std=original.wheel_std,accel_std=original.accel_std,accel_reference=original.accel_reference,
            innovation_limit=original.innovation_limit,upright_prior=original.upright_prior)
    def summary(self):
        s=super().summary();s['witness_reference_variant']='E1 not original-baseline';s['not_baseline_equivalence_claim']=True
        return s
