"""Prepare one new archive and an actual same-monitor readback helper."""
from pathlib import Path
import ast
B=Path(__file__).resolve().parent;P=B.parent/'MOD4_SCUT_FUDAN_SEVENTH_HOUR_20261019'
s=(P/'archive_seventh_reward_hour_closed_sources_local_yaw_unique_once.py').read_text('utf8')
changes={
"G=W/'MOD4_SCUT_FUDAN_SIXTH_HOUR_20261019'":"G=W/'MOD4_SCUT_FUDAN_SEVENTH_HOUR_20261019'",
"BASE='a88ae83344f3a9e50edb43e2f78a064bb791f83e'":"BASE='df17c5510a94bdb542fdc7cacc86abd2a0e41ef2'",
'scut-fudan-seventh-hour-closed-sources-local-yaw-feedback':'scut-fudan-eighth-hour-closed-sources-yaw-objective-review',
'Continue three experts from sixth reward-hour finals and record earlier local yaw drift':'Continue three experts from seventh reward-hour finals and review local holding with original yaw-rate objectives',
'len(old)==1391':'len(old)==1392',
'MOD4_SCUT_FUDAN_SIXTH_HOUR_20261019/REPORT_CAPTURE_INDEX.json':'MOD4_SCUT_FUDAN_SEVENTH_HOUR_20261019/REPORT_CAPTURE_INDEX.json',
'SIXTH_SCUT_FUDAN_HOUR_NEW_SOURCE_LOCAL_MUJOCO_BEHAVIOR_ACTUAL.json':'SEVENTH_SCUT_FUDAN_HOUR_NEW_SOURCE_LOCAL_MUJOCO_BEHAVIOR_ACTUAL.json',
"len(git('tag','--list').splitlines())==1392":"len(git('tag','--list').splitlines())==1393",
'total_tags=1392,all1391old_objects_peels_exact=True':'total_tags=1393,all1392old_objects_peels_exact=True',
'Actual sixth-hour whole models17Adam CPU/cost/out/locks; identical reward bytes and target SDK/RSL/runtime; three new GO/positive PPO/GPU compute; four new-source local traces retaining recovery events with earlier yaw drift and normal drift residuals, actual local actuator force; original physics/accounting retained.':'Actual seventh-hour whole models17Adam CPU/cost/out/locks; identical reward bytes and installed target SDK/RSL/runtime; three new GO/positive PPO/GPU compute; four new-source local traces with original recovery events and mixed normal drift, source-only yaw-rate objective review and preserved lookup failures; original physics/accounting retained.'
}
for q,z in changes.items():assert q in s,q;s=s.replace(q,z)
ast.parse(s)
with (B/'archive_eighth_reward_hour_closed_sources_yaw_objective_unique_once.py').open('x',encoding='utf8') as f:f.write(s)
s=(P/'review_actual_monitor_readback_and_future_helpers_CPU_once.py').read_text('utf8')
for q,z in [('SEVENTH_HOUR_V29','EIGHTH_HOUR_V30'),('AUTOMATION_V29','AUTOMATION_V30'),('258398','270162'),('T3sf8_1910v13','FUTURE_ROOT'),('T3sf7_1910v12','T3sf8_1910v13'),('FUTURE_ROOT','T3sf9_1910v14')]:assert q in s,q;s=s.replace(q,z)
ast.parse(s)
with (B/'review_actual_monitor_readback_and_future_helpers_CPU_once.py').open('x',encoding='utf8') as f:f.write(s)
print('Eighth-stage archive and monitor reader prepared only.')
