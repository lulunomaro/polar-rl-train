import io
F=r"D:\claude2\fangzhen\train\verify_skills.py"
src=io.open(F,encoding="utf-8").read()
old = '''    air_secs = np.zeros(N)                          # per-env airborne time [s]
    peaks = np.zeros(N)                             # per-env peak rise [m]
    base0 = robot.data.root_link_pos_w[:, 2].clone()
    alive = torch.ones(N, device=DEV)
    for k in range(steps):
        env.step(act())
        alive *= (~E.termination_manager.terminated).float()      # drop respawned envs
        dz = (robot.data.root_link_pos_w[:, 2] - base0).cpu().numpy()
        dz = np.where(alive.cpu().numpy() > 0, dz, np.nan)
        peaks = np.fmax(peaks, dz)
        air_secs += (1.0 - (E.scene["wheel_contact"].data.found > 0).float()
                     .reshape(N, -1).max(dim=1).values).cpu().numpy() * DT
        if k * DT > a.jump_hold:
            set_jump(0)
    keep = alive.cpu().numpy() > 0
    air = float(np.median(air_secs[keep])) if keep.any() else 0.0
    peak = float(np.nanmedian(peaks[keep])) if keep.any() else 0.0'''
new = '''    air_secs = np.zeros(N)                          # per-env airborne time [s]
    peaks = np.zeros(N)                             # per-env peak rise [m]
    # A two-wheel robot that falls over also loses wheel contact and its root can
    # transiently rise, so "air time" and "peak rise" without an attitude gate measure
    # the TOPPLE, not the hop.  Track uprightness per env and report both metrics.
    UPRIGHT_MAX_DEG = 30.0
    base0 = robot.data.root_link_pos_w[:, 2].clone()
    alive = torch.ones(N, device=DEV)
    upright = torch.ones(N, dtype=torch.bool, device=DEV)
    air_secs_up = np.zeros(N)
    peaks_up = np.zeros(N)
    for k in range(steps):
        env.step(act())
        alive *= (~E.termination_manager.terminated).float()      # drop respawned envs
        dz = (robot.data.root_link_pos_w[:, 2] - base0).cpu().numpy()
        dz = np.where(alive.cpu().numpy() > 0, dz, np.nan)
        peaks = np.fmax(peaks, dz)
        airborne = (1.0 - (E.scene["wheel_contact"].data.found > 0).float()
                    .reshape(N, -1).max(dim=1).values).cpu().numpy()
        air_secs += airborne * DT
        g = robot.data.projected_gravity_b
        tilt = torch.rad2deg(torch.acos(g[:, 2].clamp(-1.0, 1.0)))
        upright &= (tilt < UPRIGHT_MAX_DEG)
        up = (upright & (alive > 0)).cpu().numpy()
        peaks_up = np.fmax(peaks_up, np.where(up, dz, 0.0))
        air_secs_up += airborne * up.astype(float) * DT
        if k * DT > a.jump_hold:
            set_jump(0)
    keep = alive.cpu().numpy() > 0
    kup = upright.cpu().numpy() & keep
    n_up = int(kup.sum())
    air = float(np.median(air_secs_up[kup])) if n_up else 0.0
    peak = float(np.median(peaks_up[kup])) if n_up else 0.0
    peak_naive = float(np.nanmedian(peaks[keep])) if keep.any() else 0.0
    air_naive = float(np.median(air_secs[keep])) if keep.any() else 0.0'''
assert src.count(old)==1, src.count(old)
src = src.replace(old, new)
old2 = '''    r, p = roll_pitch()
    alive = float((~E.termination_manager.terminated).float().mean().item())
    jump_rows.append(dict(target=rise, peak=peak, air_time=air, delay=delay,
                          roll=r, pitch=p, alive=alive))
    print("      %.2f m   |  %.3f m  |  %5.2f s |     %5.2f s    |  roll %4.1f pitch %4.1f | %3.0f%%"
          % (rise, peak, air, delay if delay is not None else -1, r, p, 100 * alive))'''
new2 = '''    r, p = roll_pitch()
    alive = float((~E.termination_manager.terminated).float().mean().item())
    jump_rows.append(dict(target=rise, peak=peak, air_time=air, delay=delay,
                          roll=r, pitch=p, alive=alive,
                          peak_upright=peak, air_upright=air,
                          upright_envs=n_up, upright_frac=(n_up / max(1, N)),
                          peak_topple_inflated=peak_naive, air_topple_inflated=air_naive))
    print("      %.2f m   |  %.3f m  |  %5.2f s |     %5.2f s    |  roll %4.1f pitch %4.1f | %3.0f%%"
          % (rise, peak, air, delay if delay is not None else -1, r, p, 100 * alive))
    print("        UPRIGHT-GATED (<%.0f deg): %d/%d envs stayed upright ->"
          " peak rise %.3f m, airborne %.2f s   [ungated: %.3f m / %.2f s]"
          % (UPRIGHT_MAX_DEG, n_up, N, peak, air, peak_naive, air_naive))'''
assert src.count(old2)==1, src.count(old2)
io.open(F,"w",encoding="utf-8").write(src.replace(old2,new2))
print("verify_skills jump metric hardened")