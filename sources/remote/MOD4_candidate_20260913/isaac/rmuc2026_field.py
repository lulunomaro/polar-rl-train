
# RMUC2026 7v7 field, built for Isaac Lab out of the SAME measured numbers the mjlab
# curriculum uses (cad/out_map/field_dims.json, extracted from RMUC2026_V2.0.0.stp by
# scripts/map_field_dims.py).  One source of truth for both engines.
#
# MuJoCo/mjlab side: train/rmvehicle/src/rmvehicle/field_cfg.py -> 7 terrain columns
# (flat arena / ramp up / ramp down / stairs up / stairs down / barricades / bumps),
# height-limited by the measured leg stroke (RM_TERRAIN_CAP_H, default 0.20 m).
# This module reproduces the discrete features (arena, ramps, stairs, barricades) as
# cuboids, because Isaac previews want explicit geometry you can see and walk up.
import json, math, os
from isaaclab.assets import AssetBaseCfg
import isaaclab.sim as sim_utils

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
DIMS = os.path.join(ROOT, 'cad', 'out_map', 'field_dims.json')
DEFAULTS = dict(field_size_m=[29.75, 16.0], slope_deg=[9.4, 25.0], step_height_m=[0.02, 0.22],
                step_run_m=[0.15, 1.084], obstacle_height_m=[0.074, 0.416],
                obstacle_width_m=[0.2, 1.088], roughness_m=0.02, slope_median_deg=12.1)


def dims():
    d = dict(DEFAULTS)
    if os.path.isfile(DIMS):
        d.update(json.load(open(DIMS, encoding='utf-8')))
    return d


def box(name, size, pos, tilt_deg=0.0, color=(0.42, 0.46, 0.52)):
    """A static cuboid collider.  tilt_deg rotates it about +Y (negative = rising toward +x)."""
    q = (math.cos(math.radians(tilt_deg) / 2.0), 0.0,
         -math.sin(math.radians(tilt_deg) / 2.0), 0.0)
    return name, AssetBaseCfg(
        prim_path='/World/Field/' + name,
        init_state=AssetBaseCfg.InitialStateCfg(pos=tuple(float(v) for v in pos), rot=tuple(q)),
        spawn=sim_utils.CuboidCfg(
            size=(float(size[0]), float(size[1]), float(size[2])),
            collision_props=sim_utils.CollisionPropertiesCfg(collision_enabled=True,
                                                             contact_offset=0.001, rest_offset=0.0),
            visual_material=sim_utils.PreviewSurfaceCfg(diffuse_color=color, roughness=0.9),
            physics_material=sim_utils.RigidBodyMaterialCfg(static_friction=1.4, dynamic_friction=1.0),
        ),
    )


def rmuc2026_field(cap_h=0.20, x_start=4.0, width=6.0):
    """Returns {prim_name: AssetBaseCfg}.  x_start is where the features begin, so the robots
    get a clear runway on the flat arena."""
    d = dims()
    fx, fy = d['field_size_m']
    s_med = float(d.get('slope_median_deg', 12.1))
    s_max = float(d['slope_deg'][1])
    h_step = min(float(d['step_height_m'][1]), cap_h)
    run = min(max(float(d['step_run_m'][0]), 0.28), 0.45)
    o_cap = min(float(d['obstacle_height_m'][1]), cap_h)
    o_wall = float(d['obstacle_height_m'][1])
    out = {}
    x = x_start
    # stairs up: the map's tallest climbable step, repeated
    n = 5
    for i in range(n):
        out['stair_%d' % i] = box(('stair_%d' % i), (run, width, (i + 1) * h_step),
                                  (x + i * run, 0.0, (i + 1) * h_step / 2.0), color=(0.48, 0.53, 0.60))
    x += n * run + 1.2
    top = n * h_step
    # ramp down from the stair top, at the measured median slope
    L = top / math.tan(math.radians(s_med)) if s_med > 0 else 2.0
    out['ramp_down'] = box('ramp_down', (math.hypot(L, top), width, 0.06),
                           (x + L / 2.0, 0.0, top / 2.0), tilt_deg=s_med, color=(0.50, 0.55, 0.62))
    x += L + 1.2
    # ramp up at the map's steepest measured slope, 1.2 m high
    H = 1.2
    L2 = H / math.tan(math.radians(s_max))
    out['ramp_up'] = box('ramp_up', (math.hypot(L2, H), width, 0.06),
                         (x + L2 / 2.0, 0.0, H / 2.0), tilt_deg=-s_max, color=(0.50, 0.55, 0.62))
    x += L2 + 0.6
    out['highland'] = box('highland', (2.0, width, H), (x + 1.0, 0.0, H / 2.0), color=(0.55, 0.60, 0.66))
    x += 2.6
    x_end = x + 3.0
    # barricades: climbable height, then the real 0.416 m wall the chassis cannot clear
    for k, (hh, col) in enumerate(((o_cap, (0.62, 0.50, 0.42)), (o_wall, (0.66, 0.42, 0.36)))):
        out['barricade_%d' % k] = box('barricade_%d' % k, (0.20, width, hh),
                                      (x + k * 1.4, 0.0, hh / 2.0), color=col)
    x_end = x + 2.0
    # arena last, sized to actually cover the robot grid (x_start is >= 0 but the env grid is
    # centred on 0, so a field that starts at -2 left the robots spawning over a hole - that is
    # exactly why they free-falled through the map in the first test).
    x0 = min(-10.0, -x_start)
    x1 = max(float(fx), x_end + 4.0)
    out['arena'] = box('arena', (x1 - x0, fy, 0.05), ((x0 + x1) / 2.0, 0.0, -0.025),
                       color=(0.30, 0.33, 0.38))
    info = dict(arena_x=[round(x0, 1), round(x1, 1)], slope_median=s_med, slope_max=s_max,
                step=h_step, run=run, barricade_climb=o_cap, barricade_wall=o_wall,
                features=len(out))
    return out, info


def box_per_env(name, size, pos, tilt_deg=0.0, color=(0.42, 0.46, 0.52)):
    """Same as box(), but parented to {ENV_REGEX_NS} so EVERY environment gets its own copy of
    the measured feature at its own origin (that is how a map has to enter RL training:
    1024-2048 envs cannot share one global layout)."""
    q = (math.cos(math.radians(tilt_deg) / 2.0), 0.0, -math.sin(math.radians(tilt_deg) / 2.0), 0.0)
    return name, AssetBaseCfg(
        prim_path='{ENV_REGEX_NS}/Field_' + name,
        init_state=AssetBaseCfg.InitialStateCfg(pos=tuple(float(v) for v in pos), rot=tuple(q)),
        spawn=sim_utils.CuboidCfg(
            size=(float(size[0]), float(size[1]), float(size[2])),
            collision_props=sim_utils.CollisionPropertiesCfg(collision_enabled=True,
                                                             contact_offset=0.001, rest_offset=0.0),
            visual_material=sim_utils.PreviewSurfaceCfg(diffuse_color=color, roughness=0.9),
            # NO per-box physics_material: Isaac/PhysX caps the process at 64K materials and
            # one material per (environment, feature) blows past it at ~4k environments
            # ("PxPhysics::createMaterial: limit of 64K materials reached", measured
            # 2026-09-10 with 14 features x 4096 envs).  The field therefore uses the scene's
            # single default material; the wheel/ground friction randomization lives on the
            # robot's own material and is unaffected.
        ),
    )


def rmuc2026_field_per_env(cap_h=None, clear_x=1.1):
    """Per-env slice of the measured RMUC2026 map: a runway, then the tallest climbable step,
    then the steepest measured ramp, then the 0.416 m barricade the chassis cannot clear.
    Returns ({name: cfg}, info).  Requires env_spacing >= about 5 m."""
    d = dims()
    if cap_h is None:
        cap_h = float(os.environ.get('RM_TERRAIN_CAP_H', '0.20'))
    s_med = float(d.get('slope_median_deg', 12.1))
    s_max = float(d['slope_deg'][1])
    h = min(float(d['step_height_m'][1]), cap_h)
    run = min(max(float(d['step_run_m'][0]), 0.28), 0.45)
    o_wall_real = float(d['obstacle_height_m'][1])
    o_wall = min(o_wall_real, cap_h)
    W = 1.6
    x = clear_x
    out = {}
    # Two-level up/down stairs reach the measured climb cap without presenting an impossible
    # vertical wall to a policy that is only beginning its terrain curriculum.
    stair_start = x
    for i in range(2):
        hh = h * (i + 1) / 2.0
        name = 'stair_up_%d' % (i + 1)
        out[name] = box_per_env(name, (run, W, hh), (x + run / 2.0, 0.0, hh / 2.0),
                                color=(0.48, 0.53, 0.60))
        x += run
    for i in range(2):
        hh = h * (2 - i) / 2.0
        name = 'stair_down_%d' % (i + 1)
        out[name] = box_per_env(name, (run, W, hh), (x + run / 2.0, 0.0, hh / 2.0),
                                color=(0.44, 0.49, 0.57))
        x += run
    x += 0.35
    H = 2.0 * h
    L = H / math.tan(math.radians(s_max))
    ramp_max_center = x + L / 2.0
    out['ramp_max'] = box_per_env('ramp_max', (math.hypot(L, H), W, 0.05),
                                  (ramp_max_center, 0.0, H / 2.0), tilt_deg=-s_max,
                                  color=(0.50, 0.55, 0.62))
    x += L + 0.35
    L2 = H / math.tan(math.radians(s_med))
    ramp_med_center = x + L2 / 2.0
    out['ramp_med'] = box_per_env('ramp_med', (math.hypot(L2, H), W, 0.05),
                                  (ramp_med_center, 0.0, H / 2.0), tilt_deg=s_med,
                                  color=(0.50, 0.55, 0.62))
    x += L2 + 0.30
    out['barricade'] = box_per_env('barricade', (0.20, W, o_wall), (x, 0.0, o_wall / 2.0),
                                   color=(0.66, 0.42, 0.36))

    # Raised split runway: the global arena remains the bottom of a 0.18 m-deep gap, while
    # the two slabs form its banks.  The gap width is curriculum-safe for the 0.146 m wheels.
    gap_y, gap_h, gap_x0, gap_x1 = 2.45, min(0.18, h), 0.55, 0.92
    out['gap_bank_before'] = box_per_env(
        'gap_bank_before', (2.0, 1.35, gap_h), (-0.45, gap_y, gap_h / 2.0),
        color=(0.40, 0.45, 0.52))
    out['gap_bank_after'] = box_per_env(
        'gap_bank_after', (3.0, 1.35, gap_h), (gap_x1 + 1.50, gap_y, gap_h / 2.0),
        color=(0.40, 0.45, 0.52))

    # Launch-ramp lane: climb a measured-slope wedge and cross a short same-height air gap.
    launch_y, launch_h, launch_deg = -2.45, min(0.22, h), min(20.0, s_max)
    launch_x = 0.65
    launch_L = launch_h / math.tan(math.radians(launch_deg))
    out['launch_ramp'] = box_per_env(
        'launch_ramp', (math.hypot(launch_L, launch_h), 1.35, 0.05),
        (launch_x + launch_L / 2.0, launch_y, launch_h / 2.0),
        tilt_deg=-launch_deg, color=(0.55, 0.48, 0.38))
    landing_x = launch_x + launch_L + 0.34
    out['launch_landing'] = box_per_env(
        'launch_landing', (2.4, 1.35, launch_h),
        (landing_x + 1.20, launch_y, launch_h / 2.0), color=(0.50, 0.45, 0.38))

    # --- 250 mm tunnel (the user's measured opening) -------------------------------------
    # 250 mm high x 800 mm wide x 300 mm deep, exactly the numbers in the mjlab curriculum
    # (train/rmvehicle/src/rmvehicle/field_cfg.py, TunnelWallTerrainCfg).  Three static
    # cuboids: two side walls and a 1.2 m top beam, so going over is not an option and the
    # only way through is to crouch.  The robot's lowest commanded envelope is ~273 mm of
    # CAD but only ~235 mm of simulated collision geometry, which is why this feature is
    # trainable in simulation and still needs the real clearance checked on hardware.
    tun_y = 3.55
    tun_x = clear_x + 1.35
    hole_w, depth, hole_h, tot_w, wall_h = 0.80, 0.30, 0.25, 1.60, 1.20
    side_w = (tot_w - hole_w) / 2.0
    out['tunnel_wall_left'] = box_per_env(
        'tunnel_wall_left', (depth, side_w, wall_h),
        (tun_x, tun_y + hole_w / 2.0 + side_w / 2.0, wall_h / 2.0), color=(0.85, 0.35, 0.25))
    out['tunnel_wall_right'] = box_per_env(
        'tunnel_wall_right', (depth, side_w, wall_h),
        (tun_x, tun_y - hole_w / 2.0 - side_w / 2.0, wall_h / 2.0), color=(0.85, 0.35, 0.25))
    out['tunnel_beam'] = box_per_env(
        'tunnel_beam', (depth, tot_w, wall_h - hole_h),
        (tun_x, tun_y, hole_h + (wall_h - hole_h) / 2.0), color=(0.85, 0.35, 0.25))

    # --- P1 (audit 2026-09-11): the features the training map was missing ----------------
    # (a) the REAL 0.416 m barricade, not the 0.20 m cap: the audit flagged that the CAD
    #     obstacle was silently truncated to the climb cap.
    out['barricade_wall'] = box_per_env(
        'barricade_wall', (0.24, W, o_wall_real), (x + 0.55, 0.0, o_wall_real / 2.0),
        color=(0.72, 0.30, 0.24))
    # (b) two-level centre island with a lip on the upper deck (完整二级中心岛 + 顶面挡圈).
    island_x = x + 1.35
    island_len, island_w = 1.30, 1.20
    lvl1, lvl2, lip_h, lip_t = 0.18, 0.36, 0.05, 0.05
    out['island_level1'] = box_per_env(
        'island_level1', (island_len, island_w, lvl1), (island_x, 0.0, lvl1 / 2.0),
        color=(0.45, 0.55, 0.62))
    out['island_level2'] = box_per_env(
        'island_level2', (island_len * 0.7, island_w * 0.7, lvl2 - lvl1),
        (island_x, 0.0, lvl1 + (lvl2 - lvl1) / 2.0), color=(0.40, 0.50, 0.58))
    for k, (dy, dx, sy, sx) in enumerate(((+1, 0, 1, 0), (-1, 0, 1, 0),
                                          (0, +1, 0, 1), (0, -1, 0, 1))):
        out['island_lip_%d' % k] = box_per_env(
            'island_lip_%d' % k,
            ((island_len * 0.7) if sy else lip_t, (island_w * 0.7) if sx else lip_t, lip_h),
            (island_x + dx * island_len * 0.35, dy * island_w * 0.35, lvl1 + (lvl2 - lvl1) + lip_h / 2.0),
            color=(0.55, 0.42, 0.30))
    # (c) undulating section: 8 shallow bumps (0.02-0.06 m) the wheels must roll over.
    und_x0 = island_x + island_len / 2.0 + 0.35
    bumps = 8
    for k in range(bumps):
        hh = 0.02 + 0.04 * ((k % 3) / 2.0)
        out['undulation_%d' % k] = box_per_env(
            'undulation_%d' % k, (0.30, W * 0.8, hh),
            (und_x0 + k * 0.34, 0.0, hh / 2.0), color=(0.52, 0.56, 0.60))
    und_x1 = und_x0 + bumps * 0.34
    info = dict(per_env=True, step=h, ramp_max_deg=s_max, ramp_med_deg=s_med,
                barricade=o_wall, barricade_real=o_wall_real, span_x=round(x + 0.6, 2),
                # P1 semantic coordinates for the new features (audit: 入口/出口/起跳/落地)
                barricade_wall_x=round(x + 0.55, 2),
                island_entry=round(island_x - island_len / 2.0, 2),
                island_exit=round(island_x + island_len / 2.0, 2),
                island_level1_m=lvl1, island_level2_m=lvl2, island_lip_m=lip_h,
                undulation_entry=round(und_x0, 2),
                undulation_exit=round(und_x1, 2),
                stair_spawn=(-0.25, 0.0, 0.0),
                stair_takeoff=stair_start - 0.20,
                gap_spawn=(-0.72, gap_y, gap_h), gap_trigger=(0.05, gap_x1),
                gap_curriculum_spawn=(0.18, gap_y, gap_h),
                gap_takeoff=gap_x0 - 0.07,
                gap_success=gap_x1 + 0.28,
                launch_spawn=(-0.25, launch_y, 0.0),
                launch_trigger=(launch_x - 0.35, launch_x + launch_L),
                launch_takeoff=launch_x + launch_L - 0.18,
                launch_success=landing_x + 0.28,
                tunnel_spawn=(-0.70, tun_y, 0.0),
                tunnel_center=tun_x,
                tunnel_entry=tun_x - depth / 2.0,
                tunnel_exit=tun_x + depth / 2.0,
                tunnel_success=tun_x + 0.90,
                tunnel_hole_m=(hole_h, hole_w, depth),
                ramp_max_spawn=(ramp_max_center, 0.0, H / 2.0),
                ramp_med_spawn=(ramp_med_center, 0.0, H / 2.0),
                stair_start=stair_start,
                features=len(out))
    return out, info
