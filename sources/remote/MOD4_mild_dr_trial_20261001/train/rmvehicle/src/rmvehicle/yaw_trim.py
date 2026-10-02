# Learned steady-state YAW BIAS of an exported policy: measure, solve, bake.
#
# probe_yaw_bias.py found that the v14/v15/v16 policies keep a constant wheel differential
# at a zero yaw command, so the closed loop settles at ~0.17 rad/s of unintended yaw.  On
# the RMUC2026 map that is what destroys the straight-line speed (the robot drives a wide
# arc: world-x progress decays 0.82 -> 0.40 m/s while the wheels still turn at 1.0 m/s).
# A constant added to the yaw command cancels it; baking it INTO the network (an Add on
# obs[2] before the observation normalizer) means every consumer - ROS2 controller, CPU
# parity harness, real bridge - gets the calibrated policy from the one artifact it already
# loads, with no parameter that can be forgotten.
import numpy as np
import onnx
import onnxruntime as ort
from dataclasses import dataclass


@dataclass(frozen=True)
class Geometry:
    """The three numbers that convert a wheel differential into a yaw rate.

    They used to be module constants hardcoded to the CC plant (55.0 / 0.073 / 0.270).
    The later no-gimbal plant is 55.0 / 0.0625 / 0.235854, so the old constants silently
    baked a trim ~2 % off into every later-model export.  Defaults stay CC for backwards
    compatibility; new callers must pass ``geometry_from_contract``.
    """

    wheel_scale: float = 55.0
    wheel_radius: float = 0.073
    half_track: float = 0.270

    @property
    def rad_s_per_yaw_rad_s(self) -> float:
        return self.half_track / self.wheel_radius


CC_GEOMETRY = Geometry()
# Back-compat aliases for external scripts that still import the constants.
WHEEL_SCALE = CC_GEOMETRY.wheel_scale
R_WHEEL, HALF_TRACK = CC_GEOMETRY.wheel_radius, CC_GEOMETRY.half_track


def geometry_from_contract(contract: dict) -> Geometry:
    """Build the trim geometry from ``contract.json`` instead of re-typing constants."""
    return Geometry(
        wheel_scale=float(contract["wheel_action_scale"]),
        wheel_radius=float(contract["wheel_radius"]),
        half_track=float(contract["half_track"]),
    )


def session(path):
    return ort.InferenceSession(path, providers=["CPUExecutionProvider"])

def session_from_model(model):
    return ort.InferenceSession(model.SerializeToString(), providers=["CPUExecutionProvider"])


def make_obs(wz_cmd, yaw, height=0.22):
    o = np.zeros(35, dtype=np.float32)
    o[2] = wz_cmd
    o[3] = height * 5.0
    o[6] = 0.5 * yaw
    o[9] = -1.0
    o[28] = 1.0
    return o.reshape(1, 35)


def equilibrium_yaw(sess, trim, geom: Geometry | None = None):
    geom = geom or CC_GEOMETRY
    y = 0.0
    for _ in range(400):
        a = sess.run(None, {"obs": make_obs(trim, y)})[0][0]
        target = (a[4] - a[5]) * geom.wheel_scale / geom.rad_s_per_yaw_rad_s
        y_new = 0.5 * y + 0.5 * target
        if abs(y_new - y) < 1e-7:
            return y_new
        y = y_new
    return y


def commanded_yaw(sess, trim, yaw=0.0, geom: Geometry | None = None):
    geom = geom or CC_GEOMETRY
    # the yaw rate the policy is aiming at, read from its own wheel differential
    a = sess.run(None, {'obs': make_obs(trim, yaw)})[0][0]
    return (a[4] - a[5]) * geom.wheel_scale / geom.rad_s_per_yaw_rad_s


def solve_trim(sess, geom: Geometry | None = None):
    geom = geom or CC_GEOMETRY
    # The yaw-command offset that makes the policy command ZERO wheel differential at zero
    # measured yaw.  This is the definition the closed loop needs, and it is robust: a plain
    # fixed-point iteration of the loop diverges for policies whose yaw feedback slope
    # exceeds one (v15 did - the first version of this file baked a wrong trim into it).
    y0 = commanded_yaw(sess, 0.0, geom=geom)
    if abs(y0) < 1e-3:
        return 0.0, y0
    lo, hi = (0.0, 2.0) if y0 < 0 else (-2.0, 0.0)
    flo = y0
    for _ in range(60):
        mid = 0.5 * (lo + hi)
        e = commanded_yaw(sess, mid, geom=geom)
        if (e < 0) == (flo < 0):
            lo, flo = mid, e
        else:
            hi = mid
    return 0.5 * (lo + hi), y0

def bake(model, trim):
    # Add a constant to obs[2].  Idempotent: applying it twice just updates the existing
    # vector.  The first version inserted a second node with the same name and rewired the
    # first one into a cycle, which corrupted one exported policy.
    import numpy as _np
    g = model.graph
    name = 'yaw_trim_vec'
    have = [k for k in range(len(g.initializer)) if g.initializer[k].name == name]
    if have:
        k = have[0]
        vec = onnx.numpy_helper.to_array(g.initializer[k]).copy()
        vec[0, 2] += trim
        g.initializer[k].CopyFrom(onnx.numpy_helper.from_array(vec, name=name))
        return 0
    vec = _np.zeros((1, 35), dtype=_np.float32)
    vec[0, 2] = trim
    g.initializer.append(onnx.numpy_helper.from_array(vec, name))
    # torch.onnx.export lists initializers as graph inputs; drop ours from that list so
    # onnxruntime treats it as a constant instead of an overridable input.
    # protobuf repeated fields do not support slice assignment (that TypeError killed the
    # v17a export at 11:37 and left an ONNX without its contract metadata).
    keep = [x for x in g.input if x.name != name]
    del g.input[:]
    g.input.extend(keep)
    node = onnx.helper.make_node('Add', ['obs', name],
                                 ['obs_trimmed'], name='/yaw_trim/Add')
    touched = 0
    for i2 in range(len(g.node)):
        n = g.node[i2]
        for k2, inp in enumerate(n.input):
            if inp == 'obs':
                n.input[k2] = 'obs_trimmed'; touched += 1
    if touched == 0:
        raise RuntimeError('nothing consumes the graph input obs')
    g.node.insert(0, node)
    return touched
