"""Prepare new independent archive and actual monitor-reader helpers, no record yet."""
from pathlib import Path
import ast
B=Path(__file__).resolve().parent;P=B.parent/'MOD4_SCUT_FUDAN_FIFTH_HOUR_20261019'
s=(P/'archive_fifth_reward_hour_closed_sources_local_recovery_unique_once.py').read_text('utf8')
changes={
"G=W/'MOD4_SCUT_FUDAN_FOURTH_HOUR_20261019'":"G=W/'MOD4_SCUT_FUDAN_FIFTH_HOUR_20261019'",
"BASE='8c243d4ce3aee3f876f72d863977322c11e96f54'":"BASE='84a3c6183d6d03e70b69fab924d759fb41f1d765'",
'scut-fudan-fifth-hour-closed-sources-local-recovery-feedback':'scut-fudan-sixth-hour-closed-sources-local-recovery-review',
'Continue three experts from fourth reward-hour finals and record local survival recovery and normal drift':'Continue three experts from fifth reward-hour finals and record local recovery events with late yaw drift',
'len(old)==1389':'len(old)==1390',
'MOD4_SCUT_FUDAN_FOURTH_HOUR_20261019/REPORT_CAPTURE_INDEX.json':'MOD4_SCUT_FUDAN_FIFTH_HOUR_20261019/REPORT_CAPTURE_INDEX.json',
'FOURTH_SCUT_FUDAN_HOUR_NEW_SOURCE_LOCAL_MUJOCO_BEHAVIOR_ACTUAL.json':'FIFTH_SCUT_FUDAN_HOUR_NEW_SOURCE_LOCAL_MUJOCO_BEHAVIOR_ACTUAL.json',
"len(git('tag','--list').splitlines())==1390":"len(git('tag','--list').splitlines())==1391",
'total_tags=1390,all1389old_objects_peels_exact=True':'total_tags=1391,all1390old_objects_peels_exact=True',
'Actual fourth-hour full models and17Adam CPU/cost/out/locks; same reward bytes and target SDK/RSL/runtime; three new GO/positive PPO/GPU compute; four new-source local trajectories and explicit recovery/normal-drift/torque-readout limits; original physics/accounting retained.':'Actual fifth-hour whole models17Adam CPU/cost/out/locks; same reward bytes and installed target SDK/RSL/runtime; three new GO/positive PPO/GPU compute; four new-source local traces with original recovery events and late yaw residuals, actual local actuator force and source byteSHA clarification; original physics/accounting retained.'
}
for q,z in changes.items():assert q in s,q;s=s.replace(q,z)
ast.parse(s)
with (B/'archive_sixth_reward_hour_closed_sources_local_feedback_unique_once.py').open('x',encoding='utf8') as f:f.write(s)
s=(P/'review_actual_monitor_readback_and_future_helpers_CPU_once.py').read_text('utf8')
for q,z in [('FIFTH_HOUR_V27','SIXTH_HOUR_V28'),('AUTOMATION_V27','AUTOMATION_V28'),('235200','246762'),('T3sf6_1910v11','FUTURE_ROOT'),('T3sf5_1910v10','T3sf6_1910v11'),('FUTURE_ROOT','T3sf7_1910v12')]:assert q in s,q;s=s.replace(q,z)
ast.parse(s)
with (B/'review_actual_monitor_readback_and_future_helpers_CPU_once.py').open('x',encoding='utf8') as f:f.write(s)
print('Sixth-stage unique archive and monitor reader prepared only.')
