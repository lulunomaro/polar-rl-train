
# Isaac Lab preview: N copies of the RL plant (closed-chain MJCF -> USD), held at the analytic stance.
#
#   headless + numbers:   ..\\.venv-isaaclab\Scripts\python.exe isaac/preview_robots.py --num_envs 16 --steps 600
#   the live window:      ..\\.venv-isaaclab\Scripts\python.exe isaac/preview_robots.py --num_envs 24 --viz kit
#
# --viz kit opens the Isaac Sim viewport with all robots side by side (that is the "many robots training" view).
import argparse, json, os, sys
ROOT = r'D:/claude2/fangzhen'
DEFUSD = os.path.join(ROOT, 'isaac', 'assets', 'rm_vehicle_cc', 'rm_vehicle_cc.usda')
ap = argparse.ArgumentParser(description='Isaac Lab multi-robot preview of the wheel-leg plant')
ap.add_argument('--usd', default=DEFUSD)
ap.add_argument('--num_envs', type=int, default=16)
ap.add_argument('--spacing', type=float, default=1.7)
ap.add_argument('--steps', type=int, default=600)
ap.add_argument('--pose', type=int, default=1, help='index into docs/viz/model.json poses')
ap.add_argument('--png', default=None)
ap.add_argument('--hold', action='store_true')
ap.add_argument('--kp', type=float, default=60.0)
ap.add_argument('--kd', type=float, default=2.0)
ap.add_argument('--spring-k', dest='sk', type=float, default=6000.0)
ap.add_argument('--spring-ref', dest='sref', type=float, default=0.0583333)
ap.add_argument('--spawn-z', dest='sz', type=float, default=0.0531)
ap.add_argument('--balance', type=float, default=1.0, help='1 = wheel-balance (Segway) PD so the preview stands still, 0 = pure joint hold')
ap.add_argument('--bp', type=float, default=3.2)
ap.add_argument('--br', type=float, default=1.3)
ap.add_argument('--kvx', type=float, default=1.0)
ap.add_argument('--kx', type=float, default=0.35)
ap.add_argument('--bpi', type=float, default=1.2, help='pitch integral gain')
ap.add_argument('--keep-ground', dest='keep_ground', action='store_true',
                help='debug: also keep the generic 60x60 slab under the field')
ap.add_argument('--field', action='store_true',
                help='build the RMUC2026 7v7 field (arena + stairs + ramps + barricades) from cad/out_map/field_dims.json')
ap.add_argument('--env-x0', dest='ex0', type=float, default=0.0, help='shift the robot grid along x (use -6 with --field)')
ap.add_argument('--serial', action='store_true',
                help='the USD is the PhysX-friendly serial surrogate (no couplers/spring): only rear1, rear2, wheel exist)')
ap.add_argument('--knee-kp', dest='kpk', type=float, default=0.0, help='stiffness for rear2 (the surrogate knee); 0 keeps it passive like the real closed chain')
ap.add_argument('--knee-kd', dest='kpd', type=float, default=30.0)
ap.add_argument('--spring-mode', dest='smode', default='ref', choices=['ref', 'pose'],
                help='ref = reproduce the 350 N gas-spring pre-load (physics-true); pose = hold the spawn length (calm)')
ap.add_argument('--dt', type=float, default=0.001)
ap.add_argument('--iters', type=int, default=16, help='PhysX position iterations (the closed chain needs more than the default)')
mine, _unknown = ap.parse_known_args()
from isaaclab.app import AppLauncher
_pl = argparse.ArgumentParser()
AppLauncher.add_app_launcher_args(_pl)
args_cli, _ = _pl.parse_known_args()
_app = AppLauncher(args_cli)
simulation_app = _app.app
import torch
import isaaclab.sim as sim_utils
from isaaclab.actuators import ImplicitActuatorCfg
from isaaclab.assets import ArticulationCfg, AssetBaseCfg
from isaaclab.scene import InteractiveScene, InteractiveSceneCfg
from isaaclab.sim import SimulationContext
from isaaclab.utils.configclass import configclass
POSE = json.load(open(os.path.join(ROOT, 'docs', 'viz', 'model.json'), encoding='utf-8'))['poses'][mine.pose]
QPOS = {k: float(v) for k, v in POSE['q'].items() if k != '__root__'}


@configclass
class PreviewSceneCfg(InteractiveSceneCfg):
    ground = AssetBaseCfg(
        prim_path='/World/Ground',
        init_state=AssetBaseCfg.InitialStateCfg(pos=(0.0, 0.0, -0.05)),
        spawn=sim_utils.CuboidCfg(
            size=(60.0, 60.0, 0.1),
            collision_props=sim_utils.CollisionPropertiesCfg(collision_enabled=True),
            visual_material=sim_utils.PreviewSurfaceCfg(diffuse_color=(0.30, 0.33, 0.38), roughness=0.85),
            physics_material=sim_utils.RigidBodyMaterialCfg(static_friction=1.4, dynamic_friction=1.0),
        ),
    )
    light = AssetBaseCfg(prim_path='/World/Light',
                         spawn=sim_utils.DistantLightCfg(intensity=3800.0, color=(0.9, 0.9, 0.92)))
    robot = ArticulationCfg(
        prim_path='{ENV_REGEX_NS}/Robot',
        spawn=sim_utils.UsdFileCfg(
            usd_path=mine.usd, activate_contact_sensors=True,
            # the MJCF importer writes contactGap=0 -> PhysX only makes contact after ~2 cm of
            # penetration, which is what made the robots sink and lean back. Give it a real margin.
            collision_props=sim_utils.CollisionPropertiesCfg(collision_enabled=True,
                                                              contact_offset=0.02, rest_offset=0.0),
            # PhysX default is 4 position iterations for the whole articulation; this robot is a
            # 20 kg frame on two 26 mm-wide tyre contacts, so the wheels sank 5 cm into the floor.
            articulation_props=sim_utils.ArticulationRootPropertiesCfg(
                enabled_self_collisions=False,
                solver_position_iteration_count=mine.iters,
                solver_velocity_iteration_count=2),
            rigid_props=sim_utils.RigidBodyPropertiesCfg(
                disable_gravity=False, max_depenetration_velocity=1.0,
                linear_damping=0.0, angular_damping=0.0),
        ),
        init_state=ArticulationCfg.InitialStateCfg(pos=(0.0, 0.0, mine.sz), joint_pos=QPOS, joint_vel={'.*': 0.0}),
    )


def main():
    from isaaclab_physx.physics import PhysxCfg
    sim = SimulationContext(sim_utils.SimulationCfg(
        device=args_cli.device, dt=mine.dt,
        physics=PhysxCfg(solver_type=1, enable_external_forces_every_iteration=True)))
    sim.set_camera_view([4.0, -12.0, 3.4], [4.0, 0.0, 0.15] if mine.field else [0.0, 0.0, 0.25])
    cfg = PreviewSceneCfg(num_envs=mine.num_envs, env_spacing=mine.spacing)
    acts = {
        'hips': ImplicitActuatorCfg(joint_names_expr=(['.*rear1.*'] if mine.serial else ['.*rear1.*', '.*front1.*']),
                                    stiffness=mine.kp, damping=mine.kd,
                                    effort_limit_sim=40.0, velocity_limit_sim=17.0),
        'wheels': ImplicitActuatorCfg(joint_names_expr=['.*wheel.*'],
                                      stiffness=0.0, damping=3.0,
                                      effort_limit_sim=5.5, velocity_limit_sim=63.4),
        'knees': ImplicitActuatorCfg(joint_names_expr=['.*rear2.*'],
                                     stiffness=mine.kpk, damping=mine.kpd, effort_limit_sim=40.0),
    }
    jp = dict(QPOS)
    if mine.serial:
        # the surrogate has no crank / coupler / gas-spring bodies: drop those patterns so the
        # initialiser never asks for a joint that does not exist in this USD.
        jp = {k: v for k, v in QPOS.items() if ('rear1' in k or 'rear2' in k or 'wheel' in k)}
        acts.pop('spring', None)
    else:
        acts['spring'] = ImplicitActuatorCfg(joint_names_expr=['.*spring2.*'], stiffness=mine.sk,
                                            damping=150.0, effort_limit_sim=5000.0)
        acts['links'] = ImplicitActuatorCfg(joint_names_expr=['.*front2.*', '.*front3.*', '.*front4.*', '.*spring1.*'],
                                            stiffness=0.0, damping=0.05, effort_limit_sim=1000.0)
    cfg.robot.actuators = acts
    FIELD_INFO = None
    if mine.field:
        sys.path.insert(0, os.path.join(ROOT, 'isaac'))
        from rmuc2026_field import rmuc2026_field
        feats, FIELD_INFO = rmuc2026_field()
        if mine.keep_ground:
            pass
        else:
            cfg.ground = None        # the arena floor replaces the generic 60x60 slab
        for nm, acfg in feats.values():
            setattr(cfg, nm, acfg)
    cfg.robot.init_state.joint_pos = jp
    scene = InteractiveScene(cfg)
    if FIELD_INFO:
        print('[preview] RMUC2026 field:', FIELD_INFO, flush=True)
        try:
            import omni.usd
            from pxr import Usd, UsdPhysics, UsdGeom
            st = omni.usd.get_context().get_stage()
            root = st.GetPrimAtPath('/World/Field')
            kids = list(root.GetChildren()) if root.IsValid() else []
            print('[preview] /World/Field valid=%s children=%d %s' % (
                root.IsValid(), len(kids), [str(k.GetName()) for k in kids][:12]), flush=True)
            def walk(pr, depth=0):
                if depth > 3:
                    return
                tr = UsdGeom.Xformable(pr).ComputeLocalToWorldTransform(Usd.TimeCode.Default()).ExtractTranslation()
                print('     %s%-22s type=%-12s collide=%s size=%s' % (
                    '  ' * depth, str(pr.GetPath()).split('/')[-1], pr.GetTypeName(),
                    pr.HasAPI(UsdPhysics.CollisionAPI),
                    [round(float(v), 3) for v in tr]), flush=True)
                for c in pr.GetChildren():
                    walk(c, depth + 1)
            for k in kids[:2]:
                walk(k)
            g = st.GetPrimAtPath('/World/Ground')
            if g.IsValid():
                print('   --- generic ground ---', flush=True)
                walk(g)
        except Exception as ex:
            print('[preview] field diag failed:', type(ex).__name__, ex, flush=True)
    sim.reset()
    robot = scene['robot']
    print('[preview] %d robots x %d joints' % (mine.num_envs, robot.num_joints), flush=True)
    print('[preview] joints:', list(robot.data.joint_names), flush=True)
    # Build the target straight from the analytic closed-chain pose (never trust the
    # USD rest pose / init_state resolution), then force the state into the sim once.
    names = list(robot.data.joint_names)
    tgt = torch.zeros(1, len(names), device=sim.device)
    for i, n in enumerate(names):
        tgt[0, i] = QPOS.get(n, mine.sref if ('spring2' in n and mine.smode == 'ref') else 0.0)
    tgt = tgt.repeat(mine.num_envs, 1)
    root_pose = robot.data.default_root_pose.torch.clone()
    root_pose[:, :3] += scene.env_origins
    root_pose[:, 0] += mine.ex0
    root_pose[:, 2] = mine.sz
    robot.write_root_pose_to_sim_index(root_pose=root_pose)
    robot.write_root_velocity_to_sim_index(root_velocity=torch.zeros(mine.num_envs, 6, device=sim.device))
    robot.write_joint_position_to_sim_index(position=tgt)
    robot.write_joint_velocity_to_sim_index(velocity=torch.zeros_like(tgt))
    scene.write_data_to_sim()
    sim.forward()
    scene.update(sim.get_physics_dt())
    z0 = robot.data.root_pos_w.torch[:, 2]
    q0 = robot.data.joint_pos.torch
    print('[preview] forced spawn state: base z %.4f..%.4f, max |q-pose| %.4f rad' % (
        z0.min().item(), z0.max().item(), (q0 - tgt).abs().max().item()), flush=True)
    # (spring pre-load already handled while building tgt above)
    setter = getattr(robot, 'set_joint_position_target_index', None) or robot.set_joint_position_target
    sl = slice(None)
    from isaaclab.utils.math import quat_rotate_inverse
    WID = [i for i, n in enumerate(names) if 'wheel' in n]
    BNAMES = list(robot.data.body_names)
    WBODY = [i for i, n in enumerate(BNAMES) if 'wheel' in n]
    LID = [i for i in range(len(names)) if i not in WID]
    GDOWN = torch.tensor([0.0, 0.0, -1.0], device=sim.device).repeat(mine.num_envs, 1)
    x0 = scene.env_origins.clone()
    x0[:, 0] += mine.ex0
    sim_dt = sim.get_physics_dt()

    PIT = torch.zeros(mine.num_envs, device=sim.device)

    def balance():
        # gravity in the body frame: leaning forward makes its x-component positive
        nonlocal PIT
        g = quat_rotate_inverse(robot.data.root_state_w.torch[:, 3:7], GDOWN)
        pitch = torch.atan2(g[:, 0], -g[:, 2])
        PIT = torch.clamp(PIT + pitch * sim_dt, -1.2, 1.2)
        rate = robot.data.root_ang_vel_w.torch[:, 1]
        vx = robot.data.root_lin_vel_w.torch[:, 0]
        dx = robot.data.root_pos_w.torch[:, 0] - x0[:, 0]
        vref = mine.bp * pitch + mine.br * rate + mine.bpi * PIT - mine.kvx * vx - mine.kx * dx
        robot.set_joint_velocity_target_index(target=(vref / 0.073).unsqueeze(-1).repeat(1, len(WID)),
                                             joint_ids=WID)
    if mine.balance:
        for k in range(mine.steps):
            balance()
            tl = tgt[:, LID]
            setter(target=tl, joint_ids=LID) if setter.__name__.endswith('_index') else setter(tl, LID)
            scene.write_data_to_sim()
            sim.step()
            scene.update(sim_dt)
            if k % 100 == 0:
                z = robot.data.root_pos_w.torch[:, 2]
                g = quat_rotate_inverse(robot.data.root_state_w.torch[:, 3:7], GDOWN)
                wz = robot.data.body_pos_w.torch[:, WBODY, 2]
                print('  step %4d  base z %.4f..%.4f | wheel z %.4f | standing %d/%d | pitch %+.1f..%+.1f deg | vx %+.2f m/s' % (
                    k, z.min().item(), z.max().item(), float(wz.mean().item()),
                    int((z > 0.043).sum().item()), mine.num_envs,
                    float(torch.rad2deg(torch.atan2(g[:, 0], -g[:, 2])).min()),
                    float(torch.rad2deg(torch.atan2(g[:, 0], -g[:, 2])).max()),
                    float(robot.data.root_lin_vel_w.torch[:, 0].mean())), flush=True)
            if k == mine.steps - 1:
                break
    for k in range(0 if mine.balance else mine.steps):
        setter(target=tgt, joint_ids=sl) if setter.__name__.endswith('_index') else setter(tgt, sl)
        scene.write_data_to_sim()
        sim.step()
        scene.update(sim_dt)
        if k % 100 == 0:
            z = robot.data.root_pos_w.torch[:, 2]
            sp = [robot.data.joint_pos.torch[:, i].mean().item() for i, n in enumerate(robot.data.joint_names) if 'spring2' in n]
            stand = int((z > 0.043).sum().item())
            jp = robot.data.joint_pos.torch[0]
            want = [QPOS.get(n, 0.0) for n in robot.data.joint_names]
            err = float((jp - torch.tensor(want, device=jp.device)).abs().max().item())
            print('  step %4d  base z %.4f..%.4f | standing %d/%d | spring2 %s | max |q-q_stance| %.3f rad | %s' % (
                k, z.min().item(), z.max().item(), stand, mine.num_envs,
                ' '.join('%+.4f' % v for v in sp), err,
                ' '.join('%s=%+.2f' % (n.replace('_joint', '')[:9], jp[i].item())
                         for i, n in enumerate(robot.data.joint_names)
                         if n.split('_')[0] == 'left' and 'wheel' not in n)), flush=True)
    if mine.png:
        try:
            for _ in range(6):
                sim.render()
            import omni.kit.app as _ka
            for _ in range(40):
                _ka.get_app().update()
        except Exception:
            pass
        import importlib
        cand = []
        try:
            ka = importlib.import_module('omni.kit.app')
            for f in ('get_app_interface', 'get_app'):
                if hasattr(ka, f):
                    try:
                        o = getattr(ka, f)()
                        cand += [o, getattr(o, 'get_app', lambda: None)()]
                    except Exception:
                        pass
        except Exception as ex:
            print('[preview] no kit app module:', ex, flush=True)
        done = False
        for o in cand:
            if o is not None and hasattr(o, 'write_viewport_to_file'):
                try:
                    o.write_viewport_to_file(mine.png)
                    print('[preview] wrote', mine.png, flush=True)
                    done = True
                    break
                except Exception as ex:
                    print('[preview] capture attempt failed:', type(ex).__name__, ex, flush=True)
        if not done:
            # Kit 2.71 / Isaac Sim 6 moved this: the viewport window itself can be captured.
            try:
                import omni.ui as ui
                import numpy as _np
                from PIL import Image as _Img
                win = ui.Workspace.get_window('Viewport')
                print('[preview] window:', win, 'capture attrs:',
                      [a for a in dir(win) if any(k in a.lower() for k in ('capture', 'shot', 'image', 'draw'))], flush=True)
                if win is not None:
                    buf = win.capture_content()
                    arr = _np.frombuffer(buf, dtype=_np.uint8).reshape(buf.height, buf.width, 4)
                    _Img.fromarray(arr[:, :, [2, 1, 0]]).save(mine.png)
                    print('[preview] wrote via capture_content', mine.png, arr.shape, flush=True)
                    done = True
            except Exception as ex:
                print('[preview] capture_content failed:', type(ex).__name__, ex, flush=True)
        if not done:
            print('[preview] IApp capture/write attrs:',
                  [a for a in dir(cand[0]) if any(k in a.lower() for k in ('capture', 'shot', 'write', 'viewport'))] if cand and cand[0] else 'n/a',
                  flush=True)
    def reassert():
        rp = robot.data.default_root_pose.torch.clone()
        rp[:, :3] += scene.env_origins
        rp[:, 0] += mine.ex0
        rp[:, 2] = mine.sz
        robot.write_root_pose_to_sim_index(root_pose=rp)
        robot.write_root_velocity_to_sim_index(root_velocity=torch.zeros(mine.num_envs, 6, device=sim.device))
        robot.write_joint_position_to_sim_index(position=tgt)
        robot.write_joint_velocity_to_sim_index(velocity=torch.zeros_like(tgt))

    if mine.hold or args_cli.visualizer:
        print('[preview] window open - close it to exit', flush=True)
        j = 0
        while simulation_app.is_running():
            # every ~0.4 s snap back to the analytic stance so the display never drifts/sags:
            # this window is for LOOKING at the model, the balance tuning is a separate job.
            if j % 50 == 0:
                reassert()
            if mine.balance > 0:
                balance()
                tl = tgt[:, LID]
                setter(target=tl, joint_ids=LID) if setter.__name__.endswith('_index') else setter(tl, LID)
            else:
                setter(target=tgt, joint_ids=sl) if setter.__name__.endswith('_index') else setter(tgt, sl)
            scene.write_data_to_sim()
            sim.step()
            scene.update(sim_dt)
            j += 1
    simulation_app.close()


if __name__ == '__main__':
    main()
