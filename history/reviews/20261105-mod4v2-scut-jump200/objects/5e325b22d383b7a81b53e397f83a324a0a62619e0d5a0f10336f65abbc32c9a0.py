"""Finite original SCUT policy evaluation, without training or MOD4 writes."""
from pathlib import Path
import argparse
import sys
import json
import traceback
import datetime
import os
import hashlib

os.environ['OMNI_KIT_ACCEPT_EULA'] = 'YES'
os.environ['ISAACSIM_ACCEPT_EULA'] = 'Y'

# Load the installed tensor extensions before Kit loads its own C++ libraries.
import torch
import tensordict

ROOT = Path(__file__).resolve().parent
REF = Path('C:/Users/lulu/Desktop/claude/mjcf/reference_repos/scut_wheeled_legged_RL')
SAVED = Path('C:/Users/lulu/Desktop/claude/mjcf/polar-rl-train/history/reviews/20261102-scut-standing-step-video-115-128/primary/pretrained/26_infantry/rough_rotation_stair/2026-07-23_16-23-21/params/env.yaml')
for rel in ('source/agent_tasks', 'source/agent_world', 'source/agent_rl', '.'):
    sys.path.insert(0, str(REF / rel))

from isaaclab.app import AppLauncher
parser = argparse.ArgumentParser()
parser.add_argument('--probe', action='store_true')
parser.add_argument('--output', default='native01')
parser.add_argument('--num_envs', type=int, default=4)
parser.add_argument('--steps', type=int, default=500)
parser.add_argument('--matrix', action='store_true')
parser.add_argument('--native-rough', action='store_true')
parser.add_argument('--stand-extended', action='store_true')
parser.add_argument('--gate-standing', action='store_true')
parser.add_argument('--saved-gimbal-semantics', action='store_true')
parser.add_argument('--controller', choices=('manual', 'stair', 'both'))
parser.add_argument('--detector', choices=('saved', '200'), default='saved')
parser.add_argument('--jump-peak', type=float, default=.70)
parser.add_argument('--seed', type=int, default=66)
AppLauncher.add_app_launcher_args(parser)
args = parser.parse_args()
outdir = ROOT / args.output
outdir.mkdir(parents=True, exist_ok=True)
runner_source=Path(__file__).read_bytes()
(outdir/'RUNNER_SOURCE.py').write_bytes(runner_source)
(outdir/'INVOCATION.json').write_text(json.dumps({'argv':sys.argv,'source_sha256':hashlib.sha256(runner_source).hexdigest(),'epoch_local':datetime.datetime.now().astimezone().isoformat()},indent=2),encoding='utf-8')
application = None
env = None
try:
    application = AppLauncher(args).app
    import torch
    torch.set_num_threads(1)
    import numpy as np
    import yaml
    import copy
    from isaaclab.utils.string import string_to_callable
    from agent_tasks.direct.wheelbipe.wheelbipe_V14.env_cfg import WheelbipeV14RoughEnvCfg
    from agent_tasks.direct.wheelbipe.wheelbipe_V14.env import WheelbipeV14Env
    from isaaclab.terrains import TerrainImporter
    import trimesh

    class LocalPlaneTerrain(TerrainImporter):
        def import_ground_plane(self, name, size=(200., 200.)):
            floor = trimesh.creation.box(extents=(200., 200., .1))
            floor.apply_translation((0., 0., -.05))
            meshes = [floor]
            if args.stand_extended:
                origins = self._compute_env_origins_grid(self.cfg.num_envs, self.cfg.env_spacing).cpu().numpy()
                for i, case in enumerate(cases):
                    if case['kind'] == 'flat': continue
                    count = 5 if case['kind'] == 'small_stairs' else 1
                    for k in range(count):
                        height = case['step_height'] * (k + 1)
                        start = case['edge'] + k * .1
                        end = case['edge'] + 5.
                        shape = trimesh.creation.box(extents=(end-start, 3., height))
                        shape.apply_translation((origins[i,0] + (start+end)/2, origins[i,1], height/2))
                        meshes.append(shape)
            self.import_mesh(name, trimesh.util.concatenate(meshes))

    cases = []
    if args.controller:
        args.matrix = True
        args.stand_extended = True  # Include the actual boxes in the raycast terrain mesh.
        if args.controller == 'manual':
            for v in (0., .6, 1.2, 1.8):
                cases.append(dict(kind='flat', velocity=v, height_command=.28, edge=1.6,
                                  step_height=0., trigger_distance=.4))
            for v in (.6, 1.2, 1.8, 2.4):
                for distance in (.2, .4, .6):
                    cases.append(dict(kind='single200', velocity=v, height_command=.28,
                                      edge=1.6, step_height=.2, trigger_distance=distance))
        else:
            for height in (.13, .2):
                for v in (.6, 1.2, 1.8, 2.4):
                    for command in (.28, .38):
                        cases.append(dict(kind='single200' if height == .2 else 'single130',
                                          velocity=v, height_command=command, edge=1.6,
                                          step_height=height, trigger_distance=.4))
        args.num_envs = len(cases)
    elif args.matrix:
        for kind in ('flat', 'small_stairs', 'single200'):
            for v in (.6, 1.2, 1.8, 2.4):
                for h in ((.38, .42) if args.stand_extended else (.24, .34)):
                    cases.append({'kind': kind, 'velocity': v, 'height_command': h, 'edge': 1.6, 'step_height': .04 if kind == 'small_stairs' else (.2 if kind == 'single200' else 0.)})
        args.num_envs = len(cases)

    class VerifyEnv(WheelbipeV14Env):
        def _before_state_machine_command_updated(self):
            super()._before_state_machine_command_updated()
            if not args.controller:
                return
            from isaaclab.utils.math import euler_xyz_from_quat, wrap_to_pi
            _, _, yaw = euler_xyz_from_quat(self.robot.data.root_quat_w)
            age = self.episode_length_buf.float() * self.step_dt
            progress = self.robot.data.root_pos_w[:, 0] - self.terrain.env_origins[:, 0]
            velocity = torch.tensor([c['velocity'] for c in cases], device=self.device)
            self.command.zero_()
            self.command[:, 0] = torch.where((age >= 1.5) & (progress < 2.5), velocity, 0.)
            self.command[:, 2] = torch.clamp(-5. * wrap_to_pi(yaw), -6.28, 6.28)
            self.height_cmd[:] = torch.tensor([c['height_command'] for c in cases], device=self.device)
            self.command_generator.vel_command_b[:] = self.command
            if not hasattr(self, 'verify_requested'):
                self.verify_requested = torch.zeros(self.num_envs, dtype=torch.bool, device=self.device)
                self.verify_request_log = []
            if args.controller in ('manual', 'both'):
                threshold = torch.tensor([c['edge']-c['trigger_distance'] for c in cases], device=self.device)
                flat = torch.tensor([c['kind']=='flat' for c in cases], device=self.device)
                fire = (~self.verify_requested) & (age >= 1.5) & torch.where(flat, age >= 2.5, progress >= threshold)
                ids = fire.nonzero(as_tuple=False).flatten()
                if ids.numel():
                    self.request_jump_takeoff(ids)
                    self.verify_requested[ids] = True
                    self.verify_request_log.append(dict(ids=ids.cpu().tolist(), age=age[ids].cpu().tolist(),
                        root_x=progress[ids].cpu().tolist(), route='public request_jump_takeoff; no force/velocity assist'))

        def _setup_scene(self):
            super()._setup_scene()
            if args.matrix and not args.stand_extended:
                import isaaclab.sim as sim_utils
                for i, case in enumerate(cases):
                    if case['kind'] == 'flat':
                        continue
                    ox, oy, _ = self.terrain.env_origins[i].cpu().tolist()
                    count = 5 if case['kind'] == 'small_stairs' else 1
                    for k in range(count):
                        height = case['step_height'] * (k + 1)
                        start = case['edge'] + k * .1
                        end = case['edge'] + 5.
                        shape = sim_utils.CuboidCfg(size=(end - start, 3., height), collision_props=sim_utils.CollisionPropertiesCfg(), physics_material=self.cfg.terrain.physics_material, visual_material=sim_utils.PreviewSurfaceCfg(diffuse_color=(.2, .35, .5)))
                        shape.func(f'/World/teacher_obstacles/case_{i}/step_{k}', shape, translation=(ox + (start + end) / 2, oy, height / 2))

        def _on_command_updated(self):
            if args.controller:
                return super()._on_command_updated()
            super()._on_command_updated()
            self.command[:] = 0.
            if args.matrix or args.native_rough:
                from isaaclab.utils.math import euler_xyz_from_quat, wrap_to_pi
                _, _, yaw = euler_xyz_from_quat(self.robot.data.root_quat_w)
                progress = self.robot.data.root_pos_w[:, 0] - self.terrain.env_origins[:, 0]
                wanted = torch.tensor([c['velocity'] for c in cases], device=self.device) if args.matrix else torch.full((self.num_envs,),1.2,device=self.device)
                age = self.episode_length_buf.to(torch.float) * self.step_dt
                ready = age >= (2.5 if args.stand_extended else 1.5)
                if args.gate_standing:
                    from isaaclab.utils.math import euler_xyz_from_quat
                    roll, pitch, _ = euler_xyz_from_quat(self.robot.data.root_quat_w)
                    force = torch.linalg.vector_norm(self.contact_sensor.data.net_forces_w[:,self._desired_contact_link_idx],dim=-1)
                    quiet = (torch.linalg.vector_norm(self.robot.data.root_lin_vel_w[:,:2],dim=-1)<.05) & (self.robot.data.root_lin_vel_w[:,2].abs()<.05) & (force>1.).all(-1) & (wrap_to_pi(roll).abs()<.174533) & (wrap_to_pi(pitch).abs()<.174533) & (age>1.5)
                    if not hasattr(self,'verify_standing_count'):
                        self.verify_standing_count=torch.zeros(self.num_envs,dtype=torch.long,device=self.device)
                        self.verify_approach_started=torch.zeros(self.num_envs,dtype=torch.bool,device=self.device)
                    self.verify_standing_count=torch.where(quiet,self.verify_standing_count+1,0)
                    self.verify_approach_started |= self.verify_standing_count>=25
                    ready &= self.verify_approach_started
                stop = progress > 2.5
                self.command[:, 0] = torch.where(ready & ~stop, wanted, 0.)
                self.command[:, 2] = torch.clamp(-5. * wrap_to_pi(yaw), -6.28, 6.28)
                self.height_cmd[:] = torch.tensor([c['height_command'] for c in cases], device=self.device) if args.matrix else .35
                if args.stand_extended:
                    target = torch.tensor([c['height_command'] for c in cases], device=self.device)
                    self.height_cmd[:] = .34 + (target-.34) * torch.clamp((age-.5)/1.,0.,1.)
            else:
                self.command[:, 0] = .6
                self.height_cmd[:] = .28
            self.command_generator.vel_command_b[:] = self.command

    class Loader(yaml.FullLoader):
        pass
    Loader.add_constructor('tag:yaml.org,2002:python/object/apply:builtins.slice', lambda loader, node: slice(*loader.construct_sequence(node)))
    saved = yaml.load(SAVED.read_text(encoding='utf-8'), Loader=Loader)
    cfg = WheelbipeV14RoughEnvCfg()
    def merge(old, new):
        if isinstance(new, dict):
            if old is None:
                return copy.deepcopy(new)
            if isinstance(old, dict):
                return {k: merge(old.get(k), v) for k, v in new.items()}
            for key, value in new.items():
                setattr(old, key, merge(getattr(old, key, None), value))
            return old
        if callable(old) and isinstance(new, str):
            return string_to_callable(new)
        return copy.deepcopy(new)
    cfg = merge(cfg, saved)
    cfg.seed = args.seed
    compatibility = {}
    if args.saved_gimbal_semantics:
        for field in ('gimbal_heading_control_cfg','gimbal_spin_translate_cfg'):
            if field not in saved:
                old = copy.deepcopy(getattr(cfg,field))
                getattr(cfg,field)['enabled'] = False
                compatibility[field] = {'current_public_default':old,'saved_training_field_present':False,'evaluation_enabled':False}
        for field in vars(cfg.events):
            if not field.startswith('_') and field not in saved['events']:
                compatibility['events/'+field]={'saved_training_field_present':False,'evaluation':None}
                setattr(cfg.events,field,None)
        if 'height_obs_clip_enabled' not in saved:
            compatibility['height_obs_clip_enabled']={'saved_training_field_present':False,'prior_default':cfg.height_obs_clip_enabled,'evaluation':False}
            cfg.height_obs_clip_enabled=False
        (outdir/'SAVED_CONFIG_COMPATIBILITY.json').write_text(json.dumps(compatibility,default=str,indent=2),encoding='utf-8')
    cfg.robot_cfg.spawn.usd_path = str(REF / 'source/agent_world/agent_world/assets/usd_files/wheelbipeV14_2_1/wheelbipeV14_2.usd')
    if args.controller:
        cfg.enable_state_machines = True
        cfg.airborne_state_machine_cfg['enabled'] = False
        cfg.jump_takeoff_state_machine_cfg['enabled'] = args.controller in ('manual', 'both')
        cfg.jump_takeoff_state_machine_cfg['trajectory']['enabled'] = True
        cfg.jump_takeoff_state_machine_cfg['trajectory']['peak_height'] = (args.jump_peak, args.jump_peak)
        cfg.jump_takeoff_state_machine_cfg['trigger']['mode'] = 'manual'
        cfg.jump_takeoff_state_machine_cfg['trigger']['require_tracking'] = False
        cfg.jump_takeoff_state_machine_cfg['assist']['enabled'] = False
        cfg.jump_takeoff_permission_cfg['enabled'] = False
        cfg.wheel_forward_scan_cfg['enabled'] = args.controller in ('stair', 'both')
        cfg.stair_state_machine_cfg['enabled'] = args.controller in ('stair', 'both')
        if args.detector == '200':
            cfg.wheel_forward_scan_cfg['detect'].update(step_height_min=.12, step_height_max=.25, wall_height=.25)
        cfg.leg_length_range = [.22, .22]
    cfg.scene.num_envs = args.num_envs
    cfg.scene.env_spacing = 8.0
    if not args.native_rough:
        cfg.terrain.terrain_type = 'plane'
        cfg.terrain.class_type = LocalPlaneTerrain
        cfg.terrain.terrain_generator = None
        cfg.terrain.use_terrain_origins = False
    else:
        generator = cfg.terrain.terrain_generator
        from isaaclab.terrains import HfPyramidStairsTerrainCfg
        stair = HfPyramidStairsTerrainCfg()
        stair = merge(stair, generator.sub_terrains['inv_stair_slope_for_rm_mid'])
        stair.proportion = 1.
        generator.sub_terrains = {'inv_stair_slope_for_rm_mid': stair}
        generator.num_rows = 1
        generator.num_cols = 1
        generator.curriculum = False
        generator.difficulty_range = (.7, 1.)
        cfg.terrain.max_init_terrain_level = 0
    cfg.sim.device = args.device
    cfg.sim.log_dir = str(outdir)
    cfg.play_wheel_material_debug = False
    if args.matrix or args.native_rough:
        cfg.scene.env_spacing = 12.
        cfg.commands.special_modes = ()
        cfg.use_predefined_leg_random_start = False
        cfg.predefined_reset_air['enabled'] = False
        cfg.leg_length_range = [.22, .22] if args.controller else ([.32, .32] if args.stand_extended else [.22, .22])
        cfg.leg_angle_range = [0., 0.]
        cfg.use_joint_vel_random_start = False
        cfg.events.reset_base.params['pose_range'] = {'roll': (0., 0.), 'pitch': (0., 0.), 'yaw': (0., 0.)}
        cfg.events.reset_base.params['velocity_range'] = {}
        cfg.curriculum = None
        cfg.viewer.eye = (3.4, 5.2, 2.2)
        cfg.viewer.lookat = (1.4, 0., .3)
        cfg.rough_terrain_boundary_reset_cfg['enabled'] = False
    merge_errors = []
    summary = {'time': datetime.datetime.now().astimezone().isoformat(), 'torch': torch.__version__, 'cuda': torch.version.cuda, 'merge_errors': merge_errors, 'checkpoint': str(ROOT / 'model_1000.pt'), 'device': args.device, 'cfg_class': str(type(cfg)), 'obs': cfg.observation_space, 'action': cfg.action_space, 'simdt': cfg.sim.dt, 'decimation': cfg.decimation}
    (outdir / 'CONFIG_PROBE.json').write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding='utf-8')
    print('CONFIG_PROBE', json.dumps(summary, ensure_ascii=False), flush=True)
    if merge_errors:
        raise RuntimeError('Saved config requires explicit compatibility handling; see CONFIG_PROBE.json')
    if not args.probe:
        env = VerifyEnv(cfg)
        if args.controller:
            import contextlib, io
            from scripts.rsl_rl.keyboard_controller import Se3KeyboardMobile
            from types import SimpleNamespace
            keyboard = SimpleNamespace(_env=SimpleNamespace(unwrapped=env))
            capture = io.StringIO()
            with contextlib.redirect_stdout(capture):
                Se3KeyboardMobile._trigger_manual_jump(keyboard)
            (outdir/'RAW_Q_CALLBACK.json').write_text(json.dumps(dict(
                callback='Unmodified Se3KeyboardMobile._trigger_manual_jump',
                env_has_trigger_manual_jump=hasattr(env,'trigger_manual_jump'),
                env_has_request_jump_takeoff=hasattr(env,'request_jump_takeoff'),
                stdout=capture.getvalue(), original_saved_state_machines=saved['enable_state_machines'],
                original_saved_jump=saved['jump_takeoff_state_machine_cfg'],
                original_saved_stair=saved['stair_state_machine_cfg'],
                controller=args.controller, detector=args.detector,
                author_checkpoint_trained_with_these_state_machines=False,
                physics_assistance_enabled=False),ensure_ascii=False,indent=2),encoding='utf-8')
        if args.native_rough:
            from isaacsim.core.utils.stage import get_current_stage
            from pxr import UsdGeom,Usd
            stage=get_current_stage()
            prim=stage.GetPrimAtPath('/World/ground/terrain')
            mesh=next(UsdGeom.Mesh(p) for p in Usd.PrimRange(prim) if p.IsA(UsdGeom.Mesh))
            np.savez_compressed(outdir/'ACTUAL_TERRAIN.npz',vertices=np.asarray(mesh.GetPointsAttr().Get()),counts=np.asarray(mesh.GetFaceVertexCountsAttr().Get()),indices=np.asarray(mesh.GetFaceVertexIndicesAttr().Get()))
        policy = torch.jit.load(str(ROOT / 'policy.pt'), map_location=env.device).eval()
        obs, info = env.reset()
        (outdir / 'EFFECTIVE_CONFIG.json').write_text(json.dumps(cfg.to_dict(), default=str, ensure_ascii=False, indent=2), encoding='utf-8')
        if args.matrix or args.native_rough:
            if args.native_rough:
                cases = [{'kind':'native_inverse_mid','velocity':1.2,'height_command':.35,'edge':.5,'step_height':.04} for _ in range(args.num_envs)]
            (outdir / 'CASES.json').write_text(json.dumps({'cases': cases, 'origins': env.terrain.env_origins.cpu().tolist(), 'body_names': env.robot.body_names, 'joint_names': env.robot.joint_names, 'contact_names': env.contact_sensor.body_names, 'wheel_radius_source': .06, 'physics_dt': cfg.sim.dt, 'start': 'original IK, zero initial velocity/yaw, startup DR retained; 1.5 s standing before approach', 'stop_command_root_x': 2.5}, indent=2), encoding='utf-8')
        active = torch.ones(args.num_envs, device=env.device, dtype=torch.bool)
        physical = {'root': [], 'body_pos': [], 'body_quat': [], 'force': [], 'joint_pos': [], 'active': [], 'command': [], 'episode_step': []}
        control_fields = ('jump_takeoff_phase', 'jump_takeoff_trigger_event', 'jump_takeoff_assist_event',
            'jump_takeoff_ref_target_height', 'wheel_forward_stair_state', 'wheel_forward_stair_detect_event',
            'wheel_forward_step_detect_event', 'wheel_forward_wall_reset', 'wheel_forward_stair_success_exit_event',
            'wheel_forward_stair_failure_exit_event', 'wheel_forward_stair_timeout_exit_event')
        if args.controller:
            physical.update({k:[] for k in control_fields})
            physical.update(ctrl_mode=[], effective_height=[])
        base_update = env.scene.update
        def observed_update(*a, **kw):
            base_update(*a, **kw)
            physical['root'].append(env.robot.data.root_state_w.detach().cpu().numpy().copy())
            physical['body_pos'].append(env.robot.data.body_pos_w.detach().cpu().numpy().copy())
            physical['body_quat'].append(env.robot.data.body_quat_w.detach().cpu().numpy().copy())
            physical['force'].append(env.contact_sensor.data.net_forces_w.detach().cpu().numpy().copy())
            physical['joint_pos'].append(env.robot.data.joint_pos.detach().cpu().numpy().copy())
            physical['active'].append(active.cpu().numpy().copy())
            physical['command'].append(env.command.detach().cpu().numpy().copy())
            physical['episode_step'].append(env.episode_length_buf.detach().cpu().numpy().copy())
            if args.controller:
                for field in control_fields:
                    physical[field].append(getattr(env,field).detach().cpu().numpy().copy())
                physical['ctrl_mode'].append(env._get_ctrl_mode_obs_raw().detach().cpu().numpy().copy())
                physical['effective_height'].append(env._get_observation_height_cmd().detach().cpu().numpy().copy())
        env.scene.update = observed_update
        print('ENV_READY', env.robot.joint_names, env.robot.body_names, flush=True)
        rows = []
        for step in range(args.steps):
            env.command_generator.vel_command_b[:] = 0
            env.command_generator.vel_command_b[:, 0] = .6
            env.command_generator.is_heading_env[:] = False
            env.command_generator.is_standing_env[:] = False
            if not args.matrix:
                env.height_cmd[:] = .28
            with torch.inference_mode():
                action = policy(obs['policy'])
                obs, reward, terminated, timeout, info = env.step(action)
            active &= ~(terminated | timeout)
            rows.append({'step': step, 'root': env.robot.data.root_state_w.detach().cpu().tolist(), 'terminated': terminated.cpu().tolist(), 'timeout': timeout.cpu().tolist()})
            if step % 100 == 0:
                print('PROGRESS', step, 'active', int(active.sum()), 'maxrootz', float(env.robot.data.root_pos_w[:, 2].max()), flush=True)
        np.savez_compressed(outdir / 'PHYSICAL.npz', **{k: np.asarray(v) for k, v in physical.items()})
        (outdir / 'FLAT_ROWS.json').write_text(json.dumps(rows), encoding='utf-8')
        (outdir / 'COMPLETE.json').write_text(json.dumps({'steps': args.steps, 'envs': args.num_envs}), encoding='utf-8')
        if args.gate_standing:
            (outdir/'STANDING_GATE.json').write_text(json.dumps({'required_seconds':.5,'planar_v_max':.05,'vertical_v_max':.05,'roll_pitch_max_rad':.174533,'bilateral_wheel_force_min_N':1.,'approach_started':env.verify_approach_started.cpu().tolist(),'final_standing_count':env.verify_standing_count.cpu().tolist()},indent=2),encoding='utf-8')
        if args.controller:
            (outdir/'REQUESTS.json').write_text(json.dumps(env.verify_request_log,indent=2),encoding='utf-8')
except BaseException as exc:
    (outdir / 'ERROR.json').write_text(json.dumps({'error': repr(exc), 'traceback': traceback.format_exc(), 'time': datetime.datetime.now().astimezone().isoformat()}, indent=2, ensure_ascii=False), encoding='utf-8')
    traceback.print_exc()
    raise
finally:
    if env is not None:
        env.close()
    if application is not None:
        application.close()
