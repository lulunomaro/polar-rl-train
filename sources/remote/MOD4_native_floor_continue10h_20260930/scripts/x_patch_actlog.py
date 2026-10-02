import io
F=r"D:\claude2\fangzhen\train\verify_skills.py"
src=io.open(F,encoding="utf-8").read()
old = '''    peaks_up = np.zeros(N)
    for k in range(steps):
        env.step(act())'''
new = '''    peaks_up = np.zeros(N)
    # apples-to-apples with the deployment: record the RAW policy actions so the
    # armed-minus-idle action delta can be compared with what the ONNX produces in ROS2.
    act_log = np.zeros((steps, 6), np.float32)
    flag_log = np.zeros(steps, np.float32)
    for k in range(steps):
        a_raw = act()
        act_log[k] = a_raw[0].detach().cpu().numpy() if torch.is_tensor(a_raw) \\
            else np.asarray(a_raw).reshape(N, -1)[0]
        flag_log[k] = float(env._rm_jump_flag[0, 0].item()) if hasattr(env, "_rm_jump_flag") else 0.0
        env.step(a_raw)'''
assert src.count(old)==1
src=src.replace(old,new)
old2='''    print("        tilt at end: median %.1f deg, max %.1f deg"
          % (float(torch.median(tilt).item()), float(tilt.max().item())))'''
new2='''    print("        tilt at end: median %.1f deg, max %.1f deg"
          % (float(torch.median(tilt).item()), float(tilt.max().item())))
    on = flag_log > 0.5
    off = ~on
    if on.sum() > 20 and off.sum() > 20:
        print("        ACTION delta armed-idle (env0, raw policy units):")
        for kk, lb in enumerate(["L_front1", "L_rear1", "L_wheel",
                                 "R_front1", "R_rear1", "R_wheel"]):
            if kk < act_log.shape[1]:
                print("          a[%d] %-9s idle %+7.4f  armed %+7.4f  delta %+7.4f  "
                      "armed span %.4f" % (kk, lb, act_log[off, kk].mean(),
                                           act_log[on, kk].mean(),
                                           act_log[on, kk].mean() - act_log[off, kk].mean(),
                                           act_log[on, kk].max() - act_log[on, kk].min()))
    jump_rows.append(dict(action_delta=[float(act_log[on, i].mean() - act_log[off, i].mean())
                                        for i in range(min(6, act_log.shape[1]))]
                          if (on.sum() > 20 and off.sum() > 20) else None))'''
assert src.count(old2)==1
io.open(F,"w",encoding="utf-8").write(src.replace(old2,new2))
print("action logging added")