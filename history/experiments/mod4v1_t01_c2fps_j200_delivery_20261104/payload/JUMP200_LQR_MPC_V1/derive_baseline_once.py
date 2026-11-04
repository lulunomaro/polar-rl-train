"""Small source adaptation of actual270mm timed LQR runner, not a QA/approval layer."""
from pathlib import Path
import json
D=Path(__file__).resolve().parent;R=D.parent
s=(R/'run_jump270_audit_v2.py').read_text(encoding='utf-8')
s=s.replace('270mm prototype','200mm extra-fixture prototype')
s=s.replace('import numpy as np,mujoco',"sys.path.insert(0,str(Path(__file__).resolve().parents[1]))\nimport numpy as np,mujoco",1)
s=s.replace('from physics_bridge_contact_audit_v2 import ContactAuditPlant as BufferedImuPlant','from JUMP200_LQR_MPC_V1.bridge200 import ContactAuditPlant as BufferedImuPlant',1)
s=s.replace('from ground_controller_v4 import GroundController','from scalar_ground_mpc_v1 import GroundController',1)
s=s.replace('step=StepPatch();','step=StepPatch(top_z_m=.2);',1)
s=s.replace("abs(pos[2]-.27)","abs(pos[2]-.20)")
s=s.replace("src=[Path(__file__),", "src=[Path(__file__),ROOT/'JUMP200_LQR_MPC_V1/bridge200.py',ROOT/'scalar_ground_mpc_v1.py',",1)
s=s.replace('SENSORONLY_TIMED_JUMP270_ROLLVMC_V2_NOT_CONTACTFSM_RELEASE','JUMP200_LOCAL_MOD4_LQR_PHASES_AND_GROUND_ONLY_SCALAR_MPC_NOT_AERIAL_MPC')
needle="  h=hashlib.sha256();n=0\n"
assert needle in s
extra="""  result.update(fixture=dict(kind='EXTRA_VERTICAL_STEP_NOT_ORIGINAL_CAD',height_m=.200,front_x=0.,depth_m=3.,width_m=2.,legacy_geom_name='step270',actual_height_not_name=.200),robot_bodies=int(p.m.nbody)-1,physics_dt_s=p.dt,control_dt_s=.01,solver='original_Newton100_unmodified',approach_ground_MPC=dict(ctrl.usage),landing_ground_MPC=dict(land.usage),MPC_actual_scope='existing15-step8-state+lag scalar common-wheel QP during approach/recovery ONLY; no aerial/contact/vertical MPC',first_step_contact=p.j200_first_contact,success_200mm_top_stable2s=bool(stable>=2. and len(rows)==N and first_clear is not None and p.guide_contact_ticks==0 and p.hard_contact_ticks==0),nominal_only_not_DR_reliability=True)
"""
s=s.replace(needle,extra+needle,1)
# Require all20last physics samples on main-wheel TOP support for each stable bin.
s=s.replace("topbearing=bool(np.min(topforces)>1 and env['all_footprints_within_top_geometric'])", "topbearing=bool(np.min(topforces)>1 and env['all_footprints_within_top_geometric'] and len(p.audit_samples)>=20 and all(min(z['top_main_normal_N2'])>1. and z['guide_normal_N']<=1. and z['hard_other_normal_N']<=1. for z in p.audit_samples[-20:]))",1)
# Add real phase-specific MPC accounting to each100Hz control record.
s=s.replace('stable_s=stable))',"stable_s=stable,ground_MPC_phase=phase in('approach','recovery'),ground_MPC_last=dict((ctrl if phase=='approach'else land).mpc.log)if phase in('approach','recovery')else None))",1)
with(D/'run_case.py').open('x',encoding='utf-8',newline='\n')as f:f.write(s)
c=dict(kind='J200_BASELINE001_FROZEN_BEFORE_FIRST_NEW_NOMINAL',seed=200001,nominal=True,duration_s=8.,start_x=-.8,command_at_s=.6,launch_distance_m=.3,recover_after_push_s=.72,speed=1.4,push_roll_kp=40.,push_roll_kd=5.,push_reserve_Nm=8.,ground_roll_kp=20.,extra_step_height_m=.2,source_parameters='existingJUMP270_GAIN_BANK_reference_not_fitted_to_this_case',MPC='actual scalar_ground_mpc_v1 in approach/recovery only')
with(D/'baseline001.json').open('x',encoding='utf-8')as f:json.dump(c,f,indent=2)
print('RUNNABLE_BASELINE',D/'run_case.py','CONFIG',D/'baseline001.json','NO_PHYSICS_YET')
