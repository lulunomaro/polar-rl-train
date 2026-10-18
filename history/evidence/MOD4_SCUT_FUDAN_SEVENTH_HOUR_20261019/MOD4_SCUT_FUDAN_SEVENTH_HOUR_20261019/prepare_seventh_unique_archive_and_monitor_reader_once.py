"""Prepare a new stage archive and monitor reader; no record or prior helper replay."""
from pathlib import Path
import ast
B=Path(__file__).resolve().parent;P=B.parent/'MOD4_SCUT_FUDAN_SIXTH_HOUR_20261019'
s=(P/'archive_sixth_reward_hour_closed_sources_local_feedback_unique_once.py').read_text('utf8')
changes={
"G=W/'MOD4_SCUT_FUDAN_FIFTH_HOUR_20261019'":"G=W/'MOD4_SCUT_FUDAN_SIXTH_HOUR_20261019'",
"BASE='84a3c6183d6d03e70b69fab924d759fb41f1d765'":"BASE='a88ae83344f3a9e50edb43e2f78a064bb791f83e'",
'scut-fudan-sixth-hour-closed-sources-local-recovery-review':'scut-fudan-seventh-hour-closed-sources-local-yaw-feedback',
'Continue three experts from fifth reward-hour finals and record local recovery events with late yaw drift':'Continue three experts from sixth reward-hour finals and record earlier local yaw drift',
'len(old)==1390':'len(old)==1391',
'MOD4_SCUT_FUDAN_FIFTH_HOUR_20261019/REPORT_CAPTURE_INDEX.json':'MOD4_SCUT_FUDAN_SIXTH_HOUR_20261019/REPORT_CAPTURE_INDEX.json',
'FIFTH_SCUT_FUDAN_HOUR_NEW_SOURCE_LOCAL_MUJOCO_BEHAVIOR_ACTUAL.json':'SIXTH_SCUT_FUDAN_HOUR_NEW_SOURCE_LOCAL_MUJOCO_BEHAVIOR_ACTUAL.json',
"len(git('tag','--list').splitlines())==1391":"len(git('tag','--list').splitlines())==1392",
'total_tags=1391,all1390old_objects_peels_exact=True':'total_tags=1392,all1391old_objects_peels_exact=True',
'Actual fifth-hour whole models17Adam CPU/cost/out/locks; same reward bytes and installed target SDK/RSL/runtime; three new GO/positive PPO/GPU compute; four new-source local traces with original recovery events and late yaw residuals, actual local actuator force and source byteSHA clarification; original physics/accounting retained.':'Actual sixth-hour whole models17Adam CPU/cost/out/locks; identical reward bytes and target SDK/RSL/runtime; three new GO/positive PPO/GPU compute; four new-source local traces retaining recovery events with earlier yaw drift and normal drift residuals, actual local actuator force; original physics/accounting retained.'
}
for q,z in changes.items():assert q in s,q;s=s.replace(q,z)
ast.parse(s)
with (B/'archive_seventh_reward_hour_closed_sources_local_yaw_unique_once.py').open('x',encoding='utf8') as f:f.write(s)
s=(P/'review_actual_monitor_readback_and_future_helpers_CPU_once.py').read_text('utf8')
for q,z in [('SIXTH_HOUR_V28','SEVENTH_HOUR_V29'),('AUTOMATION_V28','AUTOMATION_V29'),('246762','258398'),('T3sf7_1910v12','FUTURE_ROOT'),('T3sf6_1910v11','T3sf7_1910v12'),('FUTURE_ROOT','T3sf8_1910v13')]:assert q in s,q;s=s.replace(q,z)
ast.parse(s)
with (B/'review_actual_monitor_readback_and_future_helpers_CPU_once.py').open('x',encoding='utf8') as f:f.write(s)
print('Seventh-stage archive and monitor reader prepared only.')
