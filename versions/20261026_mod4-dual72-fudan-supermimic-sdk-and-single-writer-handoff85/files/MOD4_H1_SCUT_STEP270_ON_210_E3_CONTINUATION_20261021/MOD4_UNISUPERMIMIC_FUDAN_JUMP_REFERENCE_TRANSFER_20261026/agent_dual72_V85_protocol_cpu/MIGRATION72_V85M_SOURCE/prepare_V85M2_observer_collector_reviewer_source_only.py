"""Generate lifecycle readers from reviewed pair source; never run readers."""
from pathlib import Path
import ast
import json
import time

HERE=Path(__file__).resolve().parent;P=HERE.parent
def write(name,text):
    ast.parse(text)
    with (HERE/name).open('x',encoding='utf8') as stream:stream.write(text)

old=(P/'observe_dual72_V85_owner_native_E3_first_UNUSED.py').read_text('utf8')
old=old.replace("R=N/'reports'","R=N/'reports'\nsys.path.insert(0,str(N))",1)
old=old.replace('DUAL72_V85_ORIGINAL_ACCOUNT_DETACHED_ACTUAL.json','V85M2_SINGLE72_OWNER_NODES_DETACHED_ACTUAL.json')
old=old.replace("H1_STEP270_DUAL72_FUDAN_SUPERMIMIC_E3_RESOURCE_V85_20261026","H1_STEP270_DUAL72_FUDAN_SUPERMIMIC_E3_MIGRATED_V85M2_20261026")
old=old.replace("C=Path('/home/egde/rl_candidates/MOD4_native_floor_continue10h_20260930/TRAINING_BUDGET_10H.json')","C=Path('/home/lc01/Zonglin Li/zonglin2/state/mod4_single_canonical_authority_20261026/TRAINING_BUDGET_10H.json')")
old=old.replace("assert c['authorized_training_seconds']==2268000 and len(c['budget_extensions'])==9","assert c['authorized_training_seconds']==2268000 and c['historical_budget_extension_count']==9 and c['new_authority_budget_extensions']==[] and c['authority_generation']=='MOD4_SINGLE_WRITER72_20261026'")
old=old.replace("'/home/egde/rl_candidates/MOD4_scut_spin_rate_20261002/autonomy_controller.lock'","str(C.parent/'autonomy_controller.lock')")
old=old.replace("sys.path.insert(0,str(T/'MOD4_MOE_T2Z_SINGLE4090_QUANTIZED_PREPARATION_20261025'));import strict_user_forwarded_original210_transport_v1 as route\n c=route.connect()", "sp=importlib.util.spec_from_file_location('memory',W/'MOD4_BUDGET_ADD100H_EIGHTH_20261021/run_authorized_cohort50_with_existing_hidden_stdin_memory.py');m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m);secret=m.recover();c=d.connect72(secret);secret=None")
old=old.replace('a=d.code(c,route.PY,READ210','a=d.code(c,d.PY72,READ210')
old=old.replace("'DUAL72_V85_ACTUAL_GO_NATIVE_E3_UUID_CREATE_ARGV_VERIFIED_ACTUAL.json'","'V85M2_SINGLE72_GO_NATIVE_E3_UUID_ACTUAL.json'")
old=old.replace('H1_E3_actual_PPO_and_H1_method_native_policy_positive','E3_PPO_and_H1_native_policy_positive').replace('all_three_distinct_expected_4090_UUIDs','both_distinct_expected_4090_UUIDs').replace('one_original_writer_three_distinct_actual_intervals','one_authority72_writer_two_distinct_actual_intervals')
write('observe_V85M2_single72_native_E3_first_UNUSED.py',old)

old=(P/'collect_dual72_V85_finals_original_cost_UNUSED.py').read_text('utf8')
old=old.replace("N=Path(__file__).resolve().parent;W=N.parent.parent;R=N/'reports'","N=Path(__file__).resolve().parent;W=N.parent.parent;R=N/'reports'\nsys.path.insert(0,str(N))",1)
old=old.replace("'/home/egde/rl_candidates/MOD4_native_floor_continue10h_20260930/TRAINING_BUDGET_10H.json'","'/home/lc01/Zonglin Li/zonglin2/state/mod4_single_canonical_authority_20261026/TRAINING_BUDGET_10H.json'")
old=old.replace("len(c['budget_extensions'])==9","c['historical_budget_extension_count']==9 and c['new_authority_budget_extensions']==[] and c['authority_generation']=='MOD4_SINGLE_WRITER72_20261026'")
old=old.replace("Path('/home/egde/rl_candidates/MOD4_scut_spin_rate_20261002/autonomy_controller.lock')","C.parent/'autonomy_controller.lock'")
old=old.replace("sys.path.insert(0,str(N.parent/'MOD4_MOE_T2Z_SINGLE4090_QUANTIZED_PREPARATION_20261025'));import strict_user_forwarded_original210_transport_v1 as route", "# Current authority and both nodes are on72; no210 route")
old=old.replace("c=route.connect();a=d.code(c,route.PY,READ210","c=d.connect72(secret);a=d.code(c,d.PY72,READ210")
old=old.replace("capture(c,a,[],'owner',route.PY)","capture(c,a,[],'owner',d.PY72)")
old=old.replace('DUAL72_V85_ACTUAL_GO_NATIVE_E3_UUID_CREATE_ARGV_VERIFIED_ACTUAL.json','V85M2_SINGLE72_GO_NATIVE_E3_UUID_ACTUAL.json')
old=old.replace('DUAL72_V85_ORIGINAL_ACCOUNT_DETACHED_ACTUAL.json','V85M2_SINGLE72_OWNER_NODES_DETACHED_ACTUAL.json')
old=old.replace('DUAL72_V85_NATIVE_E3_AND_ORIGINAL_COST_RETURNED_ACTUAL.json','V85M2_SINGLE72_NATIVE_E3_AND_ACTUAL_COST_RETURNED_ACTUAL.json')
write('collect_V85M2_single72_finals_actual_cost_UNUSED.py',old)

old=(P/'review_dual72_V85_native_E3_fullstate_CPU_UNUSED.py').read_text('utf8')
old=old.replace('import json,time,torch','import json,time,torch,sys')
old=old.replace("N=Path(__file__).resolve().parent;R=N/'reports';read=", "N=Path(__file__).resolve().parent;R=N/'reports';sys.path.insert(0,str(N));read=",1)
old=old.replace('DUAL72_V85_NATIVE_E3_AND_ORIGINAL_COST_RETURNED_ACTUAL.json','V85M2_SINGLE72_NATIVE_E3_AND_ACTUAL_COST_RETURNED_ACTUAL.json')
old=old.replace('DUAL72_V85_NATIVE_E3_AND_ORIGINAL_COST_CPU_ACTUAL.json','V85M2_SINGLE72_NATIVE_E3_AND_ACTUAL_COST_CPU_ACTUAL.json')
write('review_V85M2_single72_native_E3_fullstate_CPU_UNUSED.py',old)
print(json.dumps(dict(source_readers_written=True,no_readers_executed=True)))
