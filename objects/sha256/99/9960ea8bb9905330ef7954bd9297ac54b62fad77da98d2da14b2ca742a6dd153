import io
F=r"D:\claude2\fangzhen\train\verify_skills.py"
s=io.open(F,encoding="utf-8").read()
def rep(old,new,cnt=1):
    global s
    assert s.count(old)==cnt,("count %d:"%s.count(old))+old[:60]
    s=s.replace(old,new)
# `env` is the RslRlVecEnvWrapper; the jump buffers live on E.
rep('        flag_log[k] = float(env._rm_jump_flag[0, 0].item()) if hasattr(env, "_rm_jump_flag") else 0.0',
    '        flag_log[k] = float(E._rm_jump_flag[0, 0].item()) if hasattr(E, "_rm_jump_flag") else 0.0')
# do not append a second, malformed row - merge into the real one
rep('''    jump_rows.append(dict(action_delta=[float(act_log[on, i].mean() - act_log[off, i].mean())
                                        for i in range(min(6, act_log.shape[1]))]
                          if (on.sum() > 20 and off.sum() > 20) else None))''',
    '''    if on.sum() > 20 and off.sum() > 20:
        jump_rows[-1]["action_delta"] = [float(act_log[on, i].mean() - act_log[off, i].mean())
                                         for i in range(min(6, act_log.shape[1]))]''')
io.open(F,"w",encoding="utf-8").write(s)
print("actlog fixed")