"""Source-only while83B runs; no remote reads or training mutation."""
from pathlib import Path
import ast,importlib.util,json,time
import numpy as np
N=Path(__file__).resolve().parent;T=N.parent;R=N/'reports';P=T/'H1_STEP270_THREE_EXPERTS_RESOURCE_V80_20261026'
s=(P/'collect_closed80_landing_event_journal_small_CPU_unused_once.py').read_text('utf8').replace('CLOSED80','CLOSED83B').replace('closed80','closed83B').replace('new80','new83B').replace('complete80','complete83B').replace('indexed80','indexed83B').replace('2610v80/h1','2610v83b/h1').replace('H1_STEP270_CLOSED80_LANDING_JOURNAL_READONLY_20261026','H1_STEP270_CLOSED83B_LANDING_JOURNAL_READONLY_20261026')
assert '2610v80' not in s and 'CLOSED80' not in s;ast.parse(s)
reader=N/'collect_closed83B_landing_event_journal_small_CPU_unused_once.py'
with reader.open('x',encoding='utf8') as f:f.write(s)
B=T/'H1_STEP270_REWARD_PATH_V1_20261022';s=(B/'same_authorized_session_compressed_transport_v138.py').read_text('utf8');needle='    assert target.name in {';assert s.count(needle)==1;s=s.replace(needle,needle+'\n        '+repr(reader.name)+',',1)
with (B/'same_authorized_session_compressed_transport_v139.py').open('x',encoding='utf8') as f:f.write(s)
sp=importlib.util.spec_from_file_location('new83B_descriptive_reader',N/'analyze_closed83B_selected_landing_journal_CPU_unused_once.py');m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m)
tree=ast.parse((N/'payloads/h1/step270_goal_and_scut_rates_candidate.py').read_bytes());node=next(n for n in tree.body if isinstance(n,ast.ClassDef) and n.name=='Contract');contract={n.target.id:ast.literal_eval(n.value) for n in node.body if isinstance(n,ast.AnnAssign)}
def rows():
 count=4;r=dict(recorded_control_no=np.arange(10,14),root13=np.zeros((count,13),dtype=np.float32),history5ms=np.zeros((count,3,2,3),dtype=np.float32),raw_sampled6=np.zeros((count,6),dtype=np.float32),executed6=np.zeros((count,6),dtype=np.float32),episode=np.ones(count,dtype=np.int64),step_stable_ticks=np.arange(count,dtype=np.int64),step_success=np.zeros(count,dtype=bool),done=np.zeros(count,dtype=bool),public_request=np.ones(count,dtype=bool));r['root13'][:,6]=1;r['history5ms'][:,0,:,2]=10;return r
case=dict(case_id=0,env_id=1,episode=1,landing_control=11,last_control=13,closed_reason='post_control_limit');r=rows();value=m.summarize_arrays(r,case,contract);assert value['post_known_necessary_conditions_all_met_fraction']==1 and not value['reset_censored'] and value['executed6_equals_original_clip6']
r=rows();r['root13'][:,7]=.4;r['done'][-1]=True;r['raw_sampled6'][:,0]=8;r['executed6'][:,0]=6;value=m.summarize_arrays(r,dict(case,closed_reason='selected_reset_censored'),contract);assert value['post_planar_speed_above_original_fraction']==1 and value['reset_censored'] and value['executed6_equals_original_clip6'] and not value['recorded_original_success_any']
r=rows();r['history5ms'][:]=0;assert m.summarize_arrays(r,case,contract)['post_both_wheel_force_above_original_support_threshold_fraction']==0
r=rows();r['recorded_control_no'][2]+=10;rejected=False
try:m.summarize_arrays(r,case,contract)
except AssertionError:rejected=True
assert rejected
with (R/'SOURCE_ONLY83B_SMALL_JOURNAL_PROTOCOL_AND_DESCRIPTIVE_READER_CPU_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(dict(epoch=time.time(),prepared_source_only=True,actual_new_journal_not_read_yet=True,synthetic_CPU_source_contract_cases_passed=4,uses_exact_original_callback_quaternion_and_wheel_history_convention=True,no_assertion_of_SDK_or_training_quaternion_bug=True,not_training_GPU_or_skill_evidence=True,local_rg_wrong_optional_lib_isaaclab_path_retained_as_discovery_error=True,no_original80_or_other_consumed_binary_reextraction=True,no_remote_GPU_model_policy_or_training_mutation=True),f,indent=2)
print(json.dumps(dict(source_prepared=True,synthetic_CPU_cases=4,no_remote_training_or_actual_journal_read=True)))
