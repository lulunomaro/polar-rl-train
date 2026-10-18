"""Only the newly closed source; add local actuator-force readback without control changes."""
from pathlib import Path
import ast,json,time,hashlib
B=Path(__file__).resolve().parent;P=B.parent/'MOD4_SCUT_FUDAN_FIFTH_HOUR_20261019';R=B/'reports'
f=json.loads((P/'reports/THREE_HOUR_ALL_CLOSED_FINAL_MODELS_ORIGINAL_COST_CPU_ACTUAL.json').read_bytes());assert f['passed_all_three_whole_final_models_CPU']
old=(P/'review_fourth_reward_hour_new_source_local_behavior_once.py').read_text('utf8');s=old.replace("P=W/'MOD4_SCUT_FUDAN_FOURTH_HOUR_20261019'","P=W/'MOD4_SCUT_FUDAN_FIFTH_HOUR_20261019'")
for a,b in [('FOURTH_SCUT_FUDAN_HOUR','FIFTH_SCUT_FUDAN_HOUR'),('after_reward_hour4','after_reward_hour5'),('local_fourth_reward_hour','local_fifth_reward_hour'),('scut-fudan-fourth-hour','scut-fudan-fifth-hour')]:s=s.replace(a,b)
assert s.count('rows=[];reward_rows=[];')==1;s=s.replace('rows=[];reward_rows=[];','rows=[];reward_rows=[];actuator_rows=[];')
assert s.count('wheel_torque=tensor(np.asarray(tau)[[2,5]][None])')==1
s=s.replace('wheel_torque=tensor(np.asarray(tau)[[2,5]][None])','wheel_torque=tensor(np.asarray(d.actuator_force)[[2,5]][None])')
marker='      reward_rows.append('
assert s.count(marker)==1
s=s.replace(marker,'      actuator_rows.append([d.time,control,*np.asarray(tau),*np.asarray(d.actuator_force)])\n'+marker)
s=s.replace('reward_callback=np.asarray(reward_rows,dtype=np.float64))','reward_callback=np.asarray(reward_rows,dtype=np.float64),actuator_readback=np.asarray(actuator_rows,dtype=np.float64))')
s=s.replace('no_reward_used_for_control=True','no_reward_used_for_control=True,wheel_torque_input="actual local MuJoCo d.actuator_force indices2,5",actuator_readback_columns=["time","control","sent_d_ctrl6","actual_d_actuator_force6"],not_PhysX_applied_torque_readback=True)PLACEHOLDER')
# The replacement above adds only keyword fields inside the existing dict.
s=s.replace('True)PLACEHOLDER)','True)')
before=ast.parse(old);after=ast.parse(s)
def definitions(tree):return {n.name:ast.dump(n,include_attributes=False) for n in tree.body if isinstance(n,(ast.ClassDef,ast.FunctionDef)) and n.name in ('Policy','Sim','min_z')}
assert definitions(before)==definitions(after)
names={'mj_step','physical','begin_control','finish_control_before_selected_reset','action_to_torque','observation','observation_frame','_append_observation','reset'}
def calls(tree):return [ast.dump(n,include_attributes=False) for n in ast.walk(tree) if isinstance(n,ast.Call) and isinstance(n.func,ast.Attribute) and n.func.attr in names]
assert calls(before)==calls(after)
p=B/'review_fifth_reward_hour_new_source_local_behavior_once.py'
with p.open('x',encoding='utf8') as z:z.write(s)
with (R/'FIFTH_CLOSED_SOURCE_LOCAL_DIAGNOSTIC_PREPARED_CPU_ACTUAL.json').open('x',encoding='utf8') as z:json.dump(dict(epoch=time.time(),source=f['experts']['h1']['final'],previous_protocol_source=str(P/'review_fourth_reward_hour_new_source_local_behavior_once.py'),new_script_SHA=hashlib.sha256(s.encode()).hexdigest(),same_Policy_Sim_geometry_functions_AST=True,same_control_physics_phase_call_AST=True,only_new_source_four_trajectories=True,additional_readonly_actual_local_actuator_force=True,old_command_only_telemetry_retained_not_replayed=True,no_PhysX_live_player_GPU_or_account_change=True),z,indent=2)
print(json.dumps(dict(prepared=str(p),source_SHA=f['experts']['h1']['final']['SHA'])))
