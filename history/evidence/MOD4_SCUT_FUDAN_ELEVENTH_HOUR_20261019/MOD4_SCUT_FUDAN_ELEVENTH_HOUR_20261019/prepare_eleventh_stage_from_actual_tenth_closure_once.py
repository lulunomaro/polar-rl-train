"""Copy only current sharing-aware templates and prepare a new-source local diagnostic."""
from pathlib import Path
import ast,hashlib,json,re,shutil,time
B=Path(__file__).resolve().parent;P=B.parent/'MOD4_SCUT_FUDAN_TENTH_HOUR_20261019';R=B/'reports';R.mkdir(exist_ok=True)
H=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def put(name,value):
 with (R/name).open('x',encoding='utf8') as stream:json.dump(value,stream,indent=2)
f=json.loads((P/'reports/THREE_HOUR_ALL_CLOSED_FINAL_MODELS_ORIGINAL_COST_CPU_ACTUAL.json').read_bytes());assert f['passed_all_three_whole_final_models_CPU'] and f['all_actual_owner_nodes_children_out_canonicalNone_real_locks_free']
assert not (R/'ELEVENTH_STAGE_CURRENT_TEMPLATES_COPIED_ACTUAL.json').exists()
for name in ('prepare_next_three_closed_sources_one_hour_CPU_once.py','deploy_three_next_closed_source_hours_once.py','closed_production_continuation_CPU_v2.py','collect_next_three_actual_learning_metadata_finite_once.py'):
 target=B/name;assert not target.exists();shutil.copy2(P/'future_same_recipe_hour_templates'/name,target);ast.parse(target.read_text('utf8'))
def rename(text,mapping):return re.sub('|'.join(mapping),lambda m:mapping[m.group()],text)
def defs(s):return {x.name:ast.dump(x,include_attributes=False) for x in ast.parse(s).body if isinstance(x,(ast.ClassDef,ast.FunctionDef)) and x.name in ('Policy','Sim','min_z')}
old=(P/'review_ninth_reward_hour_new_source_local_behavior_once.py').read_text('utf8')
s=rename(old,{'MOD4_SCUT_FUDAN_NINTH_HOUR_20261019':'MOD4_SCUT_FUDAN_TENTH_HOUR_20261019','NINTH':'TENTH','ninth':'tenth','hour9':'hour10'})
assert defs(s)==defs(old) and s.count('actuator_rows.append(')==1 and s.count('reward_rows.append(')==1
target=B/'review_tenth_reward_hour_new_source_local_behavior_once.py'
with target.open('x',encoding='utf8',newline='\n') as stream:stream.write(s)
put('TENTH_CLOSED_SOURCE_LOCAL_DIAGNOSTIC_PREPARED_CPU_ACTUAL.json',dict(epoch=time.time(),source=f['experts']['h1']['final'],new_script_SHA=H(target),source_SHA_is_actual_file_bytes=True,previous_protocol_source=str(P/'review_ninth_reward_hour_new_source_local_behavior_once.py'),only_new_source_four_trajectories=True,same_Policy_Sim_geometry_AST=True,original_control_physics_phase_thresholds_and_actual_local_force_readout_unchanged=True,no_duplicate_telemetry_insertion=True,no_PhysX_live_player_GPU_or_account_change=True))
for name in ('review_ninth_local_strict_recovery_normal_and_actuator_CPU_V2_missing_only_once.py','review_ninth_local_events_and_drift_CPU_V2_missing_only_once.py'):
 s=(P/name).read_text('utf8')
 s=rename(s,{'MOD4_SCUT_FUDAN_NINTH_HOUR_20261019':'MOD4_SCUT_FUDAN_TENTH_HOUR_20261019','NINTH':'TENTH','EIGHTH':'NINTH','ninth':'tenth','eighth':'ninth'})
 # The inherited objective audit is still the actual eighth-hour report, not a guessed new alias.
 s=s.replace("B.parent/'MOD4_SCUT_FUDAN_NINTH_HOUR_20261019/reports/NORMAL_YAW_RATE_SOURCE_OBJECTIVE_CPU_ACTUAL.json'","B.parent/'MOD4_SCUT_FUDAN_EIGHTH_HOUR_20261019/reports/NORMAL_YAW_RATE_SOURCE_OBJECTIVE_CPU_ACTUAL.json'")
 ast.parse(s)
 with (B/name.replace('ninth','tenth').replace('_V2_missing_only','')).open('x',encoding='utf8',newline='\n') as stream:stream.write(s)
put('ELEVENTH_STAGE_CURRENT_TEMPLATES_COPIED_ACTUAL.json',dict(epoch=time.time(),previous_actual_owner306868_closed_whole_CPU=True,current_sharing_aware_templates_exact=True,reserved_next_root='T3sf11_1910v16',no_deployment_or_old_case_replay_yet=True))
print(json.dumps(dict(new_stage_prepared=True,H1_source=f['experts']['h1']['final']['SHA'])))
