"""Prepare four new-source local trajectories, preserving the established protocol."""
from pathlib import Path
import ast, hashlib, json, time
B=Path(__file__).resolve().parent;W=B.parent;R=B/'reports'
P=W/'MOD4_SCUT_FUDAN_TWELFTH_HOUR_20261019'
K=W/'MOD4_SCUT_FUDAN_ELEVENTH_HOUR_20261019'
f=json.loads((P/'reports/THREE_HOUR_ALL_CLOSED_FINAL_MODELS_ORIGINAL_COST_CPU_ACTUAL.json').read_bytes())
assert f['passed_all_three_whole_final_models_CPU'] and f['all_actual_owner_nodes_children_out_canonicalNone_real_locks_free']
prior=json.loads((K/'reports/TENTH_SCUT_FUDAN_HOUR_NEW_SOURCE_LOCAL_MUJOCO_BEHAVIOR_ACTUAL.json').read_bytes())
assert all(x['SHA']!=f['experts']['h1']['final']['SHA'] for x in prior['episodes'])
created=[]
for oldname,newname in [
 ('review_tenth_reward_hour_new_source_local_behavior_once.py','review_twelfth_reward_hour_new_source_local_behavior_once.py'),
 ('review_tenth_local_strict_recovery_normal_and_actuator_CPU_once.py','review_twelfth_local_strict_recovery_normal_and_actuator_CPU_once.py'),
 ('review_tenth_local_events_and_drift_CPU_once.py','review_twelfth_local_events_and_drift_CPU_once.py')]:
 s=(K/oldname).read_text('utf8')
 if 'new_source_local_behavior' in oldname:
  s=s.replace("P=W/'MOD4_SCUT_FUDAN_TENTH_HOUR_20261019'","P=W/'MOD4_SCUT_FUDAN_TWELFTH_HOUR_20261019'")
 else:
  s=s.replace("P=B.parent/'MOD4_SCUT_FUDAN_TENTH_HOUR_20261019'","P=B.parent/'MOD4_SCUT_FUDAN_ELEVENTH_HOUR_20261019'")
 s=s.replace('TENTH_','TWELFTH_').replace('NINTH_','TENTH_').replace('after_reward_hour10','after_reward_hour12').replace('tenth','twelfth')
 ast.parse(s);p=B/newname
 with p.open('x',encoding='utf8',newline='\n') as stream:stream.write(s)
 raw=p.read_bytes();created.append(dict(path=str(p),bytes=len(raw),SHA=hashlib.sha256(raw).hexdigest()))
with (R/'TWELFTH_CLOSED_SOURCE_LOCAL_DIAGNOSTIC_PREPARED_CPU_ACTUAL.json').open('x',encoding='utf8') as stream:
 json.dump(dict(epoch=time.time(),new_complete_source=f['experts']['h1']['final'],new_script_SHA=created[0]['SHA'],actual_file_bytes_SHA=True,created=created,previous_source_behavior_report=str(K/'reports/TENTH_SCUT_FUDAN_HOUR_NEW_SOURCE_LOCAL_MUJOCO_BEHAVIOR_ACTUAL.json'),only_new_source_four_local_trajectories_prepared=True,old_source_case_not_replayed=True,original_prepare80_takeoff16_landing12_recovery200_callbacks_physics_external_request_clock_unchanged=True,read_only_formula_rates_actual_local_actuator_force_not_PhysX_or_PPO_return=True,no_player_remote_GPU_or_account_change=True),stream,indent=2)
print(json.dumps(dict(prepared_new_source=f['experts']['h1']['final']['SHA'],scripts=len(created),old_cases_not_replayed=True)))
