"""MOD4 plant for Isaac Lab: the delivered USD, driven the way the firmware drives it.

The plant is imported from incoming/rm2025_mod4/isaac/robot.usd exactly as delivered (the
same file the acceptance smoke test loads).  Legs are position servos (kp 60 / kd 2), the
wheels are velocity servos (kd 0.6) -- the DM8009 / DM3519 drive modes the deployment
contract describes, so the policy sees the same action semantics on both sides.
"""
from __future__ import annotations

import json
from pathlib import Path

import isaaclab.sim as sim_utils
from isaaclab.actuators import ImplicitActuatorCfg
from isaaclab.assets import ArticulationCfg

WORKSPACE = Path(__file__).resolve().parents[4]
MOD4_DIR = WORKSPACE / "incoming" / "rm2025_mod4"
USD_PATH = MOD4_DIR / "isaac" / "robot.usd"
IMPORT_CONTRACT = json.loads((MOD4_DIR / "isaac" / "import_contract.json").read_text(encoding="utf8"))
DEPLOY_CONTRACT = json.loads((WORKSPACE / "train" / "deploy" / "contract_rm2025_later.json").read_text(encoding="utf8"))

LEG_JOINTS = ("left_hip", "left_crank", "right_hip", "right_crank")
WHEEL_JOINTS = ("left_wheel_spin", "right_wheel_spin")
GAS_JOINTS = tuple(IMPORT_CONTRACT["gas_springs"])
ALL_JOINTS = tuple(IMPORT_CONTRACT["joints"])
ACTUATED_JOINTS = LEG_JOINTS + WHEEL_JOINTS
PASSIVE_JOINTS = tuple(n for n in ALL_JOINTS if n not in ACTUATED_JOINTS and n not in GAS_JOINTS)

LEG_KP = float(DEPLOY_CONTRACT["leg_kp"])
LEG_KD = float(DEPLOY_CONTRACT["leg_kd"])
WHEEL_KD = float(DEPLOY_CONTRACT["wheel_kd"])
LEG_ACTION_SCALE = float(DEPLOY_CONTRACT["leg_action_scale"])
WHEEL_ACTION_SCALE = float(DEPLOY_CONTRACT["wheel_action_scale"])
LEG_EFFORT = float(DEPLOY_CONTRACT["leg_effort"])
WHEEL_EFFORT = float(DEPLOY_CONTRACT["wheel_effort"])
# The spawn height comes from the DELIVERED MOD4 import contract (0.337742 m), not from the
# deployment contract: contract_rm2025_later.json still points at incoming/rm2025_fixed and
# its root_height 0.2989 m is the retired model.  Spawning 39 mm low pre-loads the legs and
# buries the wheels, which showed up as a 43% base_contact termination rate.
ROOT_HEIGHT = float(IMPORT_CONTRACT["spawn_height_m"])
PHYSICS_DT = float(DEPLOY_CONTRACT["physics_dt"])
DECIMATION = int(DEPLOY_CONTRACT["decimation"])
EPISODE_LENGTH_S = 20.0


def armature(name: str) -> float:
    return float(IMPORT_CONTRACT["joints"][name]["armature"])


def damping(name: str) -> float:
    return float(IMPORT_CONTRACT["joints"][name]["damping_si"])


def make_robot_cfg(prim_path: str = "/World/envs/env_.*/Robot") -> ArticulationCfg:
    return ArticulationCfg(
        prim_path=prim_path,
        spawn=sim_utils.UsdFileCfg(
            usd_path=str(USD_PATH),
            activate_contact_sensors=True,
            rigid_props=sim_utils.RigidBodyPropertiesCfg(
                disable_gravity=False,
                max_depenetration_velocity=1.0,
                linear_damping=0.0,
                angular_damping=0.0,
                enable_gyroscopic_forces=True,
                retain_accelerations=True,
            ),
            articulation_props=sim_utils.ArticulationRootPropertiesCfg(
                enabled_self_collisions=True,
                # The delivered smoke test accepts the plant at 32/8 and the loops plus the
                # four sprocket couplings live or die with these counts.
                solver_position_iteration_count=32,
                solver_velocity_iteration_count=8,
            ),
        ),
        init_state=ArticulationCfg.InitialStateCfg(
            pos=(0.0, 0.0, ROOT_HEIGHT),
            joint_pos={".*": 0.0},
            joint_vel={".*": 0.0},
        ),
        soft_joint_pos_limit_factor=1.0,
        actuators={
            "legs": ImplicitActuatorCfg(
                joint_names_expr=list(LEG_JOINTS),
                stiffness=LEG_KP,
                damping=LEG_KD,
                effort_limit_sim=LEG_EFFORT,
                velocity_limit_sim=1000.0,
                armature={n: armature(n) for n in LEG_JOINTS},
                friction=0.0,
            ),
            "wheels": ImplicitActuatorCfg(
                joint_names_expr=list(WHEEL_JOINTS),
                stiffness=0.0,
                damping=WHEEL_KD,
                effort_limit_sim=WHEEL_EFFORT,
                velocity_limit_sim=1000.0,
                armature={n: armature(n) for n in WHEEL_JOINTS},
                friction=0.0,
            ),
            "gas_springs": ImplicitActuatorCfg(
                joint_names_expr=list(GAS_JOINTS),
                stiffness={n: float(IMPORT_CONTRACT["gas_springs"][n]["stiffness_n_m"]) for n in GAS_JOINTS},
                damping=3.0,
                effort_limit_sim=2000.0,
                velocity_limit_sim=1000.0,
                armature={n: armature(n) for n in GAS_JOINTS},
                friction=0.0,
            ),
            "passive_pins": ImplicitActuatorCfg(
                joint_names_expr=list(PASSIVE_JOINTS),
                stiffness=0.0,
                damping={n: damping(n) for n in PASSIVE_JOINTS},
                effort_limit_sim=1.0e6,
                velocity_limit_sim=1000.0,
                armature={n: armature(n) for n in PASSIVE_JOINTS},
                friction=0.0,
            ),
        },
    )
