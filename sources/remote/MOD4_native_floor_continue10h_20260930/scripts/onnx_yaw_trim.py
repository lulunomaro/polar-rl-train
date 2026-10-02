# Measure and remove the learned steady-state YAW BIAS of an exported policy.
#
# Why: probe_yaw_bias.py showed that at a zero yaw command the v14/v15/v16 policies keep a
# constant wheel differential that settles the robot at ~0.16-0.20 rad/s of unintended yaw.
# On the RMUC2026 map that costs most of the straight-line speed: the robot drives a wide
# arc, so its world-x progress decays from 0.8 to 0.4 m/s while the wheels still turn at
# 1.0 m/s.  Adding a small constant to the yaw command cancels it exactly (measured: the
# map speed becomes a held 1.00 m/s and the flat run improves 2.6x) and costs nothing on the
# gyro skill (2.28 -> 2.29 rev/s).
#
# The correction is BAKED INTO THE NETWORK (an Add on obs[2] before the normalizer) so every
# consumer - ROS2 controller, CPU harness, real bridge - gets the calibrated policy from the
# single artifact it already loads.  No per-deployment parameter to forget.
import sys, os, argparse
import numpy as np, onnx, onnxruntime as ort
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
WHEEL_SCALE = 55.0
R_WHEEL, HALF_TRACK = 0.073, 0.270


def make_session(path):
    return ort.InferenceSession(path, providers=["CPUExecutionProvider"])


def obs(wz_cmd, yaw):
    o = np.zeros(35, dtype=np.float32)
    o[2] = wz_cmd
    o[3] = 0.22 * 5.0
    o[6] = 0.5 * yaw
    o[9] = -1.0
    o[28] = 1.0
    return o.reshape(1, 35)


def equilibrium_yaw(sess, trim):
    # the fixed point of yaw_{k+1} = 0.27 * (aL - aR) with the command offset by trim
    y = 0.0
    for _ in range(200):
        a = sess.run(None, {"obs": obs(trim, y)})[0][0]
        target = (a[4] - a[5]) * WHEEL_SCALE * R_WHEEL / HALF_TRACK
        y_new = 0.5 * y + 0.5 * target
        if abs(y_new - y) < 1e-6:
            y = y_new; break
        y = y_new
    return y


ap = argparse.ArgumentParser()
ap.add_argument("--onnx", required=True)
ap.add_argument("--measure", action="store_true")
ap.add_argument("--bake", action="store_true")
ap.add_argument("--trim", type=float, default=None)
ap.add_argument("--out", default=None)
a = ap.parse_args()
sess = make_session(a.onnx)
if a.measure or a.trim is None:
    y0 = equilibrium_yaw(sess, 0.0)
    print("untrimmed equilibrium yaw = %+0.4f rad/s" % y0, flush=True)
    lo, hi = (0.0, 1.0) if y0 < 0 else (-1.0, 0.0)
    for _ in range(40):
        mid = 0.5 * (lo + hi)
        if equilibrium_yaw(sess, mid) * (1 if y0 > 0 else -1) > 0:
            lo = mid
        else:
            hi = mid
    trim = a.trim if a.trim is not None else 0.5 * (lo + hi)
    print("solved yaw trim = %+0.4f rad/s (equilibrium there %+0.5f rad/s)"
          % (trim, equilibrium_yaw(sess, trim)), flush=True)
else:
    trim = a.trim
if not a.bake:
    sys.exit(0)

model = onnx.load(a.onnx)
g = model.graph
assert g.input[0].name == "obs", g.input[0].name
vec = np.zeros((1, 35), dtype=np.float32); vec[0, 2] = trim
g.initializer.append(onnx.numpy_helper.from_array(vec, "yaw_trim_vec"))
add = onnx.helper.make_node("Add", ["obs", "yaw_trim_vec"],
                            ["obs_trimmed"], name="/yaw_trim/Add")
for n in g.node:
    for i, inp in enumerate(n.input):
        if inp == "obs":
            n.input[i] = "obs_trimmed"
g.node.insert(0, add)
g.input[0].name = "obs"
meta = {e.key: e for e in model.metadata_props}
def put(k, v):
    if k in meta:
        meta[k].value = v
    else:
        e = onnx.StringStringEntryProto(); e.key = k; e.value = v
        model.metadata_props.append(e); meta[k] = e
put("yaw_command_trim_rad_s", "%.4f" % trim)
out = a.out or a.onnx
onnx.save(model, out)
chk = make_session(out)
print("baked; re-measured equilibrium yaw = %+0.5f rad/s -> %s"
      % (equilibrium_yaw(chk, 0.0), "OK" if abs(equilibrium_yaw(chk, 0.0)) < 0.02 else "STILL BIASED"))
print("wrote", out)