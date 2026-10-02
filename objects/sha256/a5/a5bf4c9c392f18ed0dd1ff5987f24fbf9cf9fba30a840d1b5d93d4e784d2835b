import io
F=r"D:\claude2\fangzhen\sim_mujoco\onnx_play.py"
s=io.open(F,encoding="utf-8").read()
def rep(old,new,cnt=1):
    global s
    assert s.count(old)==cnt,("count %d:"%s.count(old))+old[:60]
    s=s.replace(old,new)
rep("        lo, hi = (EFFECT_LEG if leg else EFFECT_WHEEL)",
    "        # the ceiling is read from the plant itself so this can never drift from the MJCF\n"
    "        eff = FORCE_RANGE.get(jn, EFFECT_LEG if leg else EFFECT_WHEEL)\n"
    "        lo, hi = -eff, eff")
rep("EFFECT_LEG, EFFECT_WHEEL = 50.9, 10.0",
    "EFFECT_LEG, EFFECT_WHEEL = 50.9, 10.0   # legacy fallback only\n"
    "FORCE_RANGE = {}                        # joint name -> |forcerange| from the MJCF")
rep("m.opt.timestep = args.dt",
    "m.opt.timestep = args.dt\n"
    "for _i in range(m.nu):\n"
    "    _jn = mujoco.mj_id2name(m, mujoco.mjtObj.mjOBJ_JOINT, m.actuator_trnid[_i, 0])\n"
    "    if _jn:\n"
    "        FORCE_RANGE[_jn] = float(m.actuator_forcerange[_i, 1])")
io.open(F,"w",encoding="utf-8").write(s)
print("onnx_play fixed")