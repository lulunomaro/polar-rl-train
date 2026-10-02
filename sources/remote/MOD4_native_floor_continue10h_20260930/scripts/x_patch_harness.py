import io
F=r"D:\claude2\fangzhen\scripts\hop_control_law.py"
src=io.open(F,encoding="utf-8").read()
def rep(old,new,cnt=1):
    global src
    assert src.count(old)==cnt,("anchor count %d:"%src.count(old))+old[:70]
    src=src.replace(old,new)

rep("DT = 0.001\n",
    "# mjlab trains with dt = 2 ms and decimation 10 (policy at 50 Hz).  The harness used to\n"
    "# run at 1 ms, which is a different plant for a 0.5 s hop, and it clipped the leg torque\n"
    "# at a flat +-40 N*m.  A real DM-J8009 has a linear torque-speed envelope: the PD setpoint\n"
    "# is unreachable once the rotor approaches no-load speed, so the ceiling must collapse to\n"
    "# zero as |omega| -> vlim.  Without this the legs are far stronger than reality and the\n"
    "# hop diverges, which is why the old harness numbers were unusable.\n"
    "DT = float(os.environ.get(\"RM_HARNESS_DT\", \"0.002\"))\n"
    "LEG_VLIM, WHEEL_VLIM = 17.0, 63.4        # rad/s no-load at 24 V (docs/MOTOR_PARAMS.md)\n"
    "ENVELOPE = os.environ.get(\"RM_HARNESS_ENVELOPE\", \"1\") == \"1\"\n"
    "def cap_for(eff, vlim, omega):\n"
    "    if not ENVELOPE:\n"
    "        return eff\n"
    "    return eff * max(0.0, 1.0 - abs(omega) / vlim)\n")
rep("import sys\nimport numpy as np\n", "import os\nimport sys\nimport numpy as np\n")
rep('''        for nm in LEG:
            d.qfrc_applied[va[nm]] = np.clip(KP * (frozen.get(nm, 0.0) - d.qpos[qa[nm]])
                                             - KD * d.qvel[va[nm]], -LEG_EFF, LEG_EFF)
        for nm in WHL:
            d.qfrc_applied[va[nm]] = np.clip(WKD * (frozen.get(nm, 0.0) - d.qvel[va[nm]]),
                                             -WHEEL_EFF, WHEEL_EFF)''',
    '''        for nm in LEG:
            w = d.qvel[va[nm]]
            c = cap_for(LEG_EFF, LEG_VLIM, w)
            tau = KP * (frozen.get(nm, 0.0) - d.qpos[qa[nm]]) - KD * w
            d.qfrc_applied[va[nm]] = float(np.clip(tau, -c, c))
        for nm in WHL:
            w = d.qvel[va[nm]]
            c = cap_for(WHEEL_EFF, WHEEL_VLIM, w)
            d.qfrc_applied[va[nm]] = float(np.clip(WKD * (frozen.get(nm, 0.0) - w), -c, c))''')
rep('print("policy:", ONNX.split("/")[-1], "| plant: honest dm8009 (40 / 5.5 N*m) | trigger at t=2 s, hold 1.2 s")',
    'print("policy:", ONNX.split("/")[-1],\n'
    '      "| plant: honest dm8009 (40 / 5.5 N*m) | dt=%.4f s | torque-speed envelope=%s"\n'
    '      % (DT, "ON (vlim 17 / 63.4 rad/s)" if ENVELOPE else "OFF"))')
io.open(F,"w",encoding="utf-8").write(src)
print("harness patched")