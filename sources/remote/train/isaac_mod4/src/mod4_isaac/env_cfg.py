"""Manager-based MOD4 task for Isaac Lab: flat ground, 35-D contract, full DR block."""
from __future__ import annotations

import isaaclab.envs.mdp as base_mdp
import isaaclab.sim as sim_utils
from isaaclab.assets import AssetBaseCfg
from isaaclab.envs import ManagerBasedRLEnvCfg
from isaaclab.envs.mdp import UniformVelocityCommandCfg
from isaaclab.managers import (
    CurriculumTermCfg,
    EventTermCfg,
    ObservationGroupCfg,
    ObservationTermCfg,
    RewardTermCfg,
    SceneEntityCfg,
    TerminationTermCfg,
)
from isaaclab.scene import InteractiveSceneCfg
from isaaclab.sensors import ContactSensorCfg
from isaaclab.utils.configclass import configclass
from isaaclab.utils.noise import UniformNoiseCfg as Unoise

from . import mdp
from .robot_cfg import (
    ACTUATED_JOINTS,
    DECIMATION,
    EPISODE_LENGTH_S,
    LEG_ACTION_SCALE,
    LEG_JOINTS,
    PHYSICS_DT,
    WHEEL_ACTION_SCALE,
    WHEEL_JOINTS,
    make_robot_cfg,
)

ROBOT = SceneEntityCfg("robot")
LEG_CFG = SceneEntityCfg("robot", joint_names=list(LEG_JOINTS), preserve_order=True)
WHEEL_CFG = SceneEntityCfg("robot", joint_names=list(WHEEL_JOINTS), preserve_order=True)


@configclass
class Mod4SceneCfg(InteractiveSceneCfg):
    """Flat plane, robot, wheel + chassis contact sensing, headlight."""

    # A local 200 m ground cuboid, not TerrainImporterCfg(terrain_type="plane"): that path
    # pulls Isaac's default_environment.usd from the Omniverse CDN and this box trains offline.
    ground = AssetBaseCfg(
        prim_path="/World/ground",
        spawn=sim_utils.CuboidCfg(
            size=(200.0, 200.0, 0.1),
            collision_props=sim_utils.CollisionPropertiesCfg(),
            physics_material=sim_utils.RigidBodyMaterialCfg(
                friction_combine_mode="multiply",
                restitution_combine_mode="multiply",
                static_friction=0.9,
                dynamic_friction=0.9,
                restitution=0.0,
            ),
            visual_material=sim_utils.PreviewSurfaceCfg(diffuse_color=(0.35, 0.35, 0.38)),
        ),
        init_state=AssetBaseCfg.InitialStateCfg(pos=(0.0, 0.0, -0.05)),
    )
    robot = make_robot_cfg()
    wheel_contact = ContactSensorCfg(
        prim_path="{ENV_REGEX_NS}/Robot/links/.*wheel",
        update_period=0.0,
        history_length=4,
        track_air_time=True,
        debug_vis=False,
        # Only wheel<->ground counts as contact.  Without the filter the sensor also reports
        # wheel<->leg self-collisions, which is not what the contact reward means.
        filter_prim_paths_expr=["/World/ground"],
    )
    chassis_contact = ContactSensorCfg(
        prim_path="{ENV_REGEX_NS}/Robot/links/chassis",
        update_period=0.0,
        history_length=1,
        debug_vis=False,
        # Chassis<->terrain only.  Measuring all chassis contacts made the legs brushing the
        # chassis (the delivered model is a folded closed chain) terminate 99% of episodes.
        filter_prim_paths_expr=["/World/ground"],
    )
    light = AssetBaseCfg(prim_path="/World/light", spawn=sim_utils.DomeLightCfg(intensity=2500.0))


@configclass
class ObservationsCfg:
    """35-D actor contract + privileged critic."""

    @configclass
    class PolicyCfg(ObservationGroupCfg):
        commands = ObservationTermCfg(func=mdp.twist_commands, params={"command_name": "twist"})
        height_command = ObservationTermCfg(func=mdp.height_command_obs, scale=5.0,
                                            params={"command_name": "height"})
        base_ang_vel = ObservationTermCfg(func=base_mdp.base_ang_vel, scale=0.5,
                                          noise=Unoise(n_min=-0.25, n_max=0.25))
        projected_gravity = ObservationTermCfg(func=base_mdp.projected_gravity,
                                               noise=Unoise(n_min=-0.05, n_max=0.05))
        leg_pos = ObservationTermCfg(func=mdp.leg_pos_biased, params={"asset_cfg": LEG_CFG},
                                     noise=Unoise(n_min=-0.01, n_max=0.01))
        wheel_pos_slots = ObservationTermCfg(func=mdp.wheel_pos_slots, params={"asset_cfg": WHEEL_CFG})
        leg_vel = ObservationTermCfg(func=mdp.leg_vel, scale=0.1, params={"asset_cfg": LEG_CFG},
                                     noise=Unoise(n_min=-0.5, n_max=0.5))
        wheel_vel = ObservationTermCfg(func=mdp.wheel_vel, scale=0.1, params={"asset_cfg": WHEEL_CFG},
                                       noise=Unoise(n_min=-1.0, n_max=1.0))
        last_action = ObservationTermCfg(func=base_mdp.last_action)
        mode_onehot = ObservationTermCfg(func=mdp.mode_onehot)

        def __post_init__(self):
            self.enable_corruption = True
            self.concatenate_terms = True

    @configclass
    class CriticCfg(PolicyCfg):
        base_lin_vel = ObservationTermCfg(func=base_mdp.base_lin_vel)
        base_height = ObservationTermCfg(func=mdp.base_height_obs)
        encoder_bias = ObservationTermCfg(func=mdp.leg_encoder_bias_obs, params={"asset_cfg": LEG_CFG})
        applied_torque = ObservationTermCfg(func=mdp.applied_torque_legs, params={"asset_cfg": LEG_CFG})

        def __post_init__(self):
            super().__post_init__()
            self.enable_corruption = False

    policy: PolicyCfg = PolicyCfg()
    critic: CriticCfg = CriticCfg()


@configclass
class ActionsCfg:
    """Six actions in contract slot order: hip/crank pairs then wheels."""

    leg_position = mdp.LegPositionActionCfg(
        asset_name="robot",
        joint_names=list(LEG_JOINTS),
        scale=LEG_ACTION_SCALE,
        use_default_offset=True,
        preserve_order=True,
        effort_noise_scale=0.03,
    )
    wheel_velocity = mdp.WheelVelocityActionCfg(
        asset_name="robot",
        joint_names=list(WHEEL_JOINTS),
        scale=WHEEL_ACTION_SCALE,
        use_default_offset=False,
        preserve_order=True,
        effort_noise_scale=0.02,
    )


@configclass
class CommandsCfg:
    twist = UniformVelocityCommandCfg(
        asset_name="robot",
        resampling_time_range=(6.0, 12.0),
        rel_standing_envs=0.15,
        rel_heading_envs=0.0,
        heading_command=False,
        debug_vis=False,
        ranges=UniformVelocityCommandCfg.Ranges(lin_vel_x=(-1.0, 1.8), lin_vel_y=(0.0, 0.0),
                                                ang_vel_z=(-1.0, 1.0)),
    )
    height = mdp.HeightCommandCfg(ranges=(0.18, 0.34))


@configclass
class RewardsCfg:
    track_lin_vel = RewardTermCfg(func=base_mdp.track_lin_vel_xy_exp, weight=2.0,
                                  params={"command_name": "twist", "std": 0.7071067811865476})
    track_ang_vel = RewardTermCfg(func=base_mdp.track_ang_vel_z_exp, weight=2.5,
                                  params={"command_name": "twist", "std": 1.4142135623730951})
    height_tracking = RewardTermCfg(func=mdp.height_tracking, weight=1.0,
                                    params={"std": 0.06, "command_name": "height"})
    wheel_contact = RewardTermCfg(func=mdp.wheel_contact_fraction, weight=0.8,
                                  params={"sensor_name": "wheel_contact"})
    alive = RewardTermCfg(func=base_mdp.is_alive, weight=1.0)
    flat_orientation = RewardTermCfg(func=base_mdp.flat_orientation_l2, weight=-1.0)
    lin_vel_z = RewardTermCfg(func=mdp.lin_vel_z_l2, weight=-0.6)
    ang_vel_xy = RewardTermCfg(func=mdp.ang_vel_xy_l2, weight=-0.05)
    leg_symmetry = RewardTermCfg(func=mdp.leg_symmetry, weight=-0.2)
    # -1e-8, not the mjlab default -2.5e-6: the MOD4 plant carries a stiff gas spring plus
    # ten loop constraints (peak constraint force ~1e4 N), so sum(qacc^2) is ~6e6 even in a
    # zero-control drop and the CC-tuned weight would eat the whole episode reward.
    joint_acc = RewardTermCfg(func=base_mdp.joint_acc_l2, weight=-1.0e-8)
    joint_torques = RewardTermCfg(func=base_mdp.joint_torques_l2, weight=-1.5e-5)
    joint_power = RewardTermCfg(func=mdp.joint_power, weight=-2.0e-4)
    action_rate = RewardTermCfg(func=base_mdp.action_rate_l2, weight=-0.05)
    action_acc = RewardTermCfg(func=mdp.action_acc_l2, weight=-0.02)
    action_l2_leg = RewardTermCfg(func=mdp.action_l2, weight=-0.1, params={"action_slice": (0, 4)})
    action_l2_wheel = RewardTermCfg(func=mdp.action_l2, weight=-0.02, params={"action_slice": (4, 6)})
    dof_pos_limits = RewardTermCfg(func=base_mdp.joint_pos_limits, weight=-5.0)
    termination = RewardTermCfg(func=base_mdp.is_terminated, weight=-20.0)


@configclass
class TerminationsCfg:
    time_out = TerminationTermCfg(func=base_mdp.time_out, time_out=True)
    bad_orientation = TerminationTermCfg(func=base_mdp.bad_orientation, params={"limit_angle": 0.75})
    base_contact = TerminationTermCfg(func=mdp.ground_contact,
                                      params={"sensor_name": "chassis_contact", "threshold": 1.0})
    # The delivered plant only counts if the six loop closures are still held, so a broken
    # chain ends the episode instead of quietly training a different robot (limit 2 mm in the
    # acceptance test; 5 mm here because a reset transient is not a modelling failure).
    closure_break = TerminationTermCfg(func=mdp.closure_break, params={"tolerance": 0.005})
    nan_detection = TerminationTermCfg(func=mdp.nan_detection)


@configclass
class EventCfg:
    """Resets and the domain randomisation that is meant to eat the real-robot spread."""

    reset_scene = EventTermCfg(func=base_mdp.reset_scene_to_default, mode="reset")
    reset_height = EventTermCfg(func=mdp.randomize_height_command, mode="reset",
                                params={"command_name": "height", "range": (0.18, 0.34)})
    reset_base = EventTermCfg(func=base_mdp.reset_root_state_uniform, mode="reset",
                              params={"pose_range": {"x": (-0.2, 0.2), "y": (-0.2, 0.2),
                                                     "z": (0.0, 0.02), "yaw": (-3.14, 3.14)},
                                      "velocity_range": {"x": (-0.2, 0.2), "y": (-0.2, 0.2),
                                                         "z": (0.0, 0.0)},
                                      "asset_cfg": ROBOT})
    encoder_bias = EventTermCfg(func=mdp.randomize_encoder_bias, mode="reset",
                                params={"offset": 0.01})
    effort_scale = EventTermCfg(func=mdp.randomize_effort_scale, mode="reset",
                                params={"scale_range": (0.75, 1.25)})
    gas_spring = EventTermCfg(func=mdp.randomize_gas_spring, mode="reset",
                              params={"stiffness_range": (0.85, 1.15), "damping_range": (0.7, 1.3)})
    gas_spring_friction = EventTermCfg(func=mdp.randomize_gas_spring_friction, mode="reset",
                                       params={"friction_range": (0.0, 0.6)})
    leg_wheel_friction = EventTermCfg(func=base_mdp.randomize_joint_parameters, mode="reset",
                                      params={"asset_cfg": SceneEntityCfg("robot", joint_names=list(ACTUATED_JOINTS)),
                                              "friction_distribution_params": (0.0, 0.10),
                                              "operation": "abs"})
    leg_wheel_armature = EventTermCfg(func=base_mdp.randomize_joint_parameters, mode="reset",
                                      params={"asset_cfg": SceneEntityCfg("robot", joint_names=list(ACTUATED_JOINTS)),
                                              "armature_distribution_params": (0.8, 1.2),
                                              "operation": "scale"})
    leg_damping = EventTermCfg(func=base_mdp.randomize_actuator_gains, mode="reset",
                               params={"asset_cfg": LEG_CFG,
                                       "damping_distribution_params": (0.85, 1.15),
                                       "operation": "scale"})
    wheel_damping = EventTermCfg(func=base_mdp.randomize_actuator_gains, mode="reset",
                                 params={"asset_cfg": WHEEL_CFG,
                                         "damping_distribution_params": (0.8, 1.2),
                                         "operation": "scale"})
    base_mass = EventTermCfg(func=base_mdp.randomize_rigid_body_mass, mode="reset",
                             params={"asset_cfg": SceneEntityCfg("robot", body_names="chassis"),
                                     "mass_distribution_params": (0.82, 1.30), "operation": "scale"})
    base_com = EventTermCfg(func=base_mdp.randomize_rigid_body_com, mode="reset",
                            params={"asset_cfg": SceneEntityCfg("robot", body_names="chassis"),
                                    "com_range": {"x": (-0.03, 0.03), "y": (-0.03, 0.03), "z": (-0.03, 0.03)}})
    # NOT PRESENT ON PURPOSE: per-environment tyre/ground friction.  Isaac Lab randomises
    # friction through the PhysX material pool, and at 4096 environments the robot alone
    # materialises more than the 64K PxMaterial objects PhysX allows, so the scene dies with
    # "PxPhysics::createMaterial: limit of 64K materials reached" (measured on the target with
    # both 16 and 4 buckets).  Tyre friction therefore stays at the authored 0.9/0.9; the rest
    # of the uncertainty budget is covered by mass, COM, drive gains, gas spring, joint friction
    # and the push/external-force terms.  See docs/MOD4_ISAAC_TRAINING.md for the options if a
    # per-env tyre model is wanted later (physics-material pool built before replication).
    push_robot = EventTermCfg(func=base_mdp.push_by_setting_velocity, mode="interval",
                              interval_range_s=(6.0, 12.0),
                              params={"velocity_range": {"x": (-0.4, 0.4), "y": (-0.3, 0.3), "z": (0.0, 0.0)},
                                      "asset_cfg": ROBOT})
    external_force = EventTermCfg(func=base_mdp.apply_external_force_torque, mode="reset",
                                  params={"force_range": (-10.0, 10.0), "torque_range": (-1.0, 1.0),
                                          "asset_cfg": SceneEntityCfg("robot", body_names="chassis")})


@configclass
class CurriculumCfg:
    """Command windows stay closed for the first commit; open them once tracking is real."""

    twist = CurriculumTermCfg(func=mdp.commands_vel_range_curriculum,
                              params={"command_name": "twist",
                                      "vx_range": (-1.5, 2.8), "wz_range": (-14.0, 14.0),
                                      "start_step": 4000})


@configclass
class Mod4FlatEnvCfg(ManagerBasedRLEnvCfg):
    scene: Mod4SceneCfg = Mod4SceneCfg(num_envs=4096, env_spacing=2.0, replicate_physics=True)
    observations: ObservationsCfg = ObservationsCfg()
    actions: ActionsCfg = ActionsCfg()
    commands: CommandsCfg = CommandsCfg()
    rewards: RewardsCfg = RewardsCfg()
    terminations: TerminationsCfg = TerminationsCfg()
    events: EventCfg = EventCfg()
    curriculum: CurriculumCfg = CurriculumCfg()

    def __post_init__(self):
        self.decimation = DECIMATION
        self.episode_length_s = EPISODE_LENGTH_S
        self.sim.dt = PHYSICS_DT
        self.sim.render_interval = self.decimation
        self.viewer.eye = (3.0, 3.0, 2.0)
        self.viewer.lookat = (0.0, 0.0, 0.30)
