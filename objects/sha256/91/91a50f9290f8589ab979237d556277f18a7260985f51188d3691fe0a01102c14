import io
F=r"D:\claude2\fangzhen\train\verify_skills.py"
src=io.open(F,encoding="utf-8").read()
def rep(old,new,cnt=1):
    global src
    assert src.count(old)==cnt,("anchor count %d:"%src.count(old))+old[:70]
    src=src.replace(old,new)
# projected_gravity_b is R^T @ (0,0,-1): upright => g_z = -1, so tilt = acos(-g_z).
rep("        tilt = torch.rad2deg(torch.acos(g[:, 2].clamp(-1.0, 1.0)))",
    "        tilt = torch.rad2deg(torch.acos((-g[:, 2]).clamp(-1.0, 1.0)))")
rep('''    print("        UPRIGHT-GATED (<%.0f deg): %d/%d envs stayed upright ->"
          " peak rise %.3f m, airborne %.2f s   [ungated: %.3f m / %.2f s]"
          % (UPRIGHT_MAX_DEG, n_up, N, peak, air, peak_naive, air_naive))''',
    '''    print("        UPRIGHT-GATED (<%.0f deg): %d/%d envs stayed upright ->"
          " peak rise %.3f m, airborne %.2f s   [ungated: %.3f m / %.2f s]"
          % (UPRIGHT_MAX_DEG, n_up, N, peak, air, peak_naive, air_naive))
    print("        tilt at end: median %.1f deg, max %.1f deg"
          % (float(torch.median(tilt).item()), float(tilt.max().item())))''')
# allow running just one skill so re-verification is cheap
rep("ap.add_argument(\"--jump-hold\", type=float, default=1.6)",
    "ap.add_argument(\"--jump-hold\", type=float, default=1.6)\n"
    "ap.add_argument(\"--only\", default=\"all\",\n"
    "                help=\"run|gyro|jump|all -- skip the other sections\")")
io.open(F,"w",encoding="utf-8").write(src)
print("tilt gate fixed")