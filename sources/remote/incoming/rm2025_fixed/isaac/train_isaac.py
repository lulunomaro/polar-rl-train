
# RMUC 2025/2026 wheel-leg chassis - Isaac Lab (PhysX) PPO training with a live viewport.
#
#   GUI + 1024 envs:  .venv-isaaclab\Scripts\python.exe incoming/rm2025_fixed/isaac/train_isaac.py --viz kit
#   headless:         ... train_isaac.py            (no --viz = headless in Isaac Lab 3.0)
#   resume:           ... train_isaac.py --viz kit --resume runs/rm2025_serial_isaac/<run>/model_XXX.pt
#
# TEACHER / curriculum research only: this serial [hip, knee] policy is not deployable on the
# real similar-linkage [rear1(thigh), front1(crank)] drivetrain.  Production training/export is
# RMVehicle-CC-Field-v0 under train/rmvehicle.
#
# Model: incoming/rm2025_fixed/isaac/robot_serial (the PhysX serial surrogate of the delivered
# closed-chain MJCF scene_training.xml; the delivered closed-chain USD fails its own acceptance
# guard in PhysX: left_proximal_closure separated by 0.283 m).  NO gimbal in this model - the
# gimbal is added later by resuming from these checkpoints (see CKPT_*.md).
import argparse, io, json, math, os, sys, time
HERE = os.path.dirname(os.path.abspath(__file__))
WORKSPACE_ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
sys.path.insert(0, HERE)
ap = argparse.ArgumentParser(description='Isaac Lab PPO for the rm2025 serial surrogate')
ap.add_argument('--num_envs', type=int, default=1024)
ap.add_argument('--iters', type=int, default=1200)
ap.add_argument('--steps-per-env', type=int, default=24,
                help='rollout steps collected per environment for each PPO iteration')
ap.add_argument('--usd', default=os.path.join(HERE, 'robot_serial', 'robot_serial.usda'))
ap.add_argument('--exp', default='rm2025_serial_isaac')
ap.add_argument('--run', default='')
ap.add_argument('--resume', default=None, help='path to a model_*.pt to continue from (gimbal step later)')
ap.add_argument('--logdir', default=os.path.join(HERE, 'runs'))
ap.add_argument('--save_interval', type=int, default=50)
ap.add_argument('--lr', type=float, default=3e-4)
ap.add_argument('--cmd', type=float, default=1.2, help='half-range of the forward-velocity command (m/s)')
ap.add_argument('--field', action='store_true', help='put the robots on the RMUC2026 field instead of flat floor')
ap.add_argument('--skills', action='store_true',
                help='stage-2 locomotion: level chassis, turning, gyro-spin and jump/stair curriculum')
ap.add_argument('--terrain-all', action='store_true',
                help='stage-3 spawn curriculum: gap, launch ramp, two-level stairs and slope gyro')
ap.add_argument('--obstacle-focus', action='store_true',
                help='stage-4 mix: 50%% gap/launch, 25%% main terrain, 12.5%% turn, 12.5%% gyro')
ap.add_argument('--focus-profile', choices=('mixed', 'jump', 'traverse', 'gyro'), default='mixed',
                help='training-only environment allocation used by automatic post-evaluation refinement')
ap.add_argument('--jump-curriculum', action='store_true',
                help='stage-5 phased takeoff/flight/landing curriculum with decaying assistance')
ap.add_argument('--curriculum-base-iter', type=int, default=0,
                help='global PPO iteration of the resume checkpoint (keeps assist decay restart-safe)')
ap.add_argument('--assist-start-iter', type=int, default=0)
ap.add_argument('--assist-end-iter', type=int, default=0)
ap.add_argument('--assist-prob-start', type=float, default=0.85)
ap.add_argument('--assist-vx', type=float, default=1.35)
ap.add_argument('--assist-vz', type=float, default=2.05)
ap.add_argument('--eval-only', action='store_true',
                help='run deterministic, zero-assist validation instead of PPO updates')
ap.add_argument('--eval-steps', type=int, default=2000)
ap.add_argument('--eval-report', default='', help='JSON output path for deterministic validation')
ap.add_argument('--eval-hold', action='store_true',
                help='after validation, keep deterministic play running in the visible window')
ap.add_argument('--yaw-cmd', type=float, default=14.0,
                help='stage-2 maximum absolute yaw-rate command (rad/s)')
ap.add_argument('--init-std', type=float, default=0.55,
                help='stage-2 action exploration std after warm-starting the locomotion policy')
ap.add_argument('--wheel-curve', dest='wheel_curve', action='store_true',
                help='clamp wheel torque with the DM3519+15.8 envelope (current-limited plateau, then '
                     'a voltage-limited linear fall to no-load), so the sim cannot spin the wheels '
                     'faster than the real wheel motor can deliver torque')
ap.add_argument('--wheel-stall', dest='wheel_stall', type=float, default=None,
                help='wheel stall/plateau torque (N.m) used by --wheel-curve; default comes from '
                     'import_contract.json wheel_motor (DM3519 + 15.8 gearbox -> 6.42 N.m at the wheel)')
ap.add_argument('--wheel-noload', dest='wheel_noload', type=float, default=None,
                help='wheel no-load speed (rad/s); default from import_contract.json wheel_motor '
                     '(DM3519 + 15.8: 528.6 rpm = 55.36 rad/s)')
ap.add_argument('--wheel-knee', dest='wheel_knee', type=float, default=None,
                help='wheel speed (rad/s) where the current-limited torque plateau ends and the '
                     'voltage-limited linear drop to no-load begins; default from the contract '
                     '(DM3519 + 15.8: 44.0 rad/s). Pass 0 for the old linear-from-stall shape.')
ap.add_argument('--wheel-velocity', dest='wheel_velocity', action='store_true',
                help='interpret the two wheel action channels as wheel-SPEED targets (rad/s, scaled by '
                     '--wheel-vel-scale) closed by a torque servo, exactly like the deployable '
                     'contract (wheel_action_scale 55.0, wheel_kd 0.6).  spin_pure_v1/v2 and '
                     'spin_gate_v1 all failed the 小陀螺 for the same reason: with a raw torque '
                     'interface a policy has to integrate a speed error forever to hold a speed, so '
                     'the probe showed the wheels dithering at |w|~17 rad/s with only ~1 rad/s of '
                     'differential.  The closed-chain mjlab policy, which IS a speed servo, reaches '
                     '1.92 rev/s with 0.67 N.m and 0 pct saturation.')
ap.add_argument('--wheel-vel-scale', dest='wheel_vel_scale', type=float, default=55.0,
                help='rad/s of wheel speed per unit wheel action when --wheel-velocity is set')
ap.add_argument('--wheel-vel-kd', dest='wheel_vel_kd', type=float, default=0.6,
                help='wheel speed servo gain (N.m per rad/s), same number the deploy contract uses')
ap.add_argument('--wheel-armature', dest='wheel_armature', type=float, default=None,
                help='rotor inertia reflected to the wheel joint (kg.m^2).  Default is the '
                     'contract value sim_rotor_armature_kg_m2 (0.0 = keep the V11 baseline). '
                     'A DM3519 rotor behind 15.8:1 reflects ~0.0008-0.0025, so pass e.g. 0.0015 '
                     'to study wheel-reaction effects on the 小陀螺.')
ap.add_argument('--yaw-ramp-iters', dest='yaw_ramp_iters', type=float, default=20000.0,
                help='PPO iterations over which the gyro yaw command ramps from its start value '
                     'to --yaw-cmd.  The 20000 default is the historical slow ramp; a focused '
                     '小陀螺 run wants ~2000 so the full 2 rev/s actually gets sampled.')
ap.add_argument('--spin-pure', dest='spin_pure', action='store_true',
                help='reward a REAL 小陀螺: in-place yaw with zero chassis translation (wheels forced to '
                     'counter-rotate) instead of the differential-arc shortcut PPO otherwise finds')
ap.add_argument('--spin-band', dest='spin_band', type=float, default=3.0,
                help='yaw-tracking kernel sigma (rad/s) on gyro lanes when --spin-pure is set')
ap.add_argument('--spin-weight', dest='spin_weight', type=float, default=3.0,
                help='weight of the zero-translation (in-place) term on gyro lanes')
ap.add_argument('--gyro-posture-relax', dest='gyro_posture_relax', type=float, default=0.0,
                help='on gyro lanes, scale the posture-family weights (upright/level/height) by '
                     '(1 - this).  A real 小陀螺 deliberately breaks the balance posture to spin, '
                     'but level(7.0)+upright(1.2)+height(1.2) outweigh every yaw term combined, so '
                     'PPO keeps the chassis still and farms posture instead.  0.5 halves them.')
ap.add_argument('--spin-pivot', dest='spin_pivot', choices=('wheel', 'root'), default='wheel',
                help='what "in place" means for the 小陀螺 reward.  wheel = the wheel-axle '
                     'midpoint must not move (the only point a two-wheeled vehicle CAN yaw '
                     'about without scrubbing); root = the chassis origin, which is what the '
                     'code used before and which is unreachable here because the neutral pose '
                     'puts the axle 198 mm behind the origin.')
ap.add_argument('--spin-product-weight', dest='spin_product_weight', type=float, default=0.0,
                help='weight of the PRODUCT spin_hold*spin_rate on gyro lanes.  Kept separate, the '
                     'zero-translation term is farmed by standing still (spin_hold 3.0 dwarfs '
                     'spin_rate 1.5 and rotating costs hold), which is exactly what spin_pure_v1/v2 '
                     'did: spin_rate_ratio stayed at 0.03-0.04 for 3000 iterations.  The product can '
                     'only be earned by rotating IN PLACE; pair it with a small --spin-weight (0.5).')
ap.add_argument('--spin-rate-weight', dest='spin_rate_weight', type=float, default=1.5,
                help='weight of the achieved-yaw-rate term (prevents standing still to farm the '
                     'in-place term)')
ap.add_argument('--gyro-stance-weight', dest='gyro_stance_weight', type=float, default=3.0,
                help='weight of the left/right stance asymmetry penalty (1.0 recommended with --spin-pure)')
ap.add_argument('--hold-iters', dest='hold_iters', type=int, default=0,
                help='for the first N policy steps re-assert the neutral state instead of the policy '
                     '(so the viewport starts from a clean standing pose and the critic sees a sane value)')
ap.add_argument('--ack-serial-teacher-not-deployable', action='store_true',
                help='explicitly acknowledge that this [hip,knee] PhysX surrogate is a teacher/viewer '
                     'only and its checkpoints must not be deployed to the [thigh,crank] hardware')
MyArgs, _rest = ap.parse_known_args()
if not MyArgs.ack_serial_teacher_not_deployable:
    raise SystemExit(
        'REFUSING SERIAL-SURROGATE TRAINING: this policy commands [hip,knee], but the real closed-chain '
        'robot commands [thigh,crank]. Train/deploy RMVehicle-CC-Field-v0 instead. If this run is '
        'intentionally teacher-only, pass --ack-serial-teacher-not-deployable.'
    )
print('[SAFETY] SERIAL TEACHER ONLY -- NOT HARDWARE DEPLOYABLE; production task is '
      'RMVehicle-CC-Field-v0 ([thigh, crank] active coordinates).', flush=True)
from isaaclab.app import AppLauncher
_p = argparse.ArgumentParser()
AppLauncher.add_app_launcher_args(_p)
Args, _u = _p.parse_known_args()
Launcher = AppLauncher(Args)
app = Launcher.app
import numpy as np
import gymnasium.spaces as gspaces
import torch
import isaaclab.sim as sim_utils
from isaaclab.actuators import ImplicitActuatorCfg
from isaaclab.assets import ArticulationCfg, AssetBaseCfg
from isaaclab.envs import DirectRLEnv, DirectRLEnvCfg
from isaaclab.scene import InteractiveSceneCfg
from isaaclab.sensors import ContactSensorCfg
from isaaclab.utils import configclass
CONTRACT = json.loads(open(os.path.join(HERE, 'import_contract.json'), encoding='utf-8').read())
MOTOR = CONTRACT['leg_motor']
WMOTOR = CONTRACT.get('wheel_motor') or {}
# 轮电机 = 达妙 DM3519 裸电机 + 15.8:1 减速箱（用户 2026-09-09 确认）。轮端包线：
# 电流限幅平台 6.42 N.m 直到 knee 44.0 rad/s，再线性下降到空载 55.36 rad/s (528.6 rpm)。
# 反推自 DM-S3519-1EC(内含19.2) 的官方点：空载435rpm / 额定3.5N.m@395rpm / 峰值7.8N.m。
WHEEL_STALL_DEFAULT = float(WMOTOR.get('sim_envelope_stall_nm', 6.4188))
WHEEL_KNEE_DEFAULT = float(WMOTOR.get('sim_envelope_knee_rad_s', 44.0118))
WHEEL_NOLOAD_DEFAULT = float(WMOTOR.get('no_load_speed_rad_s', 55.3557))
_TURN = 2 * 3.141592653589793
_WHEEL_R_M = float(CONTRACT['geometry']['left_tire']['size'][0])
_HALF_TRACK_M = 0.5 * abs(float(CONTRACT['bodies']['left_wheel']['neutral_position_m'][1]) -
                          float(CONTRACT['bodies']['right_wheel']['neutral_position_m'][1]))
# Pure-yaw spin ceiling of the drivetrain: both wheels at no-load speed, chassis translating 0.
GYRO_CEILING_RAD_S = WHEEL_NOLOAD_DEFAULT * _WHEEL_R_M / _HALF_TRACK_M
GYRO_2REV_WHEEL_RAD_S = 2.0 * _TURN * _HALF_TRACK_M / _WHEEL_R_M
print('[cfg] wheel motor:', WMOTOR.get('model', 'not in contract'),
      '| plateau %.2f N.m up to %.2f rad/s, no-load %.2f rad/s (%.0f rpm)'
      % (WHEEL_STALL_DEFAULT, WHEEL_KNEE_DEFAULT, WHEEL_NOLOAD_DEFAULT,
         WHEEL_NOLOAD_DEFAULT * 60 / _TURN), flush=True)
print('[cfg] gyro ceiling: %.2f rad/s = %.2f rev/s (needs %.2f rad/s per wheel for 2 rev/s)'
      % (GYRO_CEILING_RAD_S, GYRO_CEILING_RAD_S / _TURN, GYRO_2REV_WHEEL_RAD_S), flush=True)
SPAWN_Z = float(CONTRACT['spawn_height_m'])
WHEEL_RADIUS = float(CONTRACT['geometry']['left_tire']['size'][0])
MOTOR_JOINTS = CONTRACT['actuated_joint_names']
LIM = torch.tensor(CONTRACT['effort_limits_nm'], dtype=torch.float32)
# Keep the V11 baseline (armature 0.0) unless the contract/CLI explicitly asks for it.
WHEEL_ARMATURE = (MyArgs.wheel_armature if MyArgs.wheel_armature is not None
                  else float(WMOTOR.get('sim_rotor_armature_kg_m2', 0.0)))
TARGET_HEIGHT = SPAWN_Z
FIELD_INFO = {}


SERIAL_MOTORS = ['left_hip', 'left_knee', 'left_wheel_spin', 'right_hip', 'right_knee', 'right_wheel_spin']
LEG_IDX = [0, 1, 3, 4]
WHL_IDX = [2, 5]
WHEEL = WHL_IDX


@configclass
class SceneCfg(InteractiveSceneCfg):
    ground = AssetBaseCfg(
        prim_path='/World/Ground', init_state=AssetBaseCfg.InitialStateCfg(pos=(0.0, 0.0, -0.05)),
        spawn=sim_utils.CuboidCfg(
            size=(400.0, 400.0, 0.1),
            collision_props=sim_utils.CollisionPropertiesCfg(collision_enabled=True, contact_offset=0.001),
            visual_material=sim_utils.PreviewSurfaceCfg(diffuse_color=(0.30, 0.33, 0.38), roughness=0.85),
            physics_material=sim_utils.RigidBodyMaterialCfg(static_friction=1.6, dynamic_friction=1.2)))
    light = AssetBaseCfg(prim_path='/World/Light',
                         spawn=sim_utils.DistantLightCfg(intensity=3800.0, color=(0.9, 0.9, 0.92)))
    robot = ArticulationCfg(
        prim_path='{ENV_REGEX_NS}/Robot',
        spawn=sim_utils.UsdFileCfg(
            usd_path=MyArgs.usd, activate_contact_sensors=True,
            collision_props=sim_utils.CollisionPropertiesCfg(collision_enabled=True, contact_offset=0.001,
                                                             rest_offset=0.0),
            articulation_props=sim_utils.ArticulationRootPropertiesCfg(
                enabled_self_collisions=False, solver_position_iteration_count=16,
                solver_velocity_iteration_count=2),
            rigid_props=sim_utils.RigidBodyPropertiesCfg(disable_gravity=False,
                                                        max_depenetration_velocity=1.0)),
        # The USD already authors the chassis at its neutral z.  Scene translation must therefore
        # start at zero; adding SPAWN_Z here used to double the root height to ~0.598 m.
        init_state=ArticulationCfg.InitialStateCfg(pos=(0.0, 0.0, 0.0),
                                                  joint_pos={'.*': 0.0}, joint_vel={'.*': 0.0}),
        soft_joint_pos_limit_factor=1.0,
        actuators={
            'legs': ImplicitActuatorCfg(joint_names_expr=['.*_hip', '.*_knee'], effort_limit_sim=40.0,
                                        velocity_limit_sim=1000.0, stiffness=0.0, damping=0.2,
                                        armature=0.025, friction=0.0),
            'wheels': ImplicitActuatorCfg(joint_names_expr=['.*wheel_spin'], effort_limit_sim=6.0,
                                          velocity_limit_sim=1000.0, stiffness=0.0, damping=0.015,
                                          armature=WHEEL_ARMATURE, friction=0.0),
        })
    wheel_contacts = ContactSensorCfg(
        prim_path='{ENV_REGEX_NS}/Robot/.*', history_length=20, update_period=0.0,
        track_air_time=False)


@configclass
class RmCfg(DirectRLEnvCfg):
    decimation = 20                    # policy dt = 20 * 0.0005 = 0.01 s  (100 Hz, as delivered)
    episode_length_s = 20.0
    action_space = gspaces.Box(-1.0, 1.0, shape=(6,), dtype=np.float32)
    observation_space = gspaces.Box(
        -np.inf, np.inf,
        shape=(44 if MyArgs.jump_curriculum else (41 if MyArgs.skills else 39),),
        dtype=np.float32)
    state_space = 0
    sim = sim_utils.SimulationCfg(dt=0.0005, device=Args.device, render_interval=20,
                                  use_fabric=True)
    scene = SceneCfg(num_envs=MyArgs.num_envs,
                     env_spacing=8.0 if (MyArgs.field and MyArgs.skills) else
                                 (6.4 if MyArgs.field else 3.0))
    cmd = MyArgs.cmd
    field = MyArgs.field
    skills = MyArgs.skills
    terrain_all = MyArgs.terrain_all
    obstacle_focus = MyArgs.obstacle_focus
    focus_profile = MyArgs.focus_profile
    jump_curriculum = MyArgs.jump_curriculum
    curriculum_base_iter = MyArgs.curriculum_base_iter
    assist_start_iter = MyArgs.assist_start_iter
    assist_end_iter = MyArgs.assist_end_iter
    assist_prob_start = MyArgs.assist_prob_start
    assist_vx = MyArgs.assist_vx
    assist_vz = MyArgs.assist_vz
    steps_per_env = MyArgs.steps_per_env
    eval_only = MyArgs.eval_only
    yaw_cmd = MyArgs.yaw_cmd
    yaw_ramp_iters = MyArgs.yaw_ramp_iters
    hold_iters = MyArgs.hold_iters
    wheel_curve = MyArgs.wheel_curve
    wheel_stall = MyArgs.wheel_stall if MyArgs.wheel_stall is not None else WHEEL_STALL_DEFAULT
    wheel_noload = MyArgs.wheel_noload if MyArgs.wheel_noload is not None else WHEEL_NOLOAD_DEFAULT
    wheel_knee = MyArgs.wheel_knee if MyArgs.wheel_knee is not None else WHEEL_KNEE_DEFAULT
    wheel_velocity = MyArgs.wheel_velocity
    wheel_vel_scale = MyArgs.wheel_vel_scale
    wheel_vel_kd = MyArgs.wheel_vel_kd
    spin_pure = MyArgs.spin_pure
    spin_band = MyArgs.spin_band
    spin_weight = MyArgs.spin_weight
    spin_rate_weight = MyArgs.spin_rate_weight
    spin_product_weight = MyArgs.spin_product_weight
    spin_pivot = MyArgs.spin_pivot
    gyro_posture_relax = MyArgs.gyro_posture_relax
    gyro_stance_weight = MyArgs.gyro_stance_weight
    seed = 42


class RmSerialEnv(DirectRLEnv):
    """Torque-interface PPO task: reward = velocity tracking + upright + height - effort - power."""

    cfg: RmCfg

    def _setup_scene(self):
        # NOTE: DirectRLEnv already built self.scene from cfg.scene before calling us, so we only
        # grab handles here (spawning the scene again would collide on /World/Ground).
        # asset data only exists after sim.reset(), so here we only take the handle
        self.robot = self.scene['robot']
        self.wheel_contacts = self.scene['wheel_contacts']

    def _init_buffers(self):
        if hasattr(self, 'command'):
            return
        names = list(self.robot.data.joint_names)
        print('[env] asset joints (%d):' % len(names), names, flush=True)
        self.motor_ids = [names.index(n) for n in SERIAL_MOTORS]
        self.nj = len(names)
        bn = list(self.robot.data.body_names)
        self.wheel_body = [bn.index(n) for n in ('left_wheel', 'right_wheel')]
        self.wheel_contact_ids, wheel_contact_names = self.wheel_contacts.find_sensors(
            ['left_wheel', 'right_wheel'], preserve_order=True)
        # The 小陀螺 has to pivot about the wheel axle, not about the chassis origin: in the
        # delivered neutral pose the axle sits 197.75 mm BEHIND the origin, so a yaw rate of
        # 12.6 rad/s drags the origin sideways at 2.5 m/s.  Scoring the origin as "moving" is
        # what pinned spin_rate_ratio at 0.03 for thousands of iterations -- the policy was
        # right and the reward was asking for a kinematically impossible motion.
        try:
            self.wheel_body_ids, _wheel_body_names = self.robot.find_bodies(
                ['left_wheel', 'right_wheel'])
            if len(self.wheel_body_ids) != 2:
                raise RuntimeError(str(_wheel_body_names))
        except Exception as ex:      # pragma: no cover - keeps a bad prim name from
            print('[warn] wheel-axle pivot unavailable, falling back to root: %s' % ex,
                  flush=True)         #         eating a 90 s Isaac startup
            self.wheel_body_ids = None
            if self.cfg.spin_pivot == 'wheel':
                self.cfg.spin_pivot = 'root'
        if wheel_contact_names != ['left_wheel', 'right_wheel']:
            raise RuntimeError('wheel contact sensors resolved incorrectly: %s' % wheel_contact_names)
        self.lim = LIM.to(self.device)
        # The imported USD puts every BODY frame ~spawn_height above the articulation root, so
        # never compare body z against an absolute number - use root-relative geometry instead
        # (frame independent).  This is also why the legs looked "upside down" on screen: the
        # absolute z of a wheel is ~0.36 m even while the tyre is exactly on the floor.
        bn2 = self.robot.data.body_names
        self.chassis_idx = bn2.index('chassis')
        rz = self.robot.data.root_pos_w[:, 2].clone()
        w0 = self.robot.data.body_pos_w[:, self.wheel_body[0], 2].clone()
        w1 = self.robot.data.body_pos_w[:, self.wheel_body[1], 2].clone()
        wmin = torch.minimum(w0, w1)
        self.wheel_below_root = float((rz - wmin).mean().item())
        # z_ref is the *world-space root-link z* that puts the tyre on the floor.  InitialStateCfg
        # applies its translation to the USD's authored root transform, whereas the runtime state
        # writer expects an absolute root-link pose.  Subtracting z_ref here used to write z=0,
        # bury the wheels 0.234 m below the floor, and terminate every episode after one step.
        self.z_ref = self.wheel_below_root + WHEEL_RADIUS
        self.spawn_z = self.z_ref
        self.h_target = self.z_ref
        print('[env] spawn frame check: root z %.4f wheel z %.4f => wheel %.4f m BELOW root '
              '(MJCF neutral 0.2295) upright=%s ; write root-link z %.4f so the tyres touch'
              % (float(rz.mean()), float(wmin.mean()), self.wheel_below_root,
                 bool(self.wheel_below_root > 0.1), self.spawn_z), flush=True)
        n = self.cfg.scene.num_envs
        self.command = torch.zeros(n, device=self.device)
        self.yaw_command = torch.zeros(n, device=self.device)
        self.jump_flag = torch.zeros(n, device=self.device)
        self.prev_jump_flag = torch.zeros(n, dtype=torch.bool, device=self.device)
        self.jump_takeoff_z = torch.full((n,), self.spawn_z, device=self.device)
        # 0 idle, 1 push, 2 flight, 3 landing.  Explicit phases remove the ambiguity of the
        # previous single jump bit while preserving every one of the original 41 observations.
        self.jump_phase = torch.zeros(n, dtype=torch.long, device=self.device)
        self.jump_phase_time = torch.zeros(n, device=self.device)
        self.jump_ref_vz = torch.zeros(n, device=self.device)
        self.jump_cooldown = torch.zeros(n, device=self.device)
        self.jump_airborne_seen = torch.zeros(n, dtype=torch.bool, device=self.device)
        self.jump_assist_selected = torch.zeros(n, dtype=torch.bool, device=self.device)
        self.jump_assisted_episode = torch.zeros(n, dtype=torch.bool, device=self.device)
        self.jump_assist_event = torch.zeros(n, device=self.device)
        # Evaluation keeps the progressive main-course gates separate.  An aggregate traversal
        # number can hide a policy that clears the stairs but never reaches either slope.
        self.eval_success_counts = torch.zeros(7, dtype=torch.long, device=self.device)
        self.eval_episode_counts = torch.zeros(7, dtype=torch.long, device=self.device)
        self.command_age = torch.zeros(n, dtype=torch.long, device=self.device)
        self.jump_clock = torch.randint(0, 800, (n,), device=self.device)
        # A deterministic split keeps incompatible objectives out of the same environment.
        env_index = torch.arange(n, device=self.device)
        if self.cfg.obstacle_focus:
            # Profiles change only the training population, never the observation/action contract.
            # A 32-slot layout keeps every retained skill and all four progressive course gates in
            # each batch while allowing the post-evaluation supervisor to target a weak family.
            slot = env_index % 32
            profile = self.cfg.focus_profile
            if profile == 'jump':
                # 6.25% gyro, 6.25% turn, 75% gap/launch, 12.5% traversal.
                self.skill_mode = torch.full_like(slot, 3)
                self.skill_mode[slot < 2] = slot[slot < 2]
                self.skill_mode[(slot >= 2) & (slot < 4)] = 2
                self.skill_mode[slot >= 28] = 4 + (slot[slot >= 28] - 28)
            elif profile == 'traverse':
                # 6.25% gyro, 6.25% turn, 25% gap/launch, 62.5% stairs/slopes.
                self.skill_mode = torch.full_like(slot, 3)
                self.skill_mode[slot < 2] = slot[slot < 2]
                self.skill_mode[(slot >= 2) & (slot < 4)] = 2
                self.skill_mode[slot >= 12] = 4 + ((slot[slot >= 12] - 12) % 4)
            elif profile == 'gyro':
                # 50% gyro, 25% turn, 12.5% gap/launch, 12.5% traversal.
                self.skill_mode = torch.full_like(slot, 3)
                self.skill_mode[slot < 16] = slot[slot < 16] % 2
                self.skill_mode[(slot >= 16) & (slot < 24)] = 2
                self.skill_mode[slot >= 28] = 4 + (slot[slot >= 28] - 28)
            else:
                # 12.5% gyro, 12.5% turn, 50% gap/launch, 25% traversal.
                self.skill_mode = torch.full_like(slot, 3)
                self.skill_mode[slot < 4] = slot[slot < 4] % 2
                self.skill_mode[(slot >= 4) & (slot < 8)] = 2
                self.skill_mode[slot >= 24] = 4 + ((slot[slot >= 24] - 24) % 4)
        else:
            # 25% gyro, 12.5% turn, 12.5% jump/stair and 50% walk/run.
            self.skill_mode = env_index % 8
        self.course_variant = torch.zeros(n, dtype=torch.long, device=self.device)
        if self.cfg.terrain_all:
            gyro_ids = torch.nonzero(self.skill_mode < 2, as_tuple=False).squeeze(-1)
            self.course_variant[gyro_ids] = 3 + (
                torch.arange(gyro_ids.numel(), device=self.device) % 3)
            jump_ids = torch.nonzero(self.skill_mode == 3, as_tuple=False).squeeze(-1)
            self.course_variant[jump_ids] = 1 + (
                torch.arange(jump_ids.numel(), device=self.device) % 2)
        self._sample_commands(torch.arange(n, device=self.device))
        self.prev_action = torch.zeros(n, 6, device=self.device)
        self.torques = torch.zeros(n, 6, device=self.device)
        self._episode_sums = {
            key: torch.zeros(n, device=self.device)
            for key in ('tracking', 'yaw_tracking', 'gyro_wide', 'spin_hold', 'spin_rate', 'spin_product',
                        'upright', 'level', 'height',
                        'jump_progress', 'jump_airborne', 'jump_vz_tracking', 'jump_upward',
                        'landing_soft', 'forward_progress',
                        'lateral', 'ang_xy', 'gyro_stance',
                        'terrain_success', 'gap_success', 'launch_success', 'traverse_success',
                        'unassisted_success',
                        'action', 'action_rate', 'power')
        }

    def _sample_commands(self, env_ids):
        """Sample mutually compatible stage-2 commands without asking one robot to sprint and spin."""
        n = len(env_ids)
        if n == 0:
            return
        if not self.cfg.skills:
            self.command[env_ids] = (torch.rand(n, device=self.device) * 2 - 1) * self.cfg.cmd
            self.yaw_command[env_ids] = 0.0
            self.command_age[env_ids] = 0
            return
        mode = self.skill_mode[env_ids]
        rnd = torch.rand(n, 5, device=self.device)
        # Start locomotion at a speed that a balancing policy can discover, then open the full
        # sprint range over about 2,500 PPO updates (12 control steps/update).  Asking a policy
        # that still stands in place for 1.8 m/s immediately produced a high-return local optimum:
        # it ignored the velocity command and collected the posture rewards instead.
        drive_cap = min(float(self.cfg.cmd),
                        0.65 + max(0.0, float(self.cfg.cmd) - 0.65) *
                        getattr(self, '_iter', 0) / 30000.0)
        speed = 0.25 + rnd[:, 0] * max(0.25, drive_cap - 0.25)
        speed = torch.where(rnd[:, 1] < 0.15, -speed, speed)
        vx = speed
        wz = (rnd[:, 2] * 2.0 - 1.0) * 1.8
        if self.cfg.terrain_all:
            # Dedicated traversal environments must actually meet the narrow measured feature;
            # large random yaw/reverse commands made them drive around the stairs and ramps.
            traverse = mode >= 4
            if self.cfg.jump_curriculum:
                traverse_cap = min(float(self.cfg.cmd), 1.40)
                traverse_vx = 0.75 + rnd[:, 0] * max(0.15, traverse_cap - 0.75)
            else:
                traverse_vx = 0.35 + rnd[:, 0] * max(0.20, drive_cap - 0.35)
            vx = torch.where(traverse, traverse_vx, vx)
            wz = torch.where(traverse, (rnd[:, 2] * 2.0 - 1.0) * 0.25, wz)
        # Dedicated turning environments use modest translation and stronger curvature.
        turn = mode == 2
        vx = torch.where(turn, -0.25 + rnd[:, 0] * 0.9, vx)
        wz = torch.where(turn, (rnd[:, 2] * 2.0 - 1.0) * 4.0, wz)
        # Gyro curriculum opens from 4 to yaw_cmd over roughly 2,000 PPO iterations at 12 steps.
        gyro = mode < 2
        yaw_start = 8.0 if self.cfg.terrain_all else 4.0
        yaw_cap = min(float(self.cfg.yaw_cmd),
                      yaw_start + (float(self.cfg.yaw_cmd) - yaw_start) *
                      getattr(self, '_iter', 0) / max(1.0, float(self.cfg.yaw_ramp_iters)))
        gyro_mag = 3.0 + rnd[:, 3] * max(0.1, yaw_cap - 3.0)
        gyro_wz = torch.where(rnd[:, 4] < 0.5, -gyro_mag, gyro_mag)
        vx = torch.where(gyro, torch.zeros_like(vx), vx)
        wz = torch.where(gyro, gyro_wz, wz)
        # Jump/stair environments approach the obstacle almost straight at walking/running speed.
        jump = mode == 3
        if self.cfg.jump_curriculum:
            # At the old 0.6--0.9 m/s approach speed the 0.37 m gap is not physically reachable
            # during a useful ballistic arc.  Dedicated jump lanes train at running speed.
            jump_speed = 1.05 + rnd[:, 0] * max(0.10, float(self.cfg.cmd) - 1.05)
            vx = torch.where(jump, jump_speed, vx)
        else:
            jump_floor = min(0.45, drive_cap)
            vx = torch.where(jump, jump_floor + rnd[:, 0] * max(0.20, drive_cap - jump_floor), vx)
        wz = torch.where(jump, (rnd[:, 2] * 2.0 - 1.0) * 0.35, wz)
        self.command[env_ids] = vx
        self.yaw_command[env_ids] = wz
        self.command_age[env_ids] = 0

    def _update_skill_schedule(self):
        if not self.cfg.skills:
            return
        self.command_age += 1
        expired = torch.nonzero(self.command_age >= 500, as_tuple=False).squeeze(-1)
        self._sample_commands(expired)
        self.jump_clock = (self.jump_clock + 1) % 800
        local_x = self.robot.data.root_pos_w[:, 0] - self.scene.env_origins[:, 0]
        jump_env = self.skill_mode == 3
        if self.cfg.jump_curriculum and self.cfg.terrain_all:
            # Main-course environments also need an explicit phase to clear the two 0.10 m
            # risers; the wheel radius is only about 0.073 m.
            jump_env |= self.skill_mode >= 4
        periodic = (self.jump_clock >= 500) & (self.jump_clock < 580)
        # Raise the jump request just before the first stair as well as periodically.  This
        # explicitly trains take-off/landing instead of hoping a velocity policy invents it.
        obstacle = (local_x > 0.62) & (local_x < 1.10)
        if self.cfg.terrain_all:
            cv = self.course_variant
            gap_trigger = FIELD_INFO.get('gap_trigger', (0.05, 0.92))
            launch_trigger = FIELD_INFO.get('launch_trigger', (0.30, 1.25))
            obstacle = (((cv == 1) & (local_x > gap_trigger[0]) &
                         (local_x < gap_trigger[1])) |
                        ((cv == 2) & (local_x > launch_trigger[0]) &
                         (local_x < launch_trigger[1])) |
                        ((cv == 0) & (local_x > 0.62) & (local_x < 1.10)))
        active = jump_env & (periodic | obstacle)
        if not self.cfg.jump_curriculum:
            started = active & ~self.prev_jump_flag
            self.jump_takeoff_z[started] = self.robot.data.root_pos_w[started, 2]
            self.jump_flag[:] = active.float()
            self.prev_jump_flag[:] = active
            return

        # The broad `active` window is useful for shaping but much too early for takeoff.  Enter
        # the push phase near the gap edge or launch-ramp lip instead.
        takeoff_request = active
        if self.cfg.terrain_all:
            gap_takeoff = float(FIELD_INFO.get('gap_takeoff', 0.48))
            launch_takeoff = float(FIELD_INFO.get('launch_takeoff', 1.07))
            stair_takeoff = float(FIELD_INFO.get('stair_takeoff', 0.90))
            takeoff_request = (((self.course_variant == 1) & (local_x >= gap_takeoff) &
                                (local_x <= gap_takeoff + 0.14)) |
                               ((self.course_variant == 2) & (local_x >= launch_takeoff) &
                                (local_x <= launch_takeoff + 0.18)) |
                               ((self.course_variant == 0) & (local_x >= stair_takeoff) &
                                (local_x <= stair_takeoff + 0.18))) & jump_env

        self.jump_assist_event.zero_()
        self.jump_cooldown -= torch.minimum(
            self.jump_cooldown, torch.full_like(self.jump_cooldown, self.step_dt))
        phase_active = self.jump_phase > 0
        self.jump_phase_time[phase_active] += self.step_dt
        enter = (self.jump_phase == 0) & takeoff_request & (self.jump_cooldown <= 0.0)
        if torch.any(enter):
            self.jump_phase[enter] = 1
            self.jump_phase_time[enter] = 0.0
            self.jump_takeoff_z[enter] = self.robot.data.root_pos_w[enter, 2]
            self.jump_airborne_seen[enter] = False
            probability = self._jump_assist_probability()
            self.jump_assist_selected[enter] = (
                torch.rand(int(enter.sum().item()), device=self.device) < probability)
            self.jump_assisted_episode[enter] = (
                self.jump_assisted_episode[enter] | self.jump_assist_selected[enter])

        push = self.jump_phase == 1
        self.jump_ref_vz[push] = self.cfg.assist_vz * torch.clamp(
            self.jump_phase_time[push] / 0.12, 0.0, 1.0)
        release = push & (self.jump_phase_time >= 0.12)
        if torch.any(release):
            self._apply_jump_velocity_assist(release & self.jump_assist_selected)
            self.jump_phase[release] = 2
            self.jump_phase_time[release] = 0.0

        flight = self.jump_phase == 2
        self.jump_ref_vz[flight] = torch.clamp(
            self.cfg.assist_vz - 9.81 * self.jump_phase_time[flight], -1.5,
            self.cfg.assist_vz)
        contacts = getattr(self, '_contacts', torch.ones(self.num_envs, 2, device=self.device))
        airborne = contacts.mean(dim=1) < 0.5
        self.jump_airborne_seen |= (self.jump_phase >= 2) & airborne
        descending = (flight & self.jump_airborne_seen &
                      (self.robot.data.root_lin_vel_w[:, 2] <= 0.0))
        if torch.any(descending):
            self.jump_phase[descending] = 3
            self.jump_phase_time[descending] = 0.0

        landing = self.jump_phase == 3
        self.jump_ref_vz[landing] = -0.35
        landed = landing & self.jump_airborne_seen & torch.all(contacts > 0.5, dim=1)
        timed_out = (self.jump_phase > 0) & (self.jump_phase_time > 0.75)
        finished = landed | timed_out
        if torch.any(finished):
            self.jump_phase[finished] = 0
            self.jump_phase_time[finished] = 0.0
            self.jump_ref_vz[finished] = 0.0
            self.jump_cooldown[finished] = 0.30
            self.jump_assist_selected[finished] = False
        self.jump_flag[:] = (self.jump_phase > 0).float()
        self.prev_jump_flag[:] = self.jump_flag.bool()

    def _global_training_iteration(self):
        """Approximate runner iteration without coupling the environment to rsl_rl internals."""
        return int(self.cfg.curriculum_base_iter +
                   getattr(self, '_iter', 0) // max(1, int(self.cfg.steps_per_env)))

    def _jump_assist_probability(self):
        if self.cfg.eval_only:
            return 0.0
        start = int(self.cfg.assist_start_iter)
        end = int(self.cfg.assist_end_iter)
        if end <= start:
            return 0.0
        progress = (self._global_training_iteration() - start) / float(end - start)
        progress = min(1.0, max(0.0, progress))
        return max(0.0, float(self.cfg.assist_prob_start) * (1.0 - progress))

    def _apply_jump_velocity_assist(self, mask):
        """One-shot teacher impulse whose sampling probability reaches zero before validation."""
        env_ids = torch.nonzero(mask, as_tuple=False).squeeze(-1)
        if env_ids.numel() == 0:
            return
        root_velocity = self.robot.data.root_com_vel_w
        root_velocity = root_velocity.torch if hasattr(root_velocity, 'torch') else root_velocity
        root_velocity = root_velocity[env_ids].clone()
        root_velocity[:, 0] = torch.maximum(
            root_velocity[:, 0], torch.full_like(root_velocity[:, 0], self.cfg.assist_vx))
        root_velocity[:, 2] = torch.maximum(
            root_velocity[:, 2], torch.full_like(root_velocity[:, 2], self.cfg.assist_vz))
        self.robot.write_root_com_velocity_to_sim_index(
            root_velocity=root_velocity, env_ids=env_ids)
        self.jump_assist_event[env_ids] = 1.0

    def _pre_physics_step(self, actions):
        self._update_skill_schedule()
        a = actions.clamp(-1.0, 1.0)
        if self.cfg.hold_iters and getattr(self, '_iter', 0) < self.cfg.hold_iters:
            # A PD on q=0 would be zero torque (the delivered neutral IS q=0) and the chassis is a
            # two-wheel balancer, so it would just fall over on screen.  During the warm phase we
            # re-assert the neutral state every policy step: the viewport shows 1024 robots stood
            # up on the measured map, and the policy then starts from a clean standing pose.
            self._write_neutral(torch.arange(self.num_envs, device=self.device))
            a = torch.zeros_like(a)
            self._held = True
        else:
            self._held = False
        self._iter = getattr(self, '_iter', 0) + 1
        if hasattr(self, 'last_raw'):
            self.prev_action = self.last_raw * self.lim
        self.last_raw = a
        self.torques = a * self.lim

    def _apply_action(self):
        v_all = self.robot.data.joint_vel[:, self.motor_ids]
        v = v_all[:, LEG_IDX]
        lo = (-MOTOR['envelope_intercept_nm'] - MOTOR['envelope_slope_nm_s_rad'] * v).clamp(-40.0, 40.0)
        hi = (MOTOR['envelope_intercept_nm'] - MOTOR['envelope_slope_nm_s_rad'] * v).clamp(-40.0, 40.0)
        t = self.torques.clone()
        if self.cfg.wheel_velocity:
            # Speed servo on the wheel channels: the action means 'hold this wheel speed', and
            # the servo asks for the torque that keeps it there.  Everything downstream (the
            # DM3519 envelope, the effort clip, the saturation metric) is unchanged.
            want = t[:, WHEEL] * float(self.cfg.wheel_vel_scale)
            t[:, WHEEL] = ((want - v_all[:, WHEEL]) * float(self.cfg.wheel_vel_kd)).clamp(
                -float(self.lim[WHEEL].max()), float(self.lim[WHEEL].max()))
        t[:, LEG_IDX] = torch.maximum(lo, torch.minimum(hi, t[:, LEG_IDX]))
        if self.cfg.wheel_curve:
            # DM3519 + 15.8 wheel envelope, driving direction only: a current-limited plateau up to
            # the knee speed, then a linear voltage-limited fall to no-load.  Without this the wheels
            # are ideal 6 N.m sources at any speed and the sim invents a 小陀螺 the motor cannot turn.
            # 2 rev/s needs 47.4 rad/s per wheel, i.e. past the 44.0 rad/s knee -> only ~4.5 N.m left.
            w = v_all[:, WHEEL]
            nl = max(1.0, float(self.cfg.wheel_noload))
            kn = min(max(0.0, float(self.cfg.wheel_knee)), nl * 0.999)
            mag = float(self.cfg.wheel_stall) * ((nl - w.abs()) / max(1e-6, nl - kn)).clamp(min=0.0, max=1.0)
            full = self.lim[WHEEL].unsqueeze(0).expand_as(mag)
            driving = (t[:, WHEEL] * w) > 0.0
            lim = torch.where(driving, mag, full)
            tw = t[:, WHEEL]
            t[:, WHEEL] = torch.maximum(torch.minimum(tw, lim), -lim)
            self._wheel_sat = float((tw.abs() > lim).float().mean())
            self._wheel_lim = lim
        self.robot.set_joint_effort_target_index(target=t, joint_ids=self.motor_ids)

    def _gyro_probe(self):
        '''Print the drivetrain's own bookkeeping on the gyro lanes.

        spin_pure_v2 saturated the wheel torque envelope 23-29 pct of the time -- which means the
        wheels really do reach near no-load speed a quarter of the time -- yet the chassis yawed at
        only ~0.5 rad/s.  Those two facts can only coexist if the wheels are (a) spinning the SAME
        direction (driving, not spinning), (b) slipping, or (c) being held by the legs/terrain.
        Signed left/right wheel speed plus the no-slip yaw prediction separates the three.
        '''
        gyro = (self.skill_mode < 2)
        if not bool(gyro.any()):
            return
        wv = self.robot.data.joint_vel[:, self.motor_ids][:, WHEEL][gyro]
        wz = self.robot.data.root_ang_vel_b[:, 2][gyro]
        cmd = self.yaw_command[gyro]
        s = torch.sign(cmd)
        # Half the gyro lanes are commanded clockwise, half counter-clockwise, so a plain signed
        # mean cancels to zero -- the first version of this probe read "actual yaw 0.00" while the
        # robots were in fact spinning both ways.  Everything below is per-env, then aligned to
        # the command sign so the two halves add up instead of cancelling.
        wl_a = (wv[:, 0] * s).mean()          # commanded-forward wheel speed
        wr_a = (wv[:, 1] * s).mean()          # should be negative for a real 小陀螺
        pred = WHEEL_RADIUS * (wv[:, 0] - wv[:, 1]) / (2.0 * _HALF_TRACK_M)
        both = ((wv[:, 0] * wv[:, 1]) < 0.0).float().mean()
        cg = self._contacts[gyro]
        grounded = ((cg[:, 0] > 0.5) & (cg[:, 1] > 0.5)).float().mean()
        fast = (wv.abs().max(dim=1).values > 8.0).float().mean()
        print('[gyro] it %-6d aligned wheelL %+.2f wheelR %+.2f rad/s | |wheel| %.2f/%.2f | '
              'counter-rotating %.0f pct | both-grounded %.0f pct | wheel-fast>8 %.0f pct | '
              'no-slip yaw %+.2f | actual yaw %+.2f | slip deficit %+.2f | '
              'mean |yaw| %.2f | |cmd| %.2f | sat %.2f'
              % (self._iter, wl_a, wr_a, wv[:, 0].abs().mean(), wv[:, 1].abs().mean(),
                 100.0 * float(both), 100.0 * float(grounded), 100.0 * float(fast),
                 (pred * s).mean(), (wz * s).mean(), (pred - wz).abs().mean(),
                 wz.abs().mean(), cmd.abs().mean(),
                 float(getattr(self, '_wheel_sat', 0.0))), flush=True)

    def _leg_q(self):
        q = self.robot.data.joint_pos[:, self.motor_ids]
        return q

    def _get_observations(self):
        d = self.robot.data
        q = self._leg_q()
        v = self.robot.data.joint_vel[:, self.motor_ids]
        legq = q[:, LEG_IDX]
        knee_q = q[:, [1, 4]]
        knee_v = v[:, [1, 4]]
        diff = q[:, [1, 4]] - q[:, [0, 3]]
        contact_forces = self.wheel_contacts.data.net_forces_w_history.torch[:, :, self.wheel_contact_ids]
        contacts = (torch.linalg.norm(contact_forces, dim=-1).amax(dim=1) > 1.0).float()
        self._up = d.projected_gravity_b[:, 2]
        self._vx = d.root_lin_vel_b[:, 0]
        self._h = d.root_pos_w[:, 2].clone().reshape(-1)
        wheel_z = d.body_pos_w[:, self.wheel_body, 2]
        self._posture_h = self._h - wheel_z.mean(dim=1)
        self._contacts = contacts
        # Absolute world z changes by 0.18--0.42 m on platforms and ramps and made the policy
        # interpret a perfectly normal stance as an over-height failure.  Keep the legacy slot,
        # but make its terrain-mode meaning root-to-wheel posture height (near 0.23 m everywhere).
        height_obs = self._posture_h if self.cfg.skills else self._h
        obs = torch.cat([d.root_lin_vel_b, d.root_ang_vel_b, d.projected_gravity_b,
                         torch.sin(legq), torch.cos(legq), v * 0.1, knee_q, knee_v * 0.1, diff,
                         height_obs[:, None], self.command[:, None], contacts,
                         self.torques / self.lim], dim=-1)
        if self.cfg.skills:
            # Append normalized yaw command and an explicit jump request.  Keeping the original
            # 39 slots untouched lets the stage-1 actor warm-start while the two new input columns
            # are initialized cleanly by warm_start_compatible().
            obs = torch.cat([obs, (self.yaw_command / max(1.0, self.cfg.yaw_cmd))[:, None],
                             self.jump_flag[:, None]], dim=-1)
        if self.cfg.jump_curriculum:
            phase = self.jump_phase.float() / 3.0
            phase_time = torch.clamp(self.jump_phase_time / 0.75, 0.0, 1.0)
            ref_vz = self.jump_ref_vz / max(1.0, float(self.cfg.assist_vz))
            obs = torch.cat([obs, phase[:, None], phase_time[:, None], ref_vz[:, None]], dim=-1)
        expected = 44 if self.cfg.jump_curriculum else (41 if self.cfg.skills else 39)
        if obs.shape[-1] != expected:
            raise RuntimeError('observation contract is %d-D, got %d' % (expected, obs.shape[-1]))
        return {'policy': obs, 'critic': obs}

    def _get_rewards(self):
        tracking = torch.exp(-((self._vx - self.command) / 0.5) ** 2)
        upright = torch.clamp(-self._up, 0.0, 1.0)
        height = torch.exp(-((self._h - TARGET_HEIGHT) / 0.09) ** 2)
        a = self.torques / self.lim
        act = a.pow(2).sum(-1)
        rate = (a - self.prev_action / self.lim).pow(2).sum(-1)
        power = (self.torques * self.robot.data.joint_vel[:, self.motor_ids]).abs().sum(-1)
        if getattr(self, '_iter', 0) % 200 == 0:
            print('[env] it %-6d h %.3f..%.3f m  upright %.2f  vx %+.2f/%+.2f  '
                  'wz %+.2f/%+.2f  %s' % (
                self._iter, self._h.min(), self._h.max(), (-self._up > 0.86).float().mean(),
                self._vx.mean(), self.command.mean(),
                self.robot.data.root_ang_vel_b[:, 2].mean(), self.yaw_command.mean(),
                '(PD hold)' if getattr(self, '_held', False) else ''), flush=True)
        zeros = torch.zeros_like(tracking)
        if not self.cfg.skills:
            terms = {
                'tracking': 1.5 * tracking * self.step_dt,
                'yaw_tracking': zeros,
                'gyro_wide': zeros,
                'upright': 1.5 * upright * self.step_dt,
                'level': zeros,
                'height': height * self.step_dt,
                'jump_progress': zeros,
                'jump_airborne': zeros,
                'jump_vz_tracking': zeros,
                'jump_upward': zeros,
                'landing_soft': zeros,
                'lateral': zeros,
                'ang_xy': zeros,
                'gyro_stance': zeros,
                'terrain_success': zeros,
                'gap_success': zeros,
                'launch_success': zeros,
                'traverse_success': zeros,
                'unassisted_success': zeros,
                'action': -0.03 * act * self.step_dt,
                'action_rate': -0.02 * rate * self.step_dt,
                'power': -0.0005 * power * self.step_dt,
            }
        else:
            d = self.robot.data
            yaw_rate = d.root_ang_vel_b[:, 2]
            yaw_err = (yaw_rate - self.yaw_command).abs()
            gyro_mask = (self.skill_mode < 2).float()
            # Spinning fast and holding a textbook-flat chassis fight each other; this lets the gyro
            # lanes trade posture for yaw rate the way the real machine does.
            posture_scale = 1.0 - float(self.cfg.gyro_posture_relax) * gyro_mask
            # --spin-pure widens the yaw kernel on gyro lanes only: at 12 rad/s command the old
            # sigma=1.5 kernel is already flat, so PPO had no gradient left to chase the spin.
            band = torch.full_like(yaw_err, 1.5)
            if self.cfg.spin_pure:
                band = torch.where(gyro_mask > 0.5, torch.full_like(yaw_err, self.cfg.spin_band), band)
            yaw_tracking = torch.exp(-((yaw_err / band) ** 2))
            gyro_wide = torch.clamp(1.0 - yaw_err / 7.0, min=0.0) * gyro_mask
            # A real 小陀螺 is pure yaw: the chassis centre must not travel.  Differential arc turning
            # also satisfies |yaw-cmd|, so the discriminator has to be the translation speed.
            if self.cfg.spin_pivot == 'wheel':
                root_pos = d.root_state_w[:, :3]
                axle = 0.5 * (d.body_pos_w[:, self.wheel_body_ids[0], :]
                              + d.body_pos_w[:, self.wheel_body_ids[1], :])
                r_w = axle - root_pos
                v_w = d.root_lin_vel_w + torch.cross(d.root_ang_vel_w, r_w, dim=-1)
                trans2 = v_w[:, 0].pow(2) + v_w[:, 1].pow(2)
            else:
                trans2 = d.root_lin_vel_b[:, 0].pow(2) + d.root_lin_vel_b[:, 1].pow(2)
            spin_hold = torch.exp(-trans2 / (0.25 ** 2)) * gyro_mask
            # ... and the robot must actually be spinning, otherwise spin_hold is farmed by standing
            # still with the wheels braked.
            spin_rate = torch.clamp(yaw_rate.abs() / self.yaw_command.abs().clamp(min=1.0),
                                    0.0, 1.2) * gyro_mask
            self._spin_trans = torch.sqrt(trans2)
            self._gyro_mask = gyro_mask
            self._spin_rate = spin_rate
            self._gyro_yaw_abs = yaw_rate.abs() * gyro_mask
            if getattr(self, '_iter', 0) % 200 == 0:
                self._gyro_probe()
            self._spin_hold = spin_hold
            # A 小陀螺 only exists through the tyres.  The probe above showed the wheels wound up
            # to ~13 rad/s while the chassis yawed at 0.25 rad/s and only ~70 pct of the time did
            # both wheels carry load: the policy was paying for wheel speed the ground could not
            # take.  Gate every spin term on BOTH tyres being grounded so an airborne wheel earns
            # nothing -- this is also what the real machine does (it cannot spin on one wheel).
            ground_gate = ((self._contacts[:, 0] > 0.5) &
                           (self._contacts[:, 1] > 0.5)).float()
            gravity_xy2 = d.projected_gravity_b[:, :2].pow(2).sum(-1)
            # A narrow-only kernel went nearly flat once locomotion leaned beyond five degrees,
            # so PPO learned to trade permanent chassis tilt for speed.  The coarse component
            # supplies a restoring gradient from larger lean angles; the fine component rewards
            # the user's strict normal-driving target around level.
            level_coarse = torch.exp(-gravity_xy2 / (0.18 ** 2))
            level_fine = torch.exp(-gravity_xy2 / (0.075 ** 2))
            level = 0.40 * level_coarse + 0.60 * level_fine
            # Root height in world coordinates rises on a stair, so it must not be compared to a
            # flat-floor constant.  Root-to-wheel height measures chassis posture on any terrain.
            posture = torch.exp(-((self._posture_h - self.wheel_below_root) / 0.065) ** 2)
            rise = self._h - self.jump_takeoff_z
            jump_progress = torch.clamp(rise / 0.10, 0.0, 1.2) * self.jump_flag
            airborne = (self._contacts.mean(dim=1) < 0.5).float()
            jump_airborne = airborne * self.jump_flag
            phase_active = ((self.jump_phase > 0).float()
                            if self.cfg.jump_curriculum else self.jump_flag)
            push_phase = ((self.jump_phase == 1).float()
                          if self.cfg.jump_curriculum else self.jump_flag)
            landing_phase = ((self.jump_phase == 3).float()
                             if self.cfg.jump_curriculum else zeros)
            vel_z = d.root_lin_vel_w[:, 2]
            jump_vz_tracking = (torch.exp(-((vel_z - self.jump_ref_vz) / 0.55) ** 2) *
                                phase_active)
            jump_upward = (torch.clamp(
                vel_z / max(0.5, float(self.cfg.assist_vz)), 0.0, 1.2) * push_phase)
            landing_soft = torch.exp(-(vel_z / 0.65) ** 2) * landing_phase
            # Yawing about the wheel axle (the only no-slip yaw centre a vehicle has) swings the
            # chassis sideways at omega x 0.198 m: 2.5 m/s of lateral velocity at 2 rev/s.  The
            # lateral penalty therefore had to be lifted on gyro lanes or it would have vetoed
            # the very motion spin_hold is now defined to allow.
            lateral_gate = 1.0 - gyro_mask if self.cfg.spin_pure else torch.ones_like(gyro_mask)
            lateral = d.root_lin_vel_b[:, 1].pow(2)
            ang_xy = d.root_ang_vel_b[:, :2].pow(2).sum(-1)
            q = self._leg_q()
            gyro_stance = ((q[:, 0] - q[:, 3]).pow(2) +
                           (q[:, 1] - q[:, 4]).pow(2)) * gyro_mask
            jump_gate = 1.0 - self.jump_flag
            # Dense signed progress prevents the stable-standing shortcut.  The exponential
            # tracking term alone has almost no gradient when the robot is far from its command.
            # This term remains bounded and reaches its maximum exactly at the requested speed.
            moving = (self.command.abs() > 0.10).float()
            aligned_speed = self._vx * torch.sign(self.command)
            forward_progress = torch.clamp(
                aligned_speed / self.command.abs().clamp(min=0.25), -1.0, 1.0) * moving
            tracking_weight = 2.0 + 8.0 * moving
            terms = {
                'tracking': tracking_weight * tracking * (0.6 + 0.4 * jump_gate) * self.step_dt,
                'yaw_tracking': 2.2 * yaw_tracking * (0.3 + 0.7 * jump_gate) * self.step_dt,
                'gyro_wide': 1.5 * gyro_wide * self.step_dt,
                'spin_hold': (self.cfg.spin_weight * spin_hold * ground_gate * self.step_dt) if self.cfg.spin_pure else zeros,
                'spin_rate': (self.cfg.spin_rate_weight * spin_rate * ground_gate * self.step_dt) if self.cfg.spin_pure else zeros,
                'spin_product': (self.cfg.spin_product_weight * spin_hold * spin_rate * ground_gate * self.step_dt)
                    if (self.cfg.spin_pure and self.cfg.spin_product_weight > 0.0) else zeros,
                'upright': 1.2 * upright * posture_scale * self.step_dt,
                'level': 7.0 * level * (0.5 + 0.5 * jump_gate) * posture_scale * self.step_dt,
                'height': 1.2 * posture * jump_gate * posture_scale * self.step_dt,
                'jump_progress': 6.0 * jump_progress * self.step_dt,
                'jump_airborne': 3.0 * jump_airborne * self.step_dt,
                'jump_vz_tracking': 5.0 * jump_vz_tracking * self.step_dt,
                'jump_upward': 4.0 * jump_upward * self.step_dt,
                'landing_soft': 2.0 * landing_soft * self.step_dt,
                'forward_progress': 3.0 * forward_progress * self.step_dt,
                'lateral': -0.30 * lateral * lateral_gate * self.step_dt,
                'ang_xy': -0.18 * ang_xy * self.step_dt,
                'gyro_stance': -float(self.cfg.gyro_stance_weight) * gyro_stance * self.step_dt,
                # A one-step crossing event must be comparable to a meaningful fraction of a
                # 20-second episode; the previous 4-point bonus was drowned by posture rewards.
                'terrain_success': 25.0 * getattr(self, '_course_done',
                                                   torch.zeros_like(tracking)).float(),
                # Logging-only entries are kept at zero here and accumulated below so they do
                # not accidentally add a second success bonus to the policy reward.
                'gap_success': zeros,
                'launch_success': zeros,
                'traverse_success': zeros,
                'unassisted_success': zeros,
                'action': -0.025 * act * self.step_dt,
                'action_rate': -0.015 * rate * (0.2 + 0.8 * jump_gate) * self.step_dt,
                'power': -0.00035 * power * (0.2 + 0.8 * jump_gate) * self.step_dt,
            }
        for key, value in terms.items():
            self._episode_sums[key] += value
        if self.cfg.terrain_all:
            done = getattr(self, '_course_done', torch.zeros_like(tracking)).float()
            self._episode_sums['gap_success'] += done * (self.course_variant == 1).float()
            self._episode_sums['launch_success'] += done * (self.course_variant == 2).float()
            self._episode_sums['traverse_success'] += done * (self.skill_mode >= 4).float()
            self._episode_sums['unassisted_success'] += (
                done * ((self.course_variant == 1) | (self.course_variant == 2)).float() *
                (~self.jump_assisted_episode).float())
        metrics_log = {
            'Metrics/height_m': self._h.mean(),
            'Metrics/posture_height_m': self._posture_h.mean(),
            'Metrics/upright_fraction': (-self._up > 0.86).float().mean(),
            'Metrics/level_5deg_fraction': (gravity_xy2 < math.sin(math.radians(5.0)) ** 2).float().mean()
                if self.cfg.skills else (-self._up > math.cos(math.radians(5.0))).float().mean(),
            'Metrics/wheel_contact_fraction': self._contacts.mean(),
            'Metrics/fallen_fraction': self._fallen.float().mean(),
            'Metrics/spin_translation_m_s': (self._spin_trans * self._gyro_mask).sum()
                / self._gyro_mask.sum().clamp(min=1.0)
                if (self.cfg.spin_pure and hasattr(self, '_gyro_mask')) else torch.zeros((), device=self.device),
            'Metrics/spin_rate_ratio': self._spin_rate.sum() / self._gyro_mask.sum().clamp(min=1.0)
                if (self.cfg.spin_pure and hasattr(self, '_gyro_mask')) else torch.zeros((), device=self.device),
            'Metrics/gyro_yaw_rate_rad_s': (self._gyro_yaw_abs.sum() / self._gyro_mask.sum().clamp(min=1.0))
                if (self.cfg.spin_pure and hasattr(self, '_gyro_mask')) else torch.zeros((), device=self.device),
            'Metrics/spin_hold_mean': self._spin_hold.mean()
                if (self.cfg.spin_pure and hasattr(self, '_spin_hold')) else torch.zeros((), device=self.device),
            'Metrics/wheel_torque_saturation': getattr(self, '_wheel_sat', 0.0),
            'Metrics/yaw_error_rad_s': (self.robot.data.root_ang_vel_b[:, 2] - self.yaw_command).abs().mean(),
            'Metrics/gyro_command_abs': self.yaw_command[self.skill_mode < 2].abs().mean()
                if self.cfg.skills else torch.zeros((), device=self.device),
            'Metrics/jump_airborne_fraction': ((self._contacts.mean(dim=1) < 0.5).float() * self.jump_flag).sum()
                / self.jump_flag.sum().clamp(min=1.0),
            'Metrics/jump_assist_probability': torch.tensor(
                self._jump_assist_probability() if self.cfg.jump_curriculum else 0.0,
                device=self.device),
            'Metrics/jump_assist_event_fraction': self.jump_assist_event.mean(),
            'Metrics/jump_push_fraction': (self.jump_phase == 1).float().mean(),
            'Metrics/jump_flight_fraction': (self.jump_phase == 2).float().mean(),
            'Metrics/course_success_fraction': getattr(
                self, '_course_done', torch.zeros_like(self._fallen)).float().mean(),
            'Metrics/gap_failure_fraction': getattr(
                self, '_gap_failed', torch.zeros_like(self._fallen)).float().mean(),
            'Metrics/traverse_progress_m': (
                (self.robot.data.root_pos_w[:, 0] - self.scene.env_origins[:, 0])[
                    self.skill_mode >= 4].mean() if self.cfg.terrain_all else
                torch.zeros((), device=self.device)),
            'Metrics/gap_progress_m': (
                (self.robot.data.root_pos_w[:, 0] - self.scene.env_origins[:, 0])[
                    self.course_variant == 1].mean() if self.cfg.terrain_all else
                torch.zeros((), device=self.device)),
            'Metrics/gap_vx_m_s': (
                self._vx[self.course_variant == 1].mean() if self.cfg.terrain_all else
                torch.zeros((), device=self.device)),
            'Metrics/gap_command_m_s': (
                self.command[self.course_variant == 1].mean() if self.cfg.terrain_all else
                torch.zeros((), device=self.device)),
            'Metrics/launch_progress_m': (
                (self.robot.data.root_pos_w[:, 0] - self.scene.env_origins[:, 0])[
                    self.course_variant == 2].mean() if self.cfg.terrain_all else
                torch.zeros((), device=self.device)),
            'Metrics/launch_vx_m_s': (
                self._vx[self.course_variant == 2].mean() if self.cfg.terrain_all else
                torch.zeros((), device=self.device)),
            'Metrics/launch_command_m_s': (
                self.command[self.course_variant == 2].mean() if self.cfg.terrain_all else
                torch.zeros((), device=self.device)),
            'Metrics/moving_vx_m_s': (
                self._vx[self.command.abs() > 0.10].mean() if self.cfg.skills else
                self._vx.mean()),
            'Metrics/traverse_vx_m_s': (
                self._vx[self.skill_mode >= 4].mean() if self.cfg.terrain_all else
                torch.zeros((), device=self.device)),
        }
        self.extras.setdefault('log', {}).update(metrics_log)
        return torch.stack(list(terms.values())).sum(0)

    def _get_dones(self):
        finite = torch.isfinite(self._h) & torch.isfinite(self._vx)
        if self.cfg.skills:
            # Terrain raises world z; terminate on collapsed posture/attitude, not absolute z.
            fallen = (self._posture_h < 0.105) | (-self._up < 0.5) | ~finite
        else:
            fallen = (self._h < 0.22) | (-self._up < 0.5) | ~finite
        self._course_done = torch.zeros_like(fallen)
        self._gap_failed = torch.zeros_like(fallen)
        if self.cfg.terrain_all:
            local_x = self.robot.data.root_pos_w[:, 0] - self.scene.env_origins[:, 0]
            cv = self.course_variant
            mode = self.skill_mode
            # Progressive traversal gates: half the traversal population only has to clear the
            # two-level stairs first; the other groups extend through one ramp, both ramps, then
            # the complete route.  This supplies success signal before full-course mastery.
            self._course_done = (((mode == 4) & (local_x > 2.35)) |
                                 ((mode == 5) & (local_x > 3.65)) |
                                 ((mode == 6) & (local_x > 5.75)) |
                                 ((mode == 7) & (local_x > 6.15)) |
                                 ((cv == 1) & (local_x > float(
                                     FIELD_INFO.get('gap_success', 1.20)))) |
                                 ((cv == 2) & (local_x > float(
                                     FIELD_INFO.get('launch_success', 1.82)))))
            gap_trigger = FIELD_INFO.get('gap_trigger', (0.55, 0.92))
            gap_floor = self.spawn_z + float(FIELD_INFO.get('gap_spawn', (0, 0, 0.18))[2]) - 0.08
            self._gap_failed = ((cv == 1) & (local_x > gap_trigger[0]) &
                                (local_x < gap_trigger[1]) & (self._h < gap_floor))
            fallen = fallen | self._gap_failed
        self._fallen = fallen
        timed_out = ((self.episode_length_buf >= self.max_episode_length - 1) |
                     self._course_done)
        if self.cfg.eval_only:
            terminal = fallen | timed_out
            lane_masks = (
                (cv == 1), (cv == 2), (mode == 4), (mode == 5),
                (mode == 6), (mode == 7), (mode >= 4),
            ) if self.cfg.terrain_all else tuple(
                torch.zeros_like(terminal) for _ in range(7))
            for lane_index, lane_mask in enumerate(lane_masks):
                self.eval_success_counts[lane_index] += torch.count_nonzero(
                    self._course_done & lane_mask)
                self.eval_episode_counts[lane_index] += torch.count_nonzero(terminal & lane_mask)
        return fallen, timed_out

    def _write_neutral(self, env_ids):
        n = len(env_ids)
        pos = self.scene.env_origins[env_ids].clone()
        pos[:, 2] = self.spawn_z
        q = torch.zeros(n, 4, device=self.device)
        # Runtime state writers consume the native Warp/PhysX quaternion layout: xyzw.
        q[:, 3] = 1.0
        vel = torch.zeros(n, 6, device=self.device)
        z = torch.zeros(n, len(self.motor_ids), device=self.device)
        self._write_state(pos, q, vel, z, env_ids)

    def _write_state(self, pos, quat, vel, joint_state, env_ids):
        self.robot.write_root_link_pose_to_sim_index(
            root_pose=torch.cat([pos, quat], dim=-1), env_ids=env_ids)
        self.robot.write_root_com_velocity_to_sim_index(root_velocity=vel, env_ids=env_ids)
        self.robot.write_joint_state_to_sim_index(
            position=joint_state, velocity=joint_state, joint_ids=self.motor_ids, env_ids=env_ids)

    def _terrain_spawn_offsets(self, env_ids):
        offsets = torch.zeros(len(env_ids), 3, device=self.device)
        if not self.cfg.terrain_all:
            return offsets
        cv = self.course_variant[env_ids]
        points = {
            0: FIELD_INFO.get('stair_spawn', (-0.25, 0.0, 0.0)),
            1: (FIELD_INFO.get('gap_curriculum_spawn', (0.18, 2.45, 0.18))
                if (self.cfg.jump_curriculum and not self.cfg.eval_only) else
                FIELD_INFO.get('gap_spawn', (-0.72, 2.45, 0.18))),
            2: FIELD_INFO.get('launch_spawn', (-0.25, -2.45, 0.0)),
            3: FIELD_INFO.get('ramp_max_spawn', (2.6, 0.0, 0.20)),
            4: FIELD_INFO.get('ramp_med_spawn', (4.0, 0.0, 0.20)),
            5: FIELD_INFO.get('gap_spawn', (-0.72, 2.45, 0.18)),
        }
        for variant, point in points.items():
            mask = cv == variant
            if torch.any(mask):
                offsets[mask] = torch.tensor(point, device=self.device, dtype=offsets.dtype)
        return offsets

    def _reset_idx(self, env_ids):
        if not hasattr(self, 'command'):
            self._init_buffers()
        n = len(env_ids)
        if n == 0:
            return
        episode_log = {}
        for key, value in self._episode_sums.items():
            episode_log['Episode_Reward/' + key] = value[env_ids].mean() / self.max_episode_length_s
            value[env_ids] = 0.0
        episode_log['Episode_Termination/fallen'] = torch.count_nonzero(
            self.reset_terminated[env_ids]).item()
        episode_log['Episode_Termination/time_out'] = torch.count_nonzero(
            self.reset_time_outs[env_ids]).item()
        super()._reset_idx(env_ids)
        pos = self.scene.env_origins[env_ids].clone()
        terrain_offset = self._terrain_spawn_offsets(env_ids)
        pos += terrain_offset
        pos[:, 2] += self.spawn_z + torch.rand(n, device=self.device) * 0.004 + 0.002
        ang = (torch.rand(n, 3, device=self.device) - 0.5) * 0.036
        q = torch.zeros(n, 4, device=self.device)
        c = torch.cos(ang * 0.5); s = torch.sin(ang * 0.5)
        # Euler XYZ -> quaternion in the state writer's xyzw layout.
        q[:, 0] = s[:, 0] * c[:, 1] * c[:, 2] - c[:, 0] * s[:, 1] * s[:, 2]
        q[:, 1] = c[:, 0] * s[:, 1] * c[:, 2] + s[:, 0] * c[:, 1] * s[:, 2]
        q[:, 2] = c[:, 0] * c[:, 1] * s[:, 2] - s[:, 0] * s[:, 1] * c[:, 2]
        q[:, 3] = c[:, 0] * c[:, 1] * c[:, 2] + s[:, 0] * s[:, 1] * s[:, 2]
        vel = torch.zeros(n, 6, device=self.device)
        # the delivered neutral pose IS q=0 for every joint, so reset the six real joints to zero
        # (the two extra entries in the imported USD are the root/closure joints, not DOFs)
        z = torch.zeros(len(env_ids), len(self.motor_ids), device=self.device)
        self._write_state(pos, q, vel, z, env_ids)
        self._sample_commands(env_ids)
        self.jump_flag[env_ids] = 0.0
        self.prev_jump_flag[env_ids] = False
        self.jump_takeoff_z[env_ids] = pos[:, 2]
        self.jump_phase[env_ids] = 0
        self.jump_phase_time[env_ids] = 0.0
        self.jump_ref_vz[env_ids] = 0.0
        self.jump_cooldown[env_ids] = 0.0
        self.jump_airborne_seen[env_ids] = False
        self.jump_assist_selected[env_ids] = False
        self.jump_assisted_episode[env_ids] = False
        self.jump_assist_event[env_ids] = 0.0
        self.jump_clock[env_ids] = torch.randint(0, 800, (n,), device=self.device)
        self.prev_action[env_ids] = 0.0
        self.torques[env_ids] = 0.0
        self.extras.setdefault('log', {}).update(episode_log)


def write_ckpt_md(log_dir, agent, extra=None):
    md = []
    md.append('# Checkpoint 记录 - rm2025 无云台轮腿底盘 / Isaac Lab (PhysX)')
    md.append('')
    md.append('| 项 | 值 |')
    md.append('|---|---|')
    md.append('| 模型源 MJCF | `incoming/rm2025_fixed/scene_training.xml`（交付包 rm2025_fixed，闭链、**无云台**） |')
    md.append('| Isaac 用资产 | `incoming/rm2025_fixed/isaac/robot_serial/robot_serial.usda`（PhysX 串联等效，见下） |')
    md.append('| 部署资格 | **不可直接部署**：此策略动作是 `[hip, knee]` 串联教师坐标；真机必须使用闭链任务 `RMVehicle-CC-Field-v0` 的 `[thigh, crank]` 主动输出轴策略 |')
    md.append('| 为什么不是闭链 USD | 交付包自带的 `isaac/smoke_test.py` 在本机跑通后**未通过它自己的验收**：`left_proximal_closure separated by 0.283094 m`（32 次位置迭代 + TGS 仍不闭合）⇒ PhysX 承载不了这 6 条闭环 |')
    md.append('| 关节/动作 | 6 路力矩：left_hip, left_knee, left_wheel_spin, right_hip, right_knee, right_wheel_spin；限幅 ±40/±40/±6 N·m，腿部带 DM8009 转矩-转速包络 |')
    md.append('| 观测 | 39 维（与交付包 `robomaster_env.py` 同布局：线速度3+角速度3+重力投影3+sin/cos(髋,膝)8+6轮速+2膝角+2膝速+2(膝-髋)+1高度+1速度指令+2轮触地+6上一动作） |')
    md.append('| 奖励 | 1.5*速度跟踪 + 1.5* upright + 高度保持 - 0.03*动作² - 0.02*动作变化² - 0.0005*机械功率，×0.01 s |')
    md.append('| 终止 | base z < 0.22 m 或 倾角 up < 0.5（=约 60°）或非有限值；截断 20 s |')
    md.append('| 物理 | dt=0.0005 s，decimation=20 ⇒ 控制 100 Hz；轮半径 %.4f m，root-link 由轮心实测偏移自动贴地 |' % WHEEL_RADIUS)
    md.append('| 训练器 | rsl_rl PPO，actor/critic MLP 512-256-128 elu，init_noise_std=1.0，obs_normalization=True，lr=%.0e，num_steps_per_env=24，save_interval=%d |' % (MyArgs.lr, MyArgs.save_interval))
    md.append('| 日志/权重目录 | `%s` |' % log_dir)
    md.append('| 权重文件 | `model_<iter>.pt`（每 %d 次迭代及正常结束各保存一次；Ctrl+C 时保存 `model_interrupt_<iter>.pt`） |' % MyArgs.save_interval)
    md.append('')
    md.append('## 续训 / 加载检查点')
    md.append('')
    md.append('```')
    md.append(':: 从最新检查点继续（同模型）')
    md.append('.venv-isaaclab\\Scripts\\python.exe incoming\\rm2025_fixed\\isaac\\train_isaac.py --viz kit ^')
    md.append('    --resume %s\\model_*.pt' % log_dir)
    md.append('```')
    md.append('')
    md.append('## 下一步：加云台（用户要求：从检查点加载后加云台继续训）')
    md.append('')
    md.append('1. 交付包明确写着 **云台/弹仓载荷未建模**（HANDOFF 第 8 条），所以当前策略的 6 个动作里不含云台轴。')
    md.append('2. 加云台的做法（保持检查点可用）：')
    md.append('   - 在 MJCF 里给 chassis 加 `yaw_link/pitch_link`（+弹仓），用 `kinematics.py` 保持闭链中立；')
    md.append('   - 重新 `make_serial.py` + `convert_robot.py` 生成带云台的 USD；')
    md.append('   - 新 env 的 **观测前 39 维保持不变**，云台角/角速度追加在后面；**动作前 6 维保持不变**，云台两个轴追加在后面；')
    md.append('   - 用 `--resume` 加载本 md 记录的 `model_*.pt`：rsl_rl 的 `load(path, strict=False)` 允许新增输出列，')
    md.append('     旧权重原样复用，新增动作列的均值初始化设 0（策略一开始不动云台），再微调；')
    md.append('   - 若 strict 加载失败，脚本会退化为"只加载 actor/critic 已有列 + 归一化统计"，同样能热启动。')
    md.append('')
    if extra:
        md.append(extra)
    txt = chr(10).join(md) + chr(10)
    here = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(here, 'CKPT_isaac_no_gimbal.md')
    # never clobber the hand-maintained record; keep the per-run copy next to the checkpoints
    io.open(os.path.join(log_dir, 'CKPT.md'), 'w', encoding='utf-8', newline=chr(10)).write(txt)
    if not os.path.exists(path):
        io.open(path, 'w', encoding='utf-8', newline=chr(10)).write(txt)
    return path


def warm_start_compatible(module, source_state):
    """Load exact tensors and overlapping slices when observations/actions were appended."""
    target_state = module.state_dict()
    exact = partial = 0
    for key, target in target_state.items():
        source = source_state.get(key)
        if source is None or not isinstance(source, torch.Tensor) or source.ndim != target.ndim:
            continue
        source = source.to(device=target.device, dtype=target.dtype)
        if source.shape == target.shape:
            target_state[key] = source
            exact += 1
            continue
        if source.ndim == 0:
            continue
        merged = target.clone()
        overlap = tuple(slice(0, min(a, b)) for a, b in zip(target.shape, source.shape))
        merged[overlap] = source[overlap]
        target_state[key] = merged
        partial += 1
    module.load_state_dict(target_state, strict=True)
    return exact, partial


def run_deterministic_evaluation(wrapped, env, runner):
    """Measure the mean policy without exploration or curriculum assistance."""
    if not MyArgs.resume:
        raise ValueError('--eval-only requires --resume model_*.pt')
    policy = runner.get_inference_policy(device=Args.device)
    obs = wrapped.get_observations()
    env.eval_success_counts.zero_()
    env.eval_episode_counts.zero_()
    sums = {key: 0.0 for key in (
        'reward', 'level_5deg', 'upright', 'moving_vx', 'moving_vx_error',
        'turn_yaw_error', 'gyro_yaw_error', 'gyro_yaw_error_25deg',
        'gyro_yaw_error_12deg', 'gyro_yaw_error_gap_platform',
        'traverse_vx', 'traverse_vx_error', 'gap_progress', 'launch_progress',
        'jump_airborne', 'action_rms')}
    fall_events = episode_events = assist_events = 0
    steps = max(1, int(MyArgs.eval_steps))
    with torch.inference_mode():
        for _ in range(steps):
            actions = policy(obs)
            obs, rewards, dones, extras = wrapped.step(actions)
            gravity_xy2 = env.robot.data.projected_gravity_b[:, :2].pow(2).sum(-1)
            sums['reward'] += float(rewards.mean().item())
            sums['level_5deg'] += float(
                (gravity_xy2 < math.sin(math.radians(5.0)) ** 2).float().mean().item())
            sums['upright'] += float((-env.robot.data.projected_gravity_b[:, 2] > 0.86)
                                      .float().mean().item())
            moving = env.command.abs() > 0.10
            if torch.any(moving):
                sums['moving_vx'] += float(env._vx[moving].mean().item())
                sums['moving_vx_error'] += float(
                    (env._vx[moving] - env.command[moving]).abs().mean().item())
            gyro = env.skill_mode < 2
            if torch.any(gyro):
                sums['gyro_yaw_error'] += float(
                    (env.robot.data.root_ang_vel_b[gyro, 2] - env.yaw_command[gyro])
                    .abs().mean().item())
            for key, variant in (
                    ('gyro_yaw_error_25deg', 3),
                    ('gyro_yaw_error_12deg', 4),
                    ('gyro_yaw_error_gap_platform', 5)):
                surface = gyro & (env.course_variant == variant)
                if torch.any(surface):
                    sums[key] += float(
                        (env.robot.data.root_ang_vel_b[surface, 2] - env.yaw_command[surface])
                        .abs().mean().item())
            turning = env.skill_mode == 2
            if torch.any(turning):
                sums['turn_yaw_error'] += float(
                    (env.robot.data.root_ang_vel_b[turning, 2] - env.yaw_command[turning])
                    .abs().mean().item())
            traverse = env.skill_mode >= 4
            if torch.any(traverse):
                sums['traverse_vx'] += float(env._vx[traverse].mean().item())
                sums['traverse_vx_error'] += float(
                    (env._vx[traverse] - env.command[traverse]).abs().mean().item())
            local_x = env.robot.data.root_pos_w[:, 0] - env.scene.env_origins[:, 0]
            gap = env.course_variant == 1
            launch = env.course_variant == 2
            if torch.any(gap):
                sums['gap_progress'] += float(local_x[gap].mean().item())
            if torch.any(launch):
                sums['launch_progress'] += float(local_x[launch].mean().item())
            jump = env.skill_mode == 3
            if torch.any(jump):
                sums['jump_airborne'] += float(
                    (env._contacts[jump].mean(dim=1) < 0.5).float().mean().item())
            sums['action_rms'] += float(torch.sqrt(actions.clamp(-1.0, 1.0).pow(2).mean()).item())
            time_outs = extras.get('time_outs', torch.zeros_like(dones, dtype=torch.bool))
            done_b = dones.bool()
            fall_events += int(torch.count_nonzero(done_b & ~time_outs.bool()).item())
            episode_events += int(torch.count_nonzero(done_b).item())
            assist_events += int(torch.count_nonzero(env.jump_assist_event).item())

    success = env.eval_success_counts.detach().cpu().tolist()
    episodes = env.eval_episode_counts.detach().cpu().tolist()
    lane_names = (
        'gap', 'launch', 'two_level_stairs', 'max_slope',
        'both_slopes', 'full_course', 'traverse_any')
    report = {
        'checkpoint': os.path.abspath(MyArgs.resume),
        'steps': steps,
        'num_envs': env.num_envs,
        'deterministic': True,
        'assist_probability': env._jump_assist_probability(),
        'assist_events': assist_events,
        'means': {key: value / steps for key, value in sums.items()},
        'fall_fraction_of_completed_episodes': fall_events / max(1, episode_events),
        'completed_episodes': episode_events,
        'lanes': {
            name: {
                'successes': int(success[index]),
                'episodes': int(episodes[index]),
                'success_rate': float(success[index]) / max(1, int(episodes[index])),
            }
            for index, name in enumerate(lane_names)
        },
    }
    report_path = MyArgs.eval_report or os.path.join(
        os.path.dirname(os.path.abspath(MyArgs.resume)),
        'eval_' + os.path.splitext(os.path.basename(MyArgs.resume))[0] + '.json')
    os.makedirs(os.path.dirname(os.path.abspath(report_path)), exist_ok=True)
    io.open(report_path, 'w', encoding='utf-8', newline=chr(10)).write(
        json.dumps(report, ensure_ascii=False, indent=2) + chr(10))
    print('[eval] report ->', report_path, flush=True)
    print('[eval] ' + json.dumps(report, ensure_ascii=False, sort_keys=True), flush=True)

    if MyArgs.eval_hold:
        print('[eval] visible deterministic play is active; close the window to stop', flush=True)
        try:
            while app.is_running():
                start = time.time()
                with torch.inference_mode():
                    actions = policy(obs)
                    obs, _, _, _ = wrapped.step(actions)
                delay = env.step_dt - (time.time() - start)
                if delay > 0.0:
                    time.sleep(delay)
        except KeyboardInterrupt:
            pass
    return report


def main():
    cfg = RmCfg()
    if cfg.field:
        # Resolve the shared field module from the repository root on both Windows and Linux.
        sys.path.insert(0, os.path.join(WORKSPACE_ROOT, 'isaac'))
        from rmuc2026_field import rmuc2026_field_per_env
        feats, info = rmuc2026_field_per_env()
        FIELD_INFO.clear()
        FIELD_INFO.update(info)
        # the big flat slab stays as the arena floor; each env gets its OWN slice of the measured
        # map in front of it, which is the only way a map can enter 1024-way parallel RL
        for nm, acfg in feats.values():
            setattr(cfg.scene, 'field_' + nm, acfg)
        print('[env] RMUC2026 measured map, per env:', info, flush=True)
    env = RmSerialEnv(cfg=cfg)
    from isaaclab_rl.rsl_rl import (RslRlMLPModelCfg, RslRlOnPolicyRunnerCfg, RslRlPpoAlgorithmCfg,
                                    RslRlVecEnvWrapper)
    from rsl_rl.runners import OnPolicyRunner
    run_name = MyArgs.run or time.strftime('%Y-%m-%d_%H-%M-%S')
    agent = RslRlOnPolicyRunnerCfg(
        seed=42, device=Args.device, num_steps_per_env=MyArgs.steps_per_env,
        max_iterations=MyArgs.iters,
        save_interval=MyArgs.save_interval, experiment_name=MyArgs.exp, run_name=run_name,
        obs_groups={'actor': ['policy'], 'critic': ['critic']}, clip_actions=None,
        empirical_normalization=False,
        actor=RslRlMLPModelCfg(
            hidden_dims=[512, 256, 128], activation='elu', obs_normalization=True,
            distribution_cfg=RslRlMLPModelCfg.GaussianDistributionCfg(
                init_std=MyArgs.init_std if MyArgs.skills else 1.0, std_type='scalar')),
        critic=RslRlMLPModelCfg(hidden_dims=[512, 256, 128], activation='elu', obs_normalization=False),
        algorithm=RslRlPpoAlgorithmCfg(num_learning_epochs=5, num_mini_batches=4,
                                       learning_rate=MyArgs.lr, schedule='adaptive', gamma=0.99,
                                       lam=0.95, entropy_coef=0.001 if MyArgs.skills else 0.005,
                                       max_grad_norm=1.0,
                                       desired_kl=0.01, value_loss_coef=1.0,
                                       use_clipped_value_loss=True, clip_param=0.2))
    log_root = os.path.abspath(MyArgs.logdir)
    log_dir = os.path.join(log_root, MyArgs.exp, run_name)
    os.makedirs(log_dir, exist_ok=True)
    wrapped = RslRlVecEnvWrapper(env, clip_actions=agent.clip_actions)
    train_cfg = agent.to_dict()
    # Isaac Lab's configclass always emits the deprecated policy fields; rsl_rl 5 MLPModel only
    # accepts hidden_dims/activation/obs_normalization/distribution_cfg, so drop the extras.
    ALLOWED = ('class_name', 'hidden_dims', 'activation', 'obs_normalization', 'distribution_cfg',
               'last_activation')
    for role in ('actor', 'critic'):
        blk = train_cfg.get(role, {})
        for k in [k for k in blk if k not in ALLOWED]:
            blk.pop(k)
        dist = blk.get('distribution_cfg')
        if isinstance(dist, dict):
            for k in [k for k in dist if k not in ('class_name', 'init_std', 'std_type')]:
                dist.pop(k)
    print('[train] actor cfg:', train_cfg['actor'], flush=True)
    runner = OnPolicyRunner(wrapped, train_cfg, log_dir=log_dir, device=Args.device)
    if MyArgs.resume:
        print('[train] resume from', MyArgs.resume, flush=True)
        try:
            runner.load(MyArgs.resume)
        except Exception as ex:
            print('[train] strict load failed (%s); falling back to partial load' % ex, flush=True)
            ck = torch.load(MyArgs.resume, map_location=Args.device, weights_only=False)
            ae, ap = warm_start_compatible(runner.alg.actor, ck.get('actor_state_dict', {}))
            ce, cp = warm_start_compatible(runner.alg.critic, ck.get('critic_state_dict', {}))
            runner.current_learning_iteration = int(ck.get('iter', 0))
            print('[train] warm-started actor %d exact + %d partial; critic %d exact + %d partial'
                  % (ae, ap, ce, cp), flush=True)
        if MyArgs.skills:
            # Stage 1's entropy coefficient let several actuator standard deviations grow above
            # 4.0, which makes the visible robot look erratic despite a good deterministic mean.
            # Keep the learned mean network, but restart exploration at a controlled level.
            with torch.no_grad():
                runner.alg.actor.distribution.std_param.fill_(MyArgs.init_std)
            print('[train] stage-2 exploration std reset to %.3f' % MyArgs.init_std, flush=True)
    print('[train] ckpt md ->', write_ckpt_md(log_dir, agent), flush=True)
    print('[train] log dir ->', log_dir, flush=True)
    print('[train] envs %d  rollout %d  batch %d  obs %d  act %d  dt %.4f  GUI %s' % (
        env.num_envs, MyArgs.steps_per_env, env.num_envs * MyArgs.steps_per_env,
        env.observation_space.shape[-1], env.action_space.shape[-1], env.step_dt,
        bool(Args.visualizer)), flush=True)
    if MyArgs.eval_only:
        try:
            run_deterministic_evaluation(wrapped, env, runner)
        finally:
            env.close()
            app.close()
        return
    t0 = time.time()
    try:
        runner.learn(MyArgs.iters, init_at_random_ep_len=True)
        print('[train] finished %d iters in %.1f min' %
              (MyArgs.iters, (time.time() - t0) / 60.0), flush=True)
    except KeyboardInterrupt:
        emergency_path = os.path.join(log_dir, 'model_interrupt_%d.pt' % runner.current_learning_iteration)
        runner.save(emergency_path)
        print('[train] interrupted; checkpoint saved ->', emergency_path, flush=True)
    finally:
        env.close()
        app.close()


if __name__ == '__main__':
    main()
