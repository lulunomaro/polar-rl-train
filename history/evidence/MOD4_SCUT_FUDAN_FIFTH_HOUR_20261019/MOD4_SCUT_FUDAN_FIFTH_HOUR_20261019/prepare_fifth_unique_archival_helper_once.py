"""Prepare a new stage's single record helper; never rerun a prior record."""
from pathlib import Path
import ast
B=Path(__file__).resolve().parent;P=B.parent/'MOD4_SCUT_FUDAN_FOURTH_HOUR_20261019'
s=(P/'archive_fourth_reward_hour_closed_sources_local_feedback_unique_once.py').read_text('utf8')
changes={
"G=W/'MOD4_SCUT_FUDAN_THIRD_HOUR_20261019'":"G=W/'MOD4_SCUT_FUDAN_FOURTH_HOUR_20261019'",
"BASE='3da5b5769c0ec2d0864364c1ab1eba25fbb55479'":"BASE='8c243d4ce3aee3f876f72d863977322c11e96f54'",
'scut-fudan-fourth-hour-closed-sources-source-phase-feedback':'scut-fudan-fifth-hour-closed-sources-local-recovery-feedback',
'Continue three experts from third reward-hour finals and record local takeoff landing without recovery':'Continue three experts from fourth reward-hour finals and record local survival recovery and normal drift',
'len(old)==1388':'len(old)==1389',
'MOD4_SCUT_FUDAN_THIRD_HOUR_20261019/REPORT_CAPTURE_INDEX.json':'MOD4_SCUT_FUDAN_FOURTH_HOUR_20261019/REPORT_CAPTURE_INDEX.json',
'THIRD_SCUT_FUDAN_HOUR_NEW_SOURCE_LOCAL_MUJOCO_BEHAVIOR_ACTUAL.json':'FOURTH_SCUT_FUDAN_HOUR_NEW_SOURCE_LOCAL_MUJOCO_BEHAVIOR_ACTUAL.json',
"len(git('tag','--list').splitlines())==1389":"len(git('tag','--list').splitlines())==1390",
'total_tags=1389,all1388old_objects_peels_exact=True':'total_tags=1390,all1389old_objects_peels_exact=True',
'Actual full prior finals/cost/out; upstream formula differential and clipping CPU; public4 normal exact; actual loaded new reward recipe and three GO/positive PPO/GPU compute; original physics/accounting retained.':'Actual fourth-hour full models and17Adam CPU/cost/out/locks; same reward bytes and target SDK/RSL/runtime; three new GO/positive PPO/GPU compute; four new-source local trajectories and explicit recovery/normal-drift/torque-readout limits; original physics/accounting retained.'
}
for a,b in changes.items():
 assert a in s,a
 s=s.replace(a,b)
ast.parse(s)
with (B/'archive_fifth_reward_hour_closed_sources_local_recovery_unique_once.py').open('x',encoding='utf8') as f:f.write(s)
print('New archival helper prepared; not recorded or pushed.')
