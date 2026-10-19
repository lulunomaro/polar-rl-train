"""Prepare only four new-source traces with the existing measured protocol."""
from pathlib import Path
import ast,json,re,time,hashlib
B=Path(__file__).resolve().parent;P=B.parent/'MOD4_SCUT_FUDAN_EIGHTH_HOUR_20261019';R=B/'reports'
f=json.loads((P/'reports/THREE_HOUR_ALL_CLOSED_FINAL_MODELS_ORIGINAL_COST_CPU_ACTUAL.json').read_bytes());assert f['passed_all_three_whole_final_models_CPU']
H=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def defs(s):return {x.name:ast.dump(x,include_attributes=False) for x in ast.parse(s).body if isinstance(x,(ast.ClassDef,ast.FunctionDef)) and x.name in ('Policy','Sim','min_z')}
old=(P/'review_seventh_reward_hour_new_source_local_behavior_once.py').read_text('utf8')
mapping={'SEVENTH':'EIGHTH','seventh':'eighth','hour7':'hour8'}
s=re.sub('|'.join(mapping),lambda m:mapping[m.group()],old)
assert defs(s)==defs(old) and s.count('actuator_rows.append(')==1 and s.count('reward_rows.append(')==1
target=B/'review_eighth_reward_hour_new_source_local_behavior_once.py'
with target.open('x',encoding='utf8',newline='\n') as stream:stream.write(s)
with (R/'EIGHTH_CLOSED_SOURCE_LOCAL_DIAGNOSTIC_PREPARED_CPU_ACTUAL.json').open('x',encoding='utf8') as stream:
    json.dump(dict(epoch=time.time(),source=f['experts']['h1']['final'],new_script_SHA=H(target),source_SHA_is_actual_file_bytes=True,previous_protocol_source=str(P/'review_seventh_reward_hour_new_source_local_behavior_once.py'),only_new_source_four_trajectories=True,same_Policy_Sim_geometry_AST=True,original_control_physics_phase_thresholds_and_actual_local_force_readout_unchanged=True,no_duplicate_telemetry_insertion=True,no_PhysX_live_player_GPU_or_account_change=True),stream,indent=2)
old=(P/'review_seventh_local_strict_recovery_normal_and_actuator_CPU_once.py').read_text('utf8')
mapping={'SEVENTH':'EIGHTH','SIXTH':'SEVENTH','seventh':'eighth','sixth':'seventh'}
s=re.sub('|'.join(mapping),lambda m:mapping[m.group()],old)
s=s.replace('assert declared==normalized','assert declared==hashlib.sha256(actual).hexdigest()')
s=s.replace('field_is_LF_normalized_source_text_SHA=True','field_is_LF_normalized_source_text_SHA=False,field_is_actual_file_bytes_SHA=True')
ast.parse(s)
with (B/'review_eighth_local_strict_recovery_normal_and_actuator_CPU_once.py').open('x',encoding='utf8',newline='\n') as stream:stream.write(s)
print(json.dumps(dict(new_source=f['experts']['h1']['final']['SHA'],only_new_source_local_helpers_prepared=True)))
