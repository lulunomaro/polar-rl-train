from pathlib import Path
import ast,json
T=Path(__file__).resolve().parent;P=T/'H1_STEP270_E3_REPAIR_PAIR_V3_20261022'
a=json.loads((P/'reports/PAIR_ACTUAL_GO_POSITIVE_PPO_UUID_CREATE_ARGV_VERIFIED_ACTUAL.json').read_bytes());assert a['passed']
old=(T/'prepare_pair_V2_reserved_workflow_source_once.py').read_text('utf8')
s=old.replace("P=T/'H1_STEP270_E3_PAIR_V1_20261021';N=T/'H1_STEP270_E3_PAIR_V2_20261022'","P=T/'H1_STEP270_E3_REPAIR_PAIR_V3_20261022';N=T/'H1_STEP270_E3_PAIR_V4_20261022'")
s=s.replace('sequence=2','sequence=4').replace('H1_STEP270_RECOVERY_ORIGINAL_1792597123349933700',a['run_id']).replace('H1step270_joint_2210v2','H1step270_joint_2210v4')
s=s.replace("new=new.replace('both_installed_source_CPU_and_H1_actual_native_query_reuse=True'", "new=new.replace(\";q['previous_owner_root']='/mnt/mod4_linux_durable_20261013/H1s270_E3bridge_2210v7/owner'\",'')\nnew=new.replace('both_installed_source_CPU_and_H1_actual_native_query_reuse=True'")
s=s.replace('PAIR_V2_RESERVED_SAMEPHASE_WORKFLOW_SOURCE_CPU_ACTUAL.json','PAIR_V4_RESERVED_SAMEPHASE_WORKFLOW_SOURCE_CPU_ACTUAL.json')
ast.parse(s);exec(compile(s,'new_pair4_reserved_source_generation','exec'),dict(__file__=str(T/'prepare_pair_V4_samephase_reserved_after_actual_repair_PPO_once.py'),__name__='__main__'))
