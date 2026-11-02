"""Named contact diagnostic. No audit data is given to the controller."""
import numpy as np
import mujoco
from physics_bridge_rm_grade_v1 import BufferedImuPlant


class RMNamedContactPlant(BufferedImuPlant):
    def __init__(self, *args, guide_priority_variant=False, **kwargs):
        super().__init__(*args, **kwargs)
        self.guide_priority_variant = bool(guide_priority_variant)
        self.terrain_ids = {i for i in range(self.m.ngeom) if self.m.geom(i).name == 'ground' or self.m.geom(i).name.startswith('rm_bar_')}
        if self.guide_priority_variant:
            guide = [i for i in range(self.m.ngeom) if self.m.geom(i).name.startswith('guide_wheel_')]
            self.m.geom_priority[guide] = int(np.max(self.m.geom_priority)) + 1
        self.contact_stats = {}
        self.first_nonwheel = None
        self.first_bar_tire = None

    def _audit_contact_step(self):
        stage = max(0., float(self.d.time) - self.dt)
        for ci, contact in enumerate(self.d.contact):
            a, b = int(contact.geom1), int(contact.geom2)
            if a not in self.terrain_ids and b not in self.terrain_ids:
                continue
            robot, terrain = (b, a) if a in self.terrain_ids else (a, b)
            force = np.zeros(6)
            mujoco.mj_contactForce(self.m, self.d, ci, force)
            normal = max(0., float(force[0]))
            if normal <= 1.:
                continue
            name = self.m.geom(robot).name
            env_name = self.m.geom(terrain).name
            kind = 'main_wheel' if robot in self.tires else 'guide_roller' if name.startswith('guide_wheel_') else 'hard_other'
            record = dict(stage_s=stage, robot_geom=name, robot_body=self.m.body(int(self.m.geom_bodyid[robot])).name,
                          environment_geom=env_name, kind=kind, normal_N=normal,
                          contact_point_m=contact.pos.tolist(), normal_geom1_to2=contact.frame[:3].tolist(),
                          effective_friction5=contact.friction.tolist())
            if kind != 'main_wheel' and self.first_nonwheel is None:
                self.first_nonwheel = record
            if kind == 'main_wheel' and env_name != 'ground' and self.first_bar_tire is None:
                self.first_bar_tire = record
            key = name + '|' + env_name
            stats = self.contact_stats.setdefault(key, dict(kind=kind, body=record['robot_body'], ticks=0,
                               normal_impulse_Ns=0., peak_N=0., first_stage_s=stage, last_stage_s=stage))
            stats['ticks'] += 1
            stats['normal_impulse_Ns'] += normal * self.dt
            stats['peak_N'] = max(stats['peak_N'], normal)
            stats['last_stage_s'] = stage

    def apply_torque_request(self, tau, packet, dt=0.01, mechanical_power_limit=None):
        self.last_control_wheel_impulse = np.zeros(2)
        self.last_control_nonwheel_ticks = 0
        terrain = {i for i in range(self.m.ngeom) if self.m.geom(i).name == 'ground' or self.m.geom(i).name.startswith('rm_bar_')}
        tau = np.asarray(tau, float)
        assert tau.shape == (6,) and np.isfinite(tau).all()
        q = np.zeros(6)
        qd = np.zeros(6)
        leg = [0, 1, 3, 4]
        q[leg] = packet.joint_pos4
        qd[leg] = packet.joint_vel4
        qd[[2, 5]] = packet.wheel_vel2
        target = q + (tau + self.KD * qd) / self.KP
        target[[2, 5]] = qd[[2, 5]] + tau[[2, 5]] / self.wKD
        target[leg] = np.clip(target[leg], -3, 3)
        for i in (0, 3):
            target[i + 1] = np.clip(target[i + 1], target[i] - 1.0843, target[i] + 0.85)
        target[[2, 5]] = np.clip(target[[2, 5]], -60, 60)
        self.last_request = tau.copy()
        for _ in range(round(dt / self.dt)):
            applied = self.dr.process_targets(target, self.tick_phys) if self.dr else target
            actual_q = self.d.qpos[self.qids]
            actual_dq = self.d.qvel[self.vids]
            kp = self.dr.KP6 if self.dr else np.array([60.0, 60.0, 0.0, 60.0, 60.0, 0.0])
            kd = self.dr.KD6 if self.dr else np.array([2.0, 2.0, 0.6, 2.0, 2.0, 0.6])
            raw = kp * (applied - actual_q) - kd * actual_dq
            raw[[2, 5]] = kd[[2, 5]] * (applied[[2, 5]] - actual_dq[[2, 5]])
            bounded = self.clip(self.clip(raw) * (self.dr.motor_gain6 if self.dr else 1.0))
            power = float(np.maximum(bounded * actual_dq, 0).sum())
            if mechanical_power_limit is not None and power > mechanical_power_limit:
                bounded *= mechanical_power_limit / power
            self.d.ctrl[:] = bounded
            self.max_mechanical_power = max(self.max_mechanical_power, float(np.maximum(bounded * actual_dq, 0).sum()))
            self.max_applied_tau = np.maximum(self.max_applied_tau, np.abs(bounded))
            self.rate_sum += self.d.qvel[self.vids]
            mujoco.mj_step(self.m, self.d)
            self.tick_phys += 1
            self.imu_omega_sum += self.d.sensor('base_gyro').data
            self.imu_acc_sum += self.d.sensor('base_acceleration').data
            self.imu_window_count += 1
            self.total_highrate_IMU_samples += 1
            self._audit_contact_step()
            hit = False
            for ci, ct in enumerate(self.d.contact):
                a, b = (int(ct.geom1), int(ct.geom2))
                if a not in terrain and b not in terrain:
                    continue
                force = np.zeros(6)
                mujoco.mj_contactForce(self.m, self.d, ci, force)
                other = b if a in terrain else a
                if other in self.tires:
                    self.last_control_wheel_impulse[self.tires.index(other)] += max(0.0, float(force[0])) * self.dt
                elif force[0] > 1:
                    self._audit_contact_step()
                    hit = True
            self.last_control_nonwheel_ticks += int(hit)
