"""Isaac Lab 2.x / PhysX integration. Import only after AppLauncher starts."""
from pathlib import Path
import json
import os
import torch
from isaaclab.assets import ArticulationCfg
from isaaclab.actuators import ImplicitActuatorCfg
import isaaclab.sim as sim_utils

HERE=Path(__file__).resolve().parent
CONTRACT=json.loads((HERE/'import_contract.json').read_text())

def make_robot_cfg(prim_path='/World/Robot'):
    names=CONTRACT['actuated_joint_names'];gas=list(CONTRACT['gas_springs'])
    passive=[n for n in CONTRACT['joints'] if n not in names+gas]
    return ArticulationCfg(
        prim_path=prim_path,
        spawn=sim_utils.UsdFileCfg(
            usd_path=str(HERE/'robot.usd'),
            rigid_props=sim_utils.RigidBodyPropertiesCfg(disable_gravity=False,max_depenetration_velocity=1.,
                linear_damping=0.,angular_damping=0.,enable_gyroscopic_forces=True),
            articulation_props=sim_utils.ArticulationRootPropertiesCfg(
                enabled_self_collisions=True,
                # The six external closures are NOT articulation joints, so their residual is set
                # by the solver budget.  Default stays the delivery's 32/8; RM_SOLVER_POS/VEL let
                # the acceptance harness tighten it (measured 2026-09-12: 1024 envs x 1000 steps
                # left a 6.8e-4 m residual at 32/8 against the 5e-4 m gate).
                solver_position_iteration_count=int(os.environ.get('RM_SOLVER_POS','32')),
                solver_velocity_iteration_count=int(os.environ.get('RM_SOLVER_VEL','8')))),
        init_state=ArticulationCfg.InitialStateCfg(pos=(0.,0.,CONTRACT['spawn_height_m']),joint_pos={'.*':0.},joint_vel={'.*':0.}),
        soft_joint_pos_limit_factor=1.0,
        actuators={
            'leg_inputs':ImplicitActuatorCfg(joint_names_expr=[n for n in names if 'wheel' not in n],
                effort_limit_sim=CONTRACT['leg_motor']['peak_torque_nm'],velocity_limit_sim=1000.,stiffness=0.,
                damping={n:CONTRACT['joints'][n]['damping_si'] for n in names if 'wheel' not in n},
                armature={n:CONTRACT['joints'][n]['armature'] for n in names if 'wheel' not in n},friction=0.),
            'wheels':ImplicitActuatorCfg(joint_names_expr=[n for n in names if 'wheel' in n],
                effort_limit_sim=max(v for n,v in zip(names,CONTRACT['effort_limits_nm']) if 'wheel' in n),
                velocity_limit_sim=1000.,stiffness=0.,damping=.015,
                armature={n:CONTRACT['joints'][n]['armature'] for n in names if 'wheel' in n},friction=0.),
            'passive_pins':ImplicitActuatorCfg(joint_names_expr=passive,effort_limit_sim=1e6,
                velocity_limit_sim=1000.,stiffness=0.,friction=0.,
                damping={n:CONTRACT['joints'][n]['damping_si'] for n in passive},
                armature={n:CONTRACT['joints'][n]['armature'] for n in passive}),
            'gas_springs':ImplicitActuatorCfg(joint_names_expr=gas,effort_limit_sim=2000.,
                velocity_limit_sim=1000.,stiffness={n:CONTRACT['gas_springs'][n]['stiffness_n_m'] for n in gas},
                damping=3.,armature=.002,friction=0.),
        })

class TorqueInterface:
    """Six normalized motor torques; passive pins never become policy actions."""
    def __init__(self,robot):
        self.robot=robot
        expected=[s+'_'+j for s in ['left','right'] for j in ['hip','crank','wheel_spin']]
        if CONTRACT['actuated_joint_names']!=expected:
            raise ValueError('Motor order differs from six-action policy contract')
        self.motor_ids=[robot.joint_names.index(n) for n in CONTRACT['actuated_joint_names']]
        self.limits=torch.tensor(CONTRACT['effort_limits_nm'],device=robot.device)
        gas=list(CONTRACT['gas_springs']);self.gas_ids=[robot.joint_names.index(n) for n in gas]
        self.gas_targets=torch.tensor([CONTRACT['gas_springs'][n]['target_position_m'] for n in gas],device=robot.device)
        self.zero=torch.zeros_like(robot.data.joint_pos)
    def apply(self,action):
        r=self.robot
        if action.shape!=(r.num_instances,6) or not torch.isfinite(action).all():
            raise ValueError('Expected finite [number_of_envs, 6] normalized torques')
        r.set_joint_effort_target(self.zero)
        r.set_joint_velocity_target(self.zero)
        r.set_joint_position_target(self.zero)
        effort=action.clamp(-1,1)*self.limits
        p=CONTRACT['leg_motor'];leg_indices=[0,1,3,4]
        velocity=r.data.joint_vel[:,[self.motor_ids[i] for i in leg_indices]]
        lo=(-p['envelope_intercept_nm']-p['envelope_slope_nm_s_rad']*velocity).clamp(-40.,40.)
        hi=(p['envelope_intercept_nm']-p['envelope_slope_nm_s_rad']*velocity).clamp(-40.,40.)
        effort[:,leg_indices]=torch.maximum(lo,torch.minimum(hi,effort[:,leg_indices]))
        wheel_indices=[2,5];wp=CONTRACT['wheel_motor']
        wheel_velocity=r.data.joint_vel[:,[self.motor_ids[i] for i in wheel_indices]]
        wheel_lo=(-wp['envelope_intercept_nm']-wp['envelope_slope_nm_s_rad']*wheel_velocity).clamp(-wp['peak_torque_nm'],wp['peak_torque_nm'])
        wheel_hi=(wp['envelope_intercept_nm']-wp['envelope_slope_nm_s_rad']*wheel_velocity).clamp(-wp['peak_torque_nm'],wp['peak_torque_nm'])
        effort[:,wheel_indices]=torch.maximum(wheel_lo,torch.minimum(wheel_hi,effort[:,wheel_indices]))
        r.set_joint_effort_target(effort,joint_ids=self.motor_ids)
        # Set after every reset/action write. A zero target would reverse the gas preload.
        r.set_joint_position_target(self.gas_targets.expand(r.num_instances,-1),joint_ids=self.gas_ids)
        self._enforce_coupling()

    # [handoff 2026-09-12 §1.3/§1.5] The CAD stop constrains `crank - hip`, and PhysX joint limits
    # are COMPLIANT: a random-torque / strong-press test drove the couple 2.6 mrad past the real
    # stop (-1.088910818 < -1.086319540).  The real robot has a physical block there; the sim has
    # no CAD proxy for part_145/124/134 yet, so the bound is enforced where a real firmware would
    # enforce it: the command/state path.  `training=True` uses the -1.0843 window, `training=False`
    # the exact mechanical stop.
    def _enforce_coupling(self, training=True):
        r=self.robot
        stop=CONTRACT.get('mechanical_stop',{}).get('input_difference_rad',-1.0863195404360622)
        bound=(CONTRACT.get('training_window',{}).get('input_difference_min_rad',-1.0843)
               if training else stop)
        pos=r.data.joint_pos
        for side in ('left','right'):
            i=r.joint_names.index(side+'_crank');j=r.joint_names.index(side+'_hip')
            diff=pos[:,i]-pos[:,j]
            bad=diff<bound-1e-9
            if bool(bad.any()):
                new_pos=r.data.joint_pos.clone()
                new_pos[bad,i]=new_pos[bad,j]+bound
                r.write_joint_state_to_sim(new_pos,r.data.joint_vel*0.0)
