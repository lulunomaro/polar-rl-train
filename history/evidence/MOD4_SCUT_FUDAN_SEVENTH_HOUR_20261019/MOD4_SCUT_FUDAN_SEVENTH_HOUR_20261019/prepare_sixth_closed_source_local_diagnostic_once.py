"""Copy the already instrumented local protocol for only this newly closed source."""
from pathlib import Path
import ast,json,time,hashlib
B=Path(__file__).resolve().parent;P=B.parent/'MOD4_SCUT_FUDAN_SIXTH_HOUR_20261019';R=B/'reports';H=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
f=json.loads((P/'reports/THREE_HOUR_ALL_CLOSED_FINAL_MODELS_ORIGINAL_COST_CPU_ACTUAL.json').read_bytes());assert f['passed_all_three_whole_final_models_CPU']
old=(P/'review_fifth_reward_hour_new_source_local_behavior_once.py').read_text('utf8');s=old.replace("P=W/'MOD4_SCUT_FUDAN_FIFTH_HOUR_20261019'","P=W/'MOD4_SCUT_FUDAN_SIXTH_HOUR_20261019'")
for a,b in [('FIFTH_SCUT_FUDAN_HOUR','SIXTH_SCUT_FUDAN_HOUR'),('after_reward_hour5','after_reward_hour6'),('local_fifth_reward_hour','local_sixth_reward_hour'),('scut-fudan-fifth-hour','scut-fudan-sixth-hour')]:s=s.replace(a,b)
def definitions(text):return {x.name:ast.dump(x,include_attributes=False) for x in ast.parse(text).body if isinstance(x,(ast.ClassDef,ast.FunctionDef)) and x.name in ('Policy','Sim','min_z')}
assert definitions(old)==definitions(s) and s.count('actuator_rows.append(')==1 and s.count('reward_rows.append(')==1
p=B/'review_sixth_reward_hour_new_source_local_behavior_once.py';assert not p.exists();p.write_bytes(s.encode('utf8'))
with (R/'SIXTH_CLOSED_SOURCE_LOCAL_DIAGNOSTIC_PREPARED_CPU_ACTUAL.json').open('x',encoding='utf8') as z:json.dump(dict(epoch=time.time(),source=f['experts']['h1']['final'],new_script_SHA=H(p),source_SHA_is_actual_file_bytes=True,previous_protocol_source=str(P/'review_fifth_reward_hour_new_source_local_behavior_once.py'),only_new_source_four_trajectories=True,same_Policy_Sim_geometry_AST=True,original_control_physics_phase_thresholds_and_actual_local_force_readout_unchanged=True,no_duplicate_telemetry_insertion=True,no_PhysX_live_player_GPU_or_account_change=True),z,indent=2)
s=(P/'review_fifth_local_strict_recovery_normal_and_actuator_CPU_once.py').read_text('utf8').replace("P=B.parent/'MOD4_SCUT_FUDAN_FIFTH_HOUR_20261019'","P=B.parent/'MOD4_SCUT_FUDAN_SIXTH_HOUR_20261019'")
for a,b in [('FIFTH_','SIXTH_'),('FOURTH_SCUT_FUDAN_HOUR','FIFTH_SCUT_FUDAN_HOUR'),('review_fifth_reward_hour','review_sixth_reward_hour'),('fifth-reward-hour','sixth-reward-hour')]:s=s.replace(a,b)
ast.parse(s);p=B/'review_sixth_local_strict_recovery_normal_and_actuator_CPU_once.py';assert not p.exists();p.write_bytes(s.encode('utf8'))
print(json.dumps(dict(new_local_source=f['experts']['h1']['final']['SHA'],local_protocol_prepared=True)))
