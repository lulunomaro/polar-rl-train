"""Joint / body / geom / actuator name sets for the two vehicle models built from
整车总装.STEP, plus the deployment-contract ordering.

OPEN - the earlier 2-DOF serial-chain simplification (kept for regression).
CC   - the validated similar-linkage (kite four-bar) closed chain: both leg motors sit on
       the hip axis, exactly like the SJTU RM2025 serial leg and the SCUT wheelbipeV14_2
       reference.  rear1 = thigh drive, front1 = crank that drives the *passive* knee
       through the linkage (validated to 0.0000 mm loop closure and to 0.02 deg against
       the mujoco-warp GPU solver; see scripts/cc_gaps.py, scripts/cc_warp_test.py).

The 8-joint deployment order is fixed by wheelbipe_ros2_sim2sim PARAMETERS.md section 3:
    0 left_front1  1 left_rear1  2 right_front1  3 right_rear1
    4 left_wheel   5 right_wheel 6 left_spring2  7 right_spring2
so the 6-D policy action is [front1_L, rear1_L, front1_R, rear1_R, wheel_L, wheel_R].
Every tuple below is in that order, one pattern per entry, so the resolved order is
deterministic.
"""
import os
from pathlib import Path

# --- motor profile (mirrors scripts/build_cc.py's CC_MOTOR) -------------------
# See docs/MOTOR_PARAMS.md for the source of every number below.
MOTOR_PROFILE = os.environ.get("RM_MOTOR", "dm8009").lower()
_MOTORS = {
  # ``*_effort`` is the current-limited plateau. ``*_saturation`` is the
  # zero-speed intercept of the voltage-only torque-speed line.  mjlab's
  # DcMotorActuator takes the minimum of both, which gives the measured/derived
  # plateau followed by the voltage-limited falloff instead of an ideal motor.
  #
  # Production hardware (confirmed by the user on 2026-09-09):
  #   legs   DM-J8009-2EC 9:1, 24 V
  #   wheels DM3519 bare motor + 15.8:1 total wheel gearbox, 24 V
  #
  # 2026-09-10 (0910 delivery): the replacement 15.8:1 gearbox is modelled at 0.90
  # relative efficiency, so the wheel plateau is 5.7759 N*m (was 6.4188) and the
  # voltage-line intercept is 28.1853 N*m (was 31.3223).  The delivered
  # robot_hifi.xml ctrlrange agrees.  Source of truth:
  # incoming/rm2025_fixed_rl_20260910/rm2025_fixed/{wheel_drive_spec.py,
  # model_parameters.json}.
  "dm8009":   dict(
      leg_model="DM-J8009-2EC", leg_effort=40.0,
      leg_saturation=53.333333333333336, leg_velocity=16.755160819145562,
      leg_internal_ratio=9.0, leg_external_ratio=1.0,
      wheel_model="DM3519+15.8", wheel_effort=5.775909774436091,
      wheel_saturation=28.18532894736838, wheel_velocity=55.3557,
      wheel_knee_velocity=44.0118, wheel_total_ratio=15.8),
  "legacy54": dict(leg_effort=50.9, leg_velocity=100.0,
                   leg_saturation=50.9, leg_internal_ratio=1.0,
                   leg_external_ratio=1.0, leg_model="legacy-reference",
                   wheel_effort=10.0, wheel_saturation=10.0,
                   wheel_velocity=25.0, wheel_knee_velocity=0.0,
                   wheel_total_ratio=1.0, wheel_model="legacy-reference"),
}
if MOTOR_PROFILE not in _MOTORS:
  raise SystemExit("unknown RM_MOTOR profile: " + MOTOR_PROFILE)
MOTORS = _MOTORS[MOTOR_PROFILE]
LEG_EFFORT = MOTORS["leg_effort"]
LEG_SATURATION = MOTORS["leg_saturation"]
LEG_VELOCITY = MOTORS["leg_velocity"]
WHEEL_EFFORT_P = MOTORS["wheel_effort"]
WHEEL_SATURATION = MOTORS["wheel_saturation"]
WHEEL_VELOCITY = MOTORS["wheel_velocity"]
WHEEL_KNEE_VELOCITY = MOTORS["wheel_knee_velocity"]

from dataclasses import dataclass


@dataclass(frozen=True)
class ModelNames:
  key: str
  xml_name: str
  leg_joints: tuple        # joint-name patterns, contract order
  leg_actuators: tuple     # actuator-name patterns, same order
  leg_effort: tuple        # N*m per leg actuator
  wheel_joints: tuple
  wheel_actuators: tuple
  wheel_geoms: tuple
  collide_geoms: tuple    # ONLY these geoms may touch the terrain
  wheel_bodies: tuple
  thigh_bodies: tuple
  base_bodies: tuple
  root_height: float = 0.075
  wheel_radius: float = 0.073
  half_track: float = 0.270
  physics_dt: float = 0.002
  decimation: int = 10
  wheel_friction: tuple = (1.2, 0.02, 0.002)
  gas_spring_joints: tuple = ()
  limb_bodies: tuple = ()
  # The delivered later MJCF hard-caps the wheel motors at its own ctrlrange (0910:
  # +-5.77590977444 N*m).  Training must use the SAME cap the deployment plant enforces,
  # so this overrides the motor profile for that model only.  0 means "use the profile
  # value".  Since 2026-09-10 the override and the delivery agree, and
  # scripts/check_model_identity.py asserts that equality, so drift here is a hard failure.
  wheel_effort_override: float = 0.0
  # Reflected rotor inertia at the wheel output shaft.  0 means "keep whatever the source
  # MJCF declares".  The 0908 delivery carried 0 (which made the wheel-armature DR a
  # no-op); the 0910 delivery carries 4e-6 * 15.8^2 = 9.9856e-4 kg*m^2 itself, so the old
  # 0.001 placeholder is gone and the number now has a delivered provenance.
  wheel_armature_override: float = 0.0
  # Wheel action unit in rad/s per policy unit for THIS model.  0 means "use the module
  # default / RM_WHEEL_SCALE".  The later plant trains at 10 rad/s per unit (its warm-start
  # seed carries a x5.5 output-row compensation so the CC policy keeps commanding the same
  # physical wheel speed), while the earlier CC plant trained at 55.  Anything that builds
  # the later env WITHOUT the launcher's RM_WHEEL_SCALE=10 -- the acceptance harness, the
  # ONNX exporter, a fresh python session -- silently used 55 and made every wheel command
  # 5.5x too large: the 2026-09-10 acceptance run reported 0.8% flat survival for a policy
  # whose training log said 19.5 s episodes.  Keep the trained value here so it cannot drift.
  wheel_action_scale_override: float = 0.0


OPEN = ModelNames(
  key="open", xml_name="rm_vehicle.xml",
  leg_joints=(r"^hip_L_joint$", r"^knee_L_joint$", r"^hip_R_joint$", r"^knee_R_joint$"),
  leg_actuators=(r"^hip_L_joint$", r"^knee_L_joint$", r"^hip_R_joint$", r"^knee_R_joint$"),
  leg_effort=(24.0, 30.0, 24.0, 30.0),
  wheel_joints=(r"^wheel_L_joint$", r"^wheel_R_joint$"),
  wheel_actuators=(r"^wheel_L_joint$", r"^wheel_R_joint$"),
  wheel_geoms=(r"^wheel_[LR]_col0$",),
  collide_geoms=(r"^(thigh|shank|wheel)_[LR]_col\d+$",),
  wheel_bodies=("wheel_L", "wheel_R"),
  thigh_bodies=("thigh_L", "thigh_R"),
  base_bodies=("base",),
)

# Both leg drives are hip-axis motors of the same class; the similar linkage splits the
# support-force and torsion load equally between them (SJTU note, section 1.2.1:
# "支持力和扭转力都平均分配到了两关节电机上"), so they get the same effort limit.
CC = ModelNames(
  key="cc", xml_name="rm_vehicle_cc.xml",
  leg_joints=(r"^left_front1_joint$", r"^left_rear1_joint$",
              r"^right_front1_joint$", r"^right_rear1_joint$"),
  # mjlab matches actuator configs by JOINT name, so these are joint patterns too.
  leg_actuators=(r"^left_front1_joint$", r"^left_rear1_joint$",
                 r"^right_front1_joint$", r"^right_rear1_joint$"),
  # 50.9 N*m = the deployment contract's joint_output_max (PARAMETERS.md sec.3), and the
  # reference MJCF uses +-54.  Jump feasibility was measured on the validated model
  # (scripts/jump_gains.py): peak vz 0.82 m/s at 30 N*m (=> 3.4 cm ballistic) versus
  # 1.10 m/s at 50.9 N*m (=> 6.2 cm), so 30 N*m physically cannot clear the 5-11 cm
  # jump target the task asks for.
  leg_effort=(LEG_EFFORT,) * 4,
  wheel_joints=(r"^left_wheel_joint$", r"^right_wheel_joint$"),
  wheel_actuators=(r"^left_wheel_joint$", r"^right_wheel_joint$"),
  wheel_geoms=(r"^(left|right)_wheel_col$",),
  collide_geoms=(r"^(left|right)_(rear1|rear2|front1|front2|front3|front4|spring1|spring2|wheel)_col$",),
  wheel_bodies=("left_wheel", "right_wheel"),
  thigh_bodies=("left_rear1", "right_rear1"),
  base_bodies=("base_link",),
  gas_spring_joints=(r"^left_spring2_joint$", r"^right_spring2_joint$"),
  limb_bodies=(
    r"^(left|right)_(rear1|rear2|front1|front2|front3|front4|spring1|spring2)$",
  ),
)


# The user's later model (2026-09-08 delivery), not the earlier Hero model above.
# Its second hip-axis motor drives ``crank`` through the external 1:1 chain and the knee is
# passive.  Keep this path explicit so selecting this task cannot silently fall back to
# train/rmvehicle/assets/rm_vehicle_cc.xml.
_WORKSPACE = Path(__file__).resolve().parents[4]
RM2025_LATER = ModelNames(
  key="rm2025_later_no_gimbal",
  # MOD4 chassis delivery (2026-09-10).  The previous 0910 file was retired: its two legs
  # were not congruent (up to 0.895 mm; 262.0 mm knee-to-wheel instead of 258 mm), the shin
  # and wheel masses were wrong, and its joint zero/limits differ from MOD4's re-zeroed
  # closed middle posture.  See incoming/rm2025_fixed/DO_NOT_USE.md; robot_cfg._resolve_path
  # raises if anything resolves back into that directory.
  xml_name=str(_WORKSPACE / "incoming" / "rm2025_mod4" / "robot_hifi.xml"),
  # Public observation/export contract stays [crank_L, thigh_L, crank_R, thigh_R].
  # The action manager resolves these patterns into model order [hip_L, crank_L,
  # hip_R, crank_R]; export applies [1,0,3,2,4,5], as for the SCUT-compatible plant.
  leg_joints=(r"^left_crank$", r"^left_hip$", r"^right_crank$", r"^right_hip$"),
  leg_actuators=(r"^left_crank$", r"^left_hip$", r"^right_crank$", r"^right_hip$"),
  leg_effort=(LEG_EFFORT,) * 4,
  wheel_joints=(r"^left_wheel_spin$", r"^right_wheel_spin$"),
  wheel_actuators=(r"^left_wheel_spin$", r"^right_wheel_spin$"),
  wheel_geoms=(r"^(left|right)_tire$",),
  collide_geoms=(
    r"^(left|right)_(thigh_collision|rocker_(lower|upper)_collision|distal_collision|"
    r"shin(_tip)?_collision|tire|input_collision|coupler_collision)$",
  ),
  wheel_bodies=("left_wheel", "right_wheel"),
  thigh_bodies=("left_thigh", "right_thigh"),
  base_bodies=("chassis",),
  root_height=0.298936789692,
  wheel_radius=0.0625,
  half_track=0.23585399708,
  physics_dt=0.0005,
  decimation=20,
  wheel_friction=(0.9, 0.003, 0.0001),
  gas_spring_joints=(r"^left_gas_slide$", r"^right_gas_slide$"),
  # 0910 delivery: ctrlrange +-5.77590977444 N*m, armature 9.9856e-4 (carried by the XML
  # itself), gas spring 3500 N/m, wheel body 0.20194 kg, shin 0.70108 kg.
  wheel_effort_override=5.775909774436091,
  wheel_armature_override=0.0,
  wheel_action_scale_override=10.0,
  limb_bodies=(
    r"^(left|right)_(thigh|rocker|distal|shin|gas_inner|gas_barrel|input|coupler|"
    r"drive_hip|drive_input)$",
  ),
)
