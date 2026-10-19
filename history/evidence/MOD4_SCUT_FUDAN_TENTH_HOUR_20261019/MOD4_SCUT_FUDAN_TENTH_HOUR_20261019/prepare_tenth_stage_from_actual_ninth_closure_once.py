"""Prepare the authorized unchanged continuation; no transport or GPU admission claim."""
from pathlib import Path
import ast, hashlib, json, re, shutil, time
B=Path(__file__).resolve().parent; P=B.parent/'MOD4_SCUT_FUDAN_NINTH_HOUR_20261019'; R=B/'reports'; R.mkdir(exist_ok=True)
H=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
f=json.loads((P/'reports/THREE_HOUR_ALL_CLOSED_FINAL_MODELS_ORIGINAL_COST_CPU_ACTUAL.json').read_bytes())
c=json.loads((P/'reports/THREE_HOUR_MISSING_CLOSED_FINAL_COLLECTION_ACTUAL.json').read_bytes())
assert f['passed_all_three_whole_final_models_CPU'] and c['actual_closed'] and c['actual_finite_transport_returned']
assert not (R/'TENTH_STAGE_PREPARED_NOT_DISPATCHED_ACTUAL.json').exists()
for name in ('prepare_next_three_closed_sources_one_hour_CPU_once.py','deploy_three_next_closed_source_hours_once.py','closed_production_continuation_CPU_v2.py','collect_next_three_actual_learning_metadata_finite_once.py'):
    dest=B/name; assert not dest.exists(); shutil.copy2(P/'future_same_recipe_hour_templates'/name,dest); ast.parse(dest.read_text('utf8'))
def rename(text,mapping):return re.sub('|'.join(mapping),lambda m:mapping[m.group()],text)
def defs(s):return {x.name:ast.dump(x,include_attributes=False) for x in ast.parse(s).body if isinstance(x,(ast.ClassDef,ast.FunctionDef)) and x.name in ('Policy','Sim','min_z')}
old=(P/'review_eighth_reward_hour_new_source_local_behavior_once.py').read_text('utf8')
s=rename(old,{'MOD4_SCUT_FUDAN_EIGHTH_HOUR_20261019':'MOD4_SCUT_FUDAN_NINTH_HOUR_20261019','EIGHTH':'NINTH','eighth':'ninth','hour8':'hour9'})
assert defs(s)==defs(old) and s.count('actuator_rows.append(')==1 and s.count('reward_rows.append(')==1
target=B/'review_ninth_reward_hour_new_source_local_behavior_once.py'
with target.open('x',encoding='utf8',newline='\n') as stream:stream.write(s)
with (R/'NINTH_CLOSED_SOURCE_LOCAL_DIAGNOSTIC_PREPARED_CPU_ACTUAL.json').open('x',encoding='utf8') as stream:
    json.dump(dict(epoch=time.time(),source=f['experts']['h1']['final'],new_script_SHA=H(target),source_SHA_is_actual_file_bytes=True,previous_protocol_source=str(P/'review_eighth_reward_hour_new_source_local_behavior_once.py'),only_new_source_four_trajectories=True,same_Policy_Sim_geometry_AST=True,original_control_physics_phase_thresholds_and_actual_local_force_readout_unchanged=True,no_duplicate_telemetry_insertion=True,no_PhysX_live_player_GPU_or_account_change=True),stream,indent=2)
for name in ('review_eighth_local_strict_recovery_normal_and_actuator_CPU_once.py','review_eighth_local_events_and_drift_CPU_once.py'):
    s=(P/name).read_text('utf8')
    s=rename(s,{'MOD4_SCUT_FUDAN_EIGHTH_HOUR_20261019':'MOD4_SCUT_FUDAN_NINTH_HOUR_20261019','EIGHTH':'NINTH','SEVENTH':'EIGHTH','eighth':'ninth','seventh':'eighth'})
    s=s.replace('EIGHTH_HOUR_LOCAL_EVENTS_AND_NORMAL_MIXED_CHANGE_CPU_ACTUAL.json','EIGHTH_HOUR_LOCAL_EVENTS_AND_DRIFT_CPU_ACTUAL.json')
    s=s.replace("retained_original_yaw_objective_source_audit=str(P/'reports/NORMAL_YAW_RATE_SOURCE_OBJECTIVE_CPU_ACTUAL.json')","retained_original_yaw_objective_source_audit=str(B.parent/'MOD4_SCUT_FUDAN_EIGHTH_HOUR_20261019/reports/NORMAL_YAW_RATE_SOURCE_OBJECTIVE_CPU_ACTUAL.json')")
    ast.parse(s)
    with (B/name.replace('eighth','ninth')).open('x',encoding='utf8',newline='\n') as stream:stream.write(s)
with (R/'TENTH_STAGE_PREPARED_NOT_DISPATCHED_ACTUAL.json').open('x',encoding='utf8') as stream:
    json.dump(dict(epoch=time.time(),previous_owner=293563,previous_actual_full_closed_and_whole_CPU=True,same_recipe_templates_copied_exact=True,reserved_remote_namespace='T3sf10_1910v15',previous_collector_target_resources=c['target_resources'],status='prepared_only_resource_admission_pending',unidentified_GPU_peer_not_bypassed=True,peer_identity_and_workload_unknown=True,no_new_owner_node_worker_GO_or_GPU_task=True,no_account_reward_physics_change=True),stream,indent=2)
print(json.dumps(dict(prepared_only=True,new_H1_source=f['experts']['h1']['final']['SHA'],resource_admission_pending=True)))
