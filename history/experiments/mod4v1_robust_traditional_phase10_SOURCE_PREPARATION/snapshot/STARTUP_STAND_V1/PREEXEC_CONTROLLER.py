"""New sensor-only, limited-pose startup TRAIN hypothesis; no plant or actuator I/O.
Caller owns original estimator/driver/health grading. Never a wheel-support certificate.
"""
import math
from numbers import Real
import numpy as np
from ground_controller_v4 import GroundController

LEG = np.array([0, 1, 3, 4])
WHEEL = np.array([2, 5])
EFFORT = np.array([40., 40., 5.775909774436091] * 2)
QMIN = np.array([-.5000000058364024, -1.2000000140073657] * 2)
QMAX = np.array([.5000000058364024, .8999999772160105] * 2)
DELTA_MIN, DELTA_MAX = -1.0843, .85


def scalar(x, label):
    if isinstance(x, (bool, np.bool_)) or not isinstance(x, Real) or not math.isfinite(float(x)):
        raise ValueError(label + ': finite real required')
    return float(x)


def vector(x, n, label):
    a = np.asarray(x)
    if a.shape != (n,) or a.dtype.kind not in 'fiu' or not np.isfinite(a).all():
        raise ValueError(label + ': finite numeric vector required')
    return a.astype(float, copy=True)


def absolute4(x, velocity=False):
    a = 10 if velocity else 3
    return np.array([x[a], x[a] + x[a+1], x[a+2], x[a+2] + x[a+3]])


def project_reference(q):
    """Reference ONLY projection. Never modify or relabel the measured packet."""
    out = np.clip(vector(q, 4, 'q measured'), QMIN, QMAX)
    for i in (0, 2):
        out[i+1] = np.clip(out[i+1], max(QMIN[i+1], out[i]+DELTA_MIN),
                           min(QMAX[i+1], out[i]+DELTA_MAX))
    return out


def legal_reference(q, qd):
    if np.any(q < QMIN) or np.any(q > QMAX) or np.max(np.abs(qd)) > 1. + 1e-12:
        raise ValueError('reference outside published active box/rate')
    for i in (0, 2):
        if not DELTA_MIN <= q[i+1]-q[i] <= DELTA_MAX:
            raise ValueError('reference outside unchanged relative driver box')


def quintic(u):
    u = max(0., min(1., float(u)))
    return u**3*(10.+u*(-15.+6.*u)), 30.*u*u*(1.-u)*(1.-u)


class StartupStand:
    """API: prepare_estimator(est, now), then command(e, packet, now, attitude_q)."""
    def __init__(self, gain_nominal, geometry, config=None):
        c = {} if config is None else dict(config)
        if set(c) - {'operator_enable'} or type(c.get('operator_enable', False)) is not bool:
            raise ValueError('V1 config accepts only exact-bool operator_enable')
        self.enabled = c.get('operator_enable', False)
        g = gain_nominal.get('gain', gain_nominal)
        shapes = {'q': (7,), 'tau': (6,), 'Ad': (14, 14), 'Bd': (14, 6),
                  'Q': (14, 14), 'R': (6, 6)}
        self.gain = {}
        for key, shape in shapes.items():
            a = np.asarray(g[key])
            if a.shape != shape or a.dtype.kind not in 'fiu' or not np.isfinite(a).all():
                raise ValueError('nominal gain finite shape: ' + key)
            self.gain[key] = a.astype(float, copy=True)
        q = self.gain['q']
        self.target = np.array([q[3], q[3]+q[4], q[5], q[5]+q[6]])
        legal_reference(self.target, np.zeros(4))
        self.ff = self.gain['tau'].copy()
        self.geometry = geometry  # caller binding only; no geometry/model/FK calls
        self.ctrl = GroundController(self.gain, dict(position_weight=25., position_leash=1.,
            yaw_kp=.8, yaw_ki=.5, yaw_integral_limit=15., roll_kp=20., roll_kd=2.,
            model_predict_fraction=0.))
        self.phase = 'OBSERVE' if self.enabled else 'DISARMED'
        self.fault_reason = None
        self.started = self.entered = None
        self.last_prepare = self.last_command = self.last_sensor = None
        self.prepared = None
        self.static_since = self.ready_since = None
        self.static_q0 = self.measured_q0 = self.q0 = None
        self.qref = self.target.copy()
        self.vref = np.zeros(4)
        self.last_tau = np.zeros(6)
        self.blend_from = np.zeros(6)
        self.project_delta = np.zeros(4)
        self.observer = {'applied': False}
        self.transitions = []
        self.log = {'phase': self.phase, 'operator_enable': self.enabled,
                    'contact_or_support_trusted': False}

    def _time(self, now, previous):
        t = scalar(now, 'control time')
        if t < 0 or abs(t-round(t/.01)*.01) > 1e-8:
            raise ValueError('control time not nonnegative100Hz grid')
        if previous is not None and (t <= previous or t-previous > .05+1e-8):
            raise ValueError('control clock duplicate/backward/gap')
        return t

    def _fault(self, reason):
        if self.fault_reason is None:
            self.fault_reason = str(reason)
        self.phase = 'INHIBIT'
        self.last_tau = np.zeros(6)
        self.log = {'phase': 'INHIBIT', 'fault_reason': self.fault_reason,
                    'operator_enable': self.enabled, 'observer': dict(self.observer),
                    'contact_or_support_trusted': False, 'hardware_send_permission': False}
        return self.last_tau.copy()

    def _enter(self, phase, t):
        self.transitions.append({'time_s': t, 'from': self.phase, 'to': phase})
        self.phase, self.entered = phase, t

    def prepare_estimator(self, est, now):
        if not self.enabled:
            self.observer = {'applied': False, 'reason': 'operator_disabled_no_estimator_mutation'}
            return
        try:
            t = self._time(now, self.last_prepare)
            self.last_prepare = t
            if self.started is None:
                self.started = self.entered = t
            if getattr(est, 'upright_prior', None) is not False:
                raise ValueError('upright_prior=False explicitly required; no attitude overwrite')
            for key in ('wheel_measurement_enabled', 'ground_kinematic_constraint_enabled', 'accel_correction'):
                if not hasattr(est, key):
                    raise ValueError('estimator lacks declared startup switch: ' + key)
            on = self.phase == 'BALANCE' and self.fault_reason is None
            est.wheel_measurement_enabled = on
            est.ground_kinematic_constraint_enabled = on
            est.accel_correction = 1.5
            self.observer = {'applied': True, 'prepare_time_s': t, 'prepare_phase': self.phase,
                'wheel_measurement_enabled': bool(est.wheel_measurement_enabled),
                'ground_kinematic_constraint_enabled': bool(est.ground_kinematic_constraint_enabled),
                'accel_correction': float(est.accel_correction),
                'quaternion_velocity_distance_or_covariance_reset': False}
            self.prepared = t
        except (ValueError, TypeError, AttributeError, OverflowError) as ex:
            self._fault(ex)

    def _sample(self, e, p, t, attitude_q):
        if getattr(p, 'validity', None) is not True:
            raise ValueError('sensor packet validity not True')
        x = vector(e.state14, 14, 'state14')
        roll = scalar(e.roll, 'roll')
        omega = vector(e.omega_body, 3, 'omega')
        age = scalar(e.sensor_age_s, 'sensor age')
        stamp, arrival = scalar(p.time_s, 'source time'), scalar(p.arrival_s, 'arrival')
        estimate_time = scalar(e.estimated_time_s, 'estimate time')
        if not 0. <= age <= .05 or stamp < 0 or stamp > arrival+.002 or arrival > t+.002:
            raise ValueError('sensor clock/age/future')
        if t-stamp > .05+.002 or t-arrival > .05 or abs(estimate_time-t) > .002:
            raise ValueError('sensor stale or estimate epoch not control epoch')
        if self.last_sensor is not None and stamp < self.last_sensor-1e-8:
            raise ValueError('sensor source rollback')
        fresh = self.last_sensor is None or stamp > self.last_sensor+1e-8
        self.last_sensor = stamp
        qp, qd = vector(p.joint_pos4, 4, 'encoder q4'), vector(p.joint_vel4, 4, 'encoder qd4')
        proper = vector(p.accel_proper_body, 3, 'IMU proper')
        gyro = vector(p.gyro_body, 3, 'raw gyro')
        vector(p.wheel_vel2, 2, 'wheel rate')
        aq = vector(attitude_q, 4, 'attitude quaternion')
        if abs(float(aq@aq)-1.) > 1e-6:
            raise ValueError('attitude quaternion not unit')
        w, a, b, c = aq
        qr = math.atan2(2*(b*c+w*a), 1-2*(a*a+b*b))
        qpitch = math.atan2(2*(w*b-c*a), math.hypot(1-2*(b*b+c*c), 2*(a*b+w*c)))
        if abs(qr-roll) > .1 or abs(qpitch-x[2]) > .1:
            raise ValueError('estimated tilt inconsistent with supplied AHRS')
        if abs(x[2]) > 1. or abs(roll) > .25:
            raise ValueError('limited startup pitch/roll envelope exceeded')
        # Tiny soft-limit excursions are retained in qp, never silently clipped.
        if np.max(np.abs(project_reference(qp)-qp)) > .04:
            raise ValueError('measured q too far outside reference box')
        return x, roll, omega, qp, qd, proper, gyro, fresh, age, stamp

    def _ready(self, x, roll, omega, q, qd, fresh):
        return bool(fresh and abs(x[2]) < .15 and abs(roll) < .15
            and np.max(np.abs(q-self.target)) <= .04 and np.max(np.abs(qd)) <= .20
            and np.linalg.norm(omega) <= .50)

    def _anchor_ground(self, x):
        self.ctrl.ref = self.ctrl.eq.copy()
        self.ctrl.ref[0], self.ctrl.ref[1] = x[0], x[1]
        self.ctrl.ref[7:14] = 0.
        self.ctrl.yaw_integral = self.ctrl.old_shaped_w = 0.
        self.ctrl.shaper.v = self.ctrl.shaper.w = self.ctrl.shaper.a = 0.
        self.ctrl.previous = self.last_tau.copy()

    def _ground_reference(self):
        r, v = self.qref, self.vref
        self.ctrl.ref[3:7] = [r[0], r[1]-r[0], r[2], r[3]-r[2]]
        self.ctrl.ref[10:14] = [v[0], v[1]-v[0], v[2], v[3]-v[2]]
        self.ctrl.ref[2] = self.ctrl.ref[9] = 0.

    def command(self, e, packet, now, attitude_q):
        if not self.enabled:
            self.last_tau = np.zeros(6)
            self.log = {'phase': 'DISARMED', 'operator_enable': False,
                        'observer': dict(self.observer), 'contact_or_support_trusted': False}
            return self.last_tau.copy()
        if self.fault_reason is not None:
            return self._fault(self.fault_reason)
        try:
            t = self._time(now, self.last_command)
            if self.prepared is None or abs(self.prepared-t) > 1e-8:
                raise ValueError('prepare_estimator required before this command epoch')
            self.last_command = t
            x, roll, omega, q, qd, proper, gyro, fresh, age, stamp = self._sample(e, packet, t, attitude_q)
            if self.phase != 'BALANCE' and t-self.started >= 6.-1e-10:
                raise ValueError('startup timeout6s')
            scale, blend = 0., 0.
            if self.phase == 'OBSERVE':
                # Explicit valid static proper-tilt check, never reset est.q to upright.
                norm = float(np.linalg.norm(proper))
                pr = math.atan2(proper[1], proper[2])
                pp = math.atan2(-proper[0], math.hypot(proper[1], proper[2]))
                static = (fresh and .8*9.81 <= norm <= 1.2*9.81
                    and np.linalg.norm(gyro) <= .15 and np.linalg.norm(omega) <= .15
                    and np.max(np.abs(qd)) <= .15 and abs(pr-roll) <= .1 and abs(pp-x[2]) <= .1)
                if static and self.static_since is not None and np.max(np.abs(q-self.static_q0)) > .02:
                    static = False
                if not static:
                    self.static_since = self.static_q0 = None
                elif self.static_since is None:
                    self.static_since, self.static_q0 = t, q.copy()
                self.qref, self.vref = project_reference(q), np.zeros(4)
                if self.static_since is not None and t-self.static_since >= .25-1e-10:
                    self.measured_q0, self.q0 = q.copy(), project_reference(q)
                    self.project_delta = self.q0-self.measured_q0
                    if np.max(np.abs(self.target-self.q0))*1.875/2. > 1.:
                        raise ValueError('quintic peak reference speed exceeds1rad/s')
                    self._anchor_ground(x)
                    self._enter('SHAPE_TO_STAND', t)
                else:
                    self.last_tau = np.zeros(6)
                    return self._publish(t, self.last_tau, scale, blend, q, age, stamp)
            if self.phase == 'SHAPE_TO_STAND':
                u = (t-self.entered)/2.
                scale, ds = quintic(u)
                self.qref = self.q0+(self.target-self.q0)*scale
                self.vref = (self.target-self.q0)*ds/2.
                if u >= 1.-1e-10:
                    self.qref, self.vref = self.target.copy(), np.zeros(4)
                    scale = 1.
                    self.ready_since = None
                    self._enter('VERIFY', t)
            if self.phase in ('VERIFY', 'BLEND', 'BALANCE'):
                self.qref, self.vref, scale = self.target.copy(), np.zeros(4), 1.
            if self.phase == 'VERIFY':
                if not self._ready(x, roll, omega, q, qd, fresh):
                    self.ready_since = None
                elif self.ready_since is None:
                    self.ready_since = t
                if self.ready_since is not None and t-self.ready_since >= .5-1e-10:
                    self.blend_from = self.last_tau.copy()
                    self._anchor_ground(x)  # only controller refs/state, never estimator state
                    self._enter('BLEND', t)
            if self.phase == 'BLEND' and not self._ready(x, roll, omega, q, qd, fresh):
                raise ValueError('handoff readiness lost during blend')
            legal_reference(self.qref, self.vref)
            self._ground_reference()
            ground = vector(self.ctrl.command(e, 0., 0.), 6, 'GroundController tau')
            if not self.ctrl.valid_command:
                raise ValueError('GroundController invalid command')
            if self.phase in ('SHAPE_TO_STAND', 'VERIFY'):
                tau = np.zeros(6)
                tau[LEG] = 60.*(self.qref-q)+3.*(self.vref-qd)+scale*self.ff[LEG]
                tau[WHEEL] = scale*ground[WHEEL]
            elif self.phase == 'BLEND':
                blend, _ = quintic((t-self.entered)/.5)
                tau = (1.-blend)*self.blend_from+blend*ground
                if t-self.entered >= .5-1e-10:
                    self._enter('BALANCE', t)
            elif self.phase == 'BALANCE':
                blend, tau = 1., ground
            else:
                raise ValueError('unknown startup phase')
            tau = np.clip(vector(tau, 6, 'startup tau'), -EFFORT, EFFORT)
            self.last_tau = tau.copy()
            return self._publish(t, tau, scale, blend, q, age, stamp)
        except (ValueError, TypeError, AttributeError, IndexError, OverflowError, ArithmeticError) as ex:
            return self._fault(ex)

    def _publish(self, t, tau, scale, blend, measured, age, stamp):
        self.log = {'phase': self.phase, 'time_s': t, 'operator_enable': self.enabled,
            'source_time_s': stamp, 'sensor_age_s': age, 'observer': dict(self.observer),
            'reference_q4': self.qref.tolist(), 'reference_qd4': self.vref.tolist(),
            'measured_q4_UNMODIFIED': measured.tolist(),
            'locked_measured_q0': None if self.measured_q0 is None else self.measured_q0.tolist(),
            'locked_projected_reference_q0': None if self.q0 is None else self.q0.tolist(),
            'reference_projection_delta4': self.project_delta.tolist(),
            'reference_projection_applied': bool(np.any(self.project_delta != 0.)),
            'nominal_ff_scale': scale, 'startup_wheel_scale': scale,
            'handoff_blend': blend, 'ground_ref_distance_yaw': self.ctrl.ref[:2].tolist(),
            'output_tau6_Nm': tau.tolist(), 'contact_or_support_trusted': False,
            'sensor_gate_is_not_double_wheel_support_proof': True,
            'physical_standup_success_NOT_claimed': True, 'hardware_send_permission': False}
        return tau.copy()


Controller = StartupStand
