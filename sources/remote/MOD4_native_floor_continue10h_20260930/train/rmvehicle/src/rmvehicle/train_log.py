"""Recover the actuator envelope a checkpoint was ACTUALLY trained under.

mjlab dumps the full env config next to every run (`<run>/params/env.yaml`).  Without this,
an exported ONNX only carries the contract of whatever source tree happened to be checked out
at export time -- exactly how a policy trained at 5.5 N.m / 63.4 rad/s wheels could be stamped
as a DM3519+15.8 policy.  This module reads the training-time numbers back out of the run
directory so the exporter can refuse that lie.
"""
import io
import os
import re

NUM_FIELDS = ("stiffness", "damping", "effort_limit", "saturation_effort", "velocity_limit",
              "delay_min_lag", "delay_max_lag")


def params_path(checkpoint):
  """`<run>/model_123.pt` -> `<run>/params/env.yaml` (empty string when absent)."""
  run = os.path.dirname(os.path.abspath(checkpoint))
  p = os.path.join(run, "params", "env.yaml")
  return p if os.path.isfile(p) else ""


def read_actuator_envelope(checkpoint):
  """{joint pattern -> {field: float}} for every actuator block in the training log."""
  path = params_path(checkpoint)
  if not path:
    return {}
  lines = io.open(path, encoding="utf-8").read().splitlines()
  out, i = {}, 0
  while i < len(lines):
    if "target_names_expr" not in lines[i]:
      i += 1
      continue
    names, j = [], i + 1
    while j < len(lines) and re.match(r"^\s*-\s+\S+\s*$", lines[j]):
      names.append(re.sub(r"^\s*-\s+", "", lines[j]).strip())
      j += 1
    vals, k = {}, j
    while k < len(lines) and "target_names_expr" not in lines[k]:
      m = re.match(r"^\s*(" + "|".join(NUM_FIELDS) + r"):\s*([-0-9.eE]+)\s*$", lines[k])
      if m:
        vals[m.group(1)] = float(m.group(2))
      k += 1
    for n in names:
      out[n.strip("^$")] = dict(vals)
    i = j
  return out


def _pick(env, pattern, field):
  for key, vals in env.items():
    if pattern in key:
      return vals.get(field)
  return None


def describe(env):
  return "; ".join("%s %s" % (k, v) for k, v in sorted(env.items()))


def check_against_contract(env, c, leg_hints=("front1", "crank", "hip")):
  """Human-readable list of disagreements between the training log and the deploy contract."""
  if not env:
    return ["训练日志里找不到 params/env.yaml，无法核实这个检查点当时的执行器包线"]
  bad = []
  # The earlier CC plant names its drives front1/rear1, the delivered later plant names
  # them crank/hip.  Probe every spelling so the same envelope check covers both.
  def leg(field, want, label):
    for hint in leg_hints:
      got = _pick(env, hint, field)
      if got is not None:
        return got, label
    return None, label
  probes = (
    ("wheel", "effort_limit", c["wheel_effort"], "轮端电流限幅平台 N.m"),
    ("wheel", "saturation_effort", c["wheel_voltage_line_intercept"],
     "轮端电压线零速截距 N.m"),
    ("wheel", "velocity_limit", c["wheel_no_load"], "轮端空载转速 rad/s"),
    ("wheel", "damping", c["wheel_kd"], "轮端阻尼"),
  )
  leg_probes = (
    ("effort_limit", c["leg_effort"], "腿端电流限幅平台 N.m"),
    ("saturation_effort", c["leg_voltage_line_intercept"], "腿端电压线零速截距 N.m"),
    ("velocity_limit", c["leg_no_load"], "腿端空载转速 rad/s"),
    ("stiffness", c["leg_kp"], "腿端 kp"),
    ("damping", c["leg_kd"], "腿端 kd"),
  )
  for pat, field, want, label in probes:
    got = _pick(env, pat, field)
    if got is None:
      bad.append("%s: 训练日志里读不到 %s" % (label, field))
    elif abs(got - float(want)) > (abs(float(want)) * 0.02 if field == "velocity_limit"
                                   else 1e-3):
      bad.append("%s: 训练时 %s=%s，当前合同 %s" % (label, field, got, want))
  for field, want, label in leg_probes:
    got, _ = leg(field, want, label)
    # velocity_limit is allowed to differ by 2%: older runs rounded the datasheet no-load
    # speed (17.0 vs 16.755 rad/s), which is not a motor-model change worth blocking an
    # export over.  Torque, damping and stiffness have no such excuse.
    tol = abs(float(want)) * 0.02 if field == "velocity_limit" else 1e-3
    if got is None:
      bad.append("%s: 训练日志里读不到 %s" % (label, field))
    elif abs(got - float(want)) > tol:
      bad.append("%s: 训练时 %s=%s，当前合同 %s" % (label, field, got, want))
  return bad
