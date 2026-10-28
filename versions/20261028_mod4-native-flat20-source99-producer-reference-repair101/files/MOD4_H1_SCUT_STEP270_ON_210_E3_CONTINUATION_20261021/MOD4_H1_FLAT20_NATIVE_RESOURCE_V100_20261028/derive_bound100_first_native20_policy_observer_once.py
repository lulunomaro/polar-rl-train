from pathlib import Path
import ast,json,hashlib,time
N=Path(__file__).resolve().parent;T=N.parent;L=T/'MOD4_H1_OVERNIGHT_FUDAN_SUPERMIMIC_REPAIR_GOAL_20261027';O=L/'TWO99_TWO_NATIVE_FIRST_POLICY_OBSERVER_SOURCE_V1';B=L/'TWO100_TWO_NATIVE20_FIRST_POLICY_OBSERVER_SOURCE_V1';B.mkdir();(B/'reports').mkdir()
p=O/'observe_two99_two_native_first_policy_metadata_once_v1.py';s=p.read_text();tree=ast.parse(s);strings={x.targets[0].id:ast.literal_eval(x.value) for x in tree.body if isinstance(x,ast.Assign) and isinstance(x.targets[0],ast.Name) and x.targets[0].id in ['OWNER','NATIVE']}
owner=strings['OWNER'].replace("'restart'","'h1_seed28'");native=strings['NATIVE'].replace('own_MOD4_native_flat5cm_same_nominal400','own_MOD4_native_flat20cm_same_nominal400')
a="win['schema']=='mod4.native99.stance_'+spec['input_start_mode']+'.objective_window.v1'";assert native.count(a)==1;native=native.replace(a,"win['schema']=='mod4.native99_to_flat20.target100.objective_window.v1'")
a="assert win['reference_SHA']==spec['native_reference_SHA']";assert native.count(a)==1;native=native.replace(a,a+"\n  assert go['flat_jump_target_m']==positive['producer']['flat_jump_target_m']==positive['flat_real_physics_events']['height_m']==spec['flat_jump_target_m']==.20\n  assert positive['producer']['physical_initial_seed']==spec['native_seed'] and pre['actual_flat_counter_height_m']==pre['flat_goal_height_m']==.20")
for text in [owner,native]:ast.parse(text)
body=''.join(s.splitlines(keepends=True)[next(x for x in tree.body if isinstance(x,ast.ImportFrom)).lineno-1:]);body=body.replace('TWO99_GENUINE_NATIVE_START_COMPARISON_OWNER_SOURCE_V1','TWO100_TARGET20_TWO_NATIVE_ORIGINAL_OWNER_SOURCE_V1').replace('TWO99','TWO100').replace("'restart'","'h1_seed28'")
out='OWNER='+repr(owner)+'\nNATIVE='+repr(native)+'\n'+body;ast.parse(out);entry=B/'observe_two100_actual20cm_two_native_first_policy_metadata_once.py';entry.write_text(out,encoding='utf8')
(B/'FROZEN_UNUSED_TWO100_NATIVE20_FIRST_OBSERVER_INDEX_V1.json').write_text(json.dumps(dict(epoch=time.time(),unused=True,entry=str(entry),SHA=hashlib.sha256(entry.read_bytes()).hexdigest(),actual_goal_and_real_counter20_required=True,saved_learning27_physical27_28_required=True),indent=2),encoding='utf8')
print(json.dumps(dict(prepared=True,entry=str(entry))))
