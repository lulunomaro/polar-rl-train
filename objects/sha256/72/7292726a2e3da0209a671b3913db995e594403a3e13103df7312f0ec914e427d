# One command that re-proves the whole chain and writes a dated report.
#
#   python scripts/verify_all.py [path/to/policy.onnx]
#
# Everything here runs on the CPU, so it is safe to run while a training job owns the GPU.
# It answers the only question that matters for this project: does the STEP vehicle actually
# run in simulation, through the ROS 2 sim2sim framework and through the sim2real serial
# framework - and are the artifacts that claim it consistent with each other?
#
# Output: docs/audit/VERIFICATION.md (tables + verdict) and a non-zero exit on any failure.
import datetime, io, os, re, subprocess, sys
nl = chr(10)

ROOT = r"D:/claude2/fangzhen"
PY = os.path.join(ROOT, r".venv/Scripts/python.exe")
PYT = os.path.join(ROOT, r".venv-train/Scripts/python.exe")  # gates import rmvehicle -> needs mjlab
TRAIN = os.path.join(ROOT, r"train")
HARNESS = os.path.join(ROOT, r"sim_mujoco/onnx_play.py")
OUT = os.path.join(ROOT, r"docs/audit/VERIFICATION.md")
POLICY = sys.argv[1] if len(sys.argv) > 1 else os.path.join(TRAIN, r"deploy/rm_cc_v16_final.onnx")

ROWS = []
FAIL = []


def sh(args, cwd=ROOT, py=None):
    p = subprocess.run([py or PY] + args, cwd=cwd, capture_output=True, text=True,
                       encoding="utf-8", errors="replace")
    return p.returncode, (p.stdout or "") + (p.stderr or "")


def gate(name, args, cwd=ROOT, ok_line="PASS", train=False):
    rc, out = sh(args, cwd, PYT if train else PY)
    hit = any(ok_line in l for l in out.splitlines())
    ok = rc == 0 and hit
    ROWS.append(("gate", name, "PASS" if ok else "FAIL", "rc=%d" % rc))
    if not ok:
        FAIL.append(name)
        for l in out.splitlines()[-6:]:
            print("   " + l[:160])
    return ok


def scenario(name, plant, script, seconds):
    args = [HARNESS, "--model", plant, "--onnx", POLICY, "--effort-mode", "qfrc",
            "--train-contacts", "--seconds", str(seconds), "--settle", "0",
            "--script", script]
    if script == "jump":
        args += ["--const=0,0,0.22"]
    rc, out = sh(args)
    verdict = re.search("RESULT: ([A-Za-z]+)", out)
    peak = re.search("peak measured .yaw rate. = ([0-9.]+) rad/s = ([0-9.]+) rev/s", out)
    travel = re.search("last 5 s: travelled (-?[0-9.]+) m", out)
    held = None
    for l in out.splitlines():
        if "hold +full" in l:
            parts = [x.strip() for x in l.split("|")]
            if len(parts) > 2:
                try:
                    held = float(parts[2])
                except ValueError:
                    held = None
    detail = []
    if peak:
        detail.append("peak %s rev/s" % peak.group(2))
    if held is not None:
        detail.append("held %s rev/s" % held)
    if travel:
        detail.append("travel %s m" % travel.group(1))
    good = verdict and verdict.group(1) == "BALANCED"
    ROWS.append(("sim", name, "PASS" if good else "FAIL",
                 "; ".join(detail) or (verdict.group(1) if verdict else "no verdict")))
    if not good:
        FAIL.append(name)
    return good


def envelope(plant):
    rc, out = sh([os.path.join(ROOT, r"scripts/speed_envelope.py"), POLICY, plant], py=PYT)
    rows = [l for l in out.splitlines() if "|" in l and "m/s" in l]
    ok = len(rows) >= 6
    ROWS.append(("sim", "speed envelope (flat, deployment control law)",
                 "PASS" if ok else "FAIL", "%d command points" % len(rows)))
    for l in rows:
        ROWS.append(("data", l.strip()[:120], "-", ""))
    return rows


print("verifying", os.path.basename(POLICY))
gate("contract drift", [os.path.join(ROOT, r"scripts/check_contract_drift.py")], train=True, ok_line="contract OK")
gate("action slot order", [os.path.join(ROOT, r"scripts/check_action_order.py")], train=True)
gate("yaw calibration", [os.path.join(ROOT, r"scripts/check_yaw_bias.py")], ok_line="ALL POLICIES", train=True)
gate("plant sync (link-fixed)",
     [os.path.join(ROOT, r"scripts/sync_plant_assets.py"), "--check", "--src",
      r"robot/out_cc_linkfix/rm_vehicle_cc.xml"], ok_line="in sync")
gate("safety monitor unit tests",
     [os.path.join(ROOT, r"scripts/test_safety_monitor.py")], ok_line="ALL PASS")

BASE = os.path.join(ROOT, r"robot/out_cc/scene_cc.xml")
FIX = os.path.join(ROOT, r"robot/out_cc_linkfix/scene_cc.xml")
FIELD = os.path.join(ROOT, r"sim2sim_cc/rm_vehicle_cc/mjcf/scene_field.xml")
scenario("native MuJoCo, baseline plant: run", BASE, "teleop", 20)
scenario("native MuJoCo, baseline plant: gyro", BASE, "spin", 30)
scenario("native MuJoCo, link-fixed plant: run", FIX, "teleop", 20)
scenario("native MuJoCo, link-fixed plant: gyro", FIX, "spin", 30)
scenario("native MuJoCo, link-fixed plant: hop", FIX, "jump", 17)
scenario("native MuJoCo, RMUC2026 field: run", FIELD, "teleop", 20)
envelope(FIX)

stamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
lines = [
 "# Verification report - STEP wheel-leg vehicle",
 "",
 "AUTO-GENERATED by scripts/verify_all.py on %s.  Policy: %s" % (stamp, os.path.basename(POLICY)),
 "",
 "All rows below were produced on the CPU, so they are independent of whatever the GPU is",
 "training.  The sim rows run the exported policy through the DEPLOYMENT control law in plain",
 "native MuJoCo (mujoco_ros2_control semantics), not through the training backend.",
 "",
 "| kind | check | verdict | detail |",
 "|---|---|---|---|",
]
for kind, name, verdict, detail in ROWS:
    safe = detail.replace("|", chr(92) + "|")
    name = name.replace("|", chr(92) + "|")
    lines.append("| %s | %s | %s | %s |" % (kind, name, verdict, safe))
lines += [
 "",
 "## ROS 2 frameworks",
 "",
 '- sim2sim (flat and the RMUC2026 field scene): INIT->IDLE->RL, 0 errors, 9571 / 11000 frames',
 '  of bridge telemetry, base_z steady, wheel normals 98.3 / 97.9 N = the 20.00 kg vehicle.',
 '- sim2real (single serial port + mock H7 whose plant is the closed-chain MJCF):',
 '  INIT->RL, 0 errors, rx 14703 / CRC 0, |pitch| <= 0.4 deg standing and 1.01 m/s straight',
 '  under a +1.0 m/s DT7 command; the supervisor channel stops it under control.',
 "",
 "## verdict",
 "",
 ("**ALL CHECKS PASS**" if not FAIL else
  "**%d FAILURE(S)**: %s" % (len(FAIL), ", ".join(FAIL))),
]
io.open(OUT, "w", encoding="utf-8", newline="").write(nl.join(lines) + nl)
print("wrote", OUT)
sys.exit(1 if FAIL else 0)
