"""Make a separately named, reproducible rescue source; never patch a running task."""
from pathlib import Path
import json
import shutil
import py_compile

p=Path(__file__).parent
out=p/'rescue';out.mkdir(exist_ok=True)
s=(p/'mod4_task.py').read_text(encoding='utf8')
s=s.replace('import skills_isaac as skills  # noqa: E402','import skills_isaac as skills  # noqa: E402\nimport scut_flat_rescue as scut_rescue')
s=s.replace('torch.full((env.num_envs, 1), 0.24, device=env.device)','torch.full((env.num_envs, 1), _f("RM_NOMINAL_HEIGHT", .25), device=env.device)')
s=s.replace('randomize_leg_start = EventTerm(func=randomize_leg_start, mode="reset")','randomize_leg_start = None  # replaced by full constraint-consistent reset below')
s=s.replace('randomize_wheel_vel = EventTerm(func=randomize_wheel_vel, mode="reset")','randomize_wheel_vel = None  # basic locomotion stage: zero initial wheel velocity')
s=s.replace('@configclass\nclass RewardsCfg:', '    consistent_start = EventTerm(func=scut_rescue.consistent_reset, mode="reset")\n\n\n@configclass\nclass RewardsCfg:')
assert 'consistent_start = EventTerm' in s
s=s.replace('heading=(-math.pi, math.pi)','heading=(0.0, 0.0)')
s=s.replace('func=track_lin_vel_gated','func=scut_rescue.linear_exp')
s=s.replace('func=track_lin_vel_huge_gap','func=scut_rescue.linear_gap')
s=s.replace('func=track_lin_vel_square_gated','func=scut_rescue.linear_square')
s=s.replace('func=track_ang_vel_gated','func=scut_rescue.yaw_exp')
s=s.replace('flat_orientation = RewTerm(func=skills.flat_orientation_jump_exempt, weight=SCUT_ORIENT_W)', '''flat_orientation = None
    flat_orientation_y = RewTerm(func=scut_rescue.orientation, weight=-1., params={"mode":"pitch"})
    flat_orientation_y_v = RewTerm(func=scut_rescue.orientation, weight=-1., params={"mode":"pitch_velocity"})
    flat_orientation_x_v = RewTerm(func=scut_rescue.orientation, weight=-1., params={"mode":"roll_velocity"})
    no_fork = RewTerm(func=scut_rescue.no_fork, weight=-1., params={"axis":0})
    no_fork_z = RewTerm(func=scut_rescue.no_fork, weight=-2., params={"axis":2})
    wheel_motor_z_axis_align_exp = RewTerm(func=scut_rescue.leg_gravity_alignment, weight=.1, params={"sigma":.01})
    wheel_motor_z_axis_align_exp_tight = RewTerm(func=scut_rescue.leg_gravity_alignment, weight=.1, params={"sigma":.001})''')
s=s.replace('joint_power = RewTerm(func=skills.joint_power_motors, weight=SCUT_POWER_W,\n                          params={"joint_names": LEG_ORDER + WHEEL_ORDER})','joint_power = RewTerm(func=scut_rescue.wheel_power, weight=SCUT_POWER_W)')
s=s.replace('weight=-0.2,\n                           params={"leg_joint_names": LEG_ORDER}', 'weight=0.0,\n                           params={"leg_joint_names": LEG_ORDER}')
# Exact upstream reward table; constraints remain enforced by physical limits / safety guards.
s=s.replace('weight=-5.0)','weight=0.0)')
(out/'mod4_task.py').write_text(s,encoding='utf8')
for name in ['skills_isaac.py','train_mod4_ppo.py','mod4_env.py','scut_flat_rescue.py','reset_bank.json']:
    shutil.copyfile(p/name,out/name)
env=json.loads((p/'run_manifest.json').read_text())['env']
env.update(RM_KEEP_STD='1',RM_VEL_HEIGHT_GATE='off',RM_SCUT_H_SQ_W='0',
           RM_SCUT_BASE_CONTACT_W='0',RM_RANDOM_START='0',RM_NOMINAL_HEIGHT='.25',
           RM_HEIGHT_MIN='.25',RM_HEIGHT_MAX='.25',RM_W_HEIGHT_DEFICIT='0',RM_W_HEIGHT_LINEAR='0',
           RM_SCUT_H_SOFT_SIGMA='.1',RM_HEIGHT_BOTH_WHEELS_W='.3',RM_JUMP_SCRIPT_PROB='0')
(out/'env.json').write_text(json.dumps(env,indent=2),encoding='utf8')
for f in out.glob('*.py'):py_compile.compile(str(f),doraise=True)
print(out)
