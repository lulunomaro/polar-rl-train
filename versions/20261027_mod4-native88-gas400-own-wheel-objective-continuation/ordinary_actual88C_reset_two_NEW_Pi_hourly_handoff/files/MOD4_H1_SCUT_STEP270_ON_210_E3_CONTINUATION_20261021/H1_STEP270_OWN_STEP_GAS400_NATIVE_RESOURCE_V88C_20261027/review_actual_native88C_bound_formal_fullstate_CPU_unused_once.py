"""UNUSED localCPU wrapper; new formal publications only, initial loads once."""
from pathlib import Path
import sys,runpy,hashlib
N=Path(__file__).resolve().parent;R=N/'reports';T=N.parent
D=T/'MOD4_H1_OVERNIGHT_FUDAN_SUPERMIMIC_REPAIR_GOAL_20261027/native88C_exact_reset_bank_lifecycle_source_v1'
entry=D/'review_native88_finals_initial_CPU_unused_once.py'
assert hashlib.sha256(entry.read_bytes()).hexdigest()=='a97587c3ee6ff7015949d06aa429851026f8d3837ab65bda56f69a048906bbb9'
assert (R/'NATIVE88_FINALS_AND_ORIGINAL_COST_RETURNED_ACTUAL.json').is_file(),'Actual collection must return first'
assert not (R/'NATIVE88_INITIAL_CPU_ENTRY_CONSUMED_ACTUAL.json').exists(),'No initial model-reader replay'
witness=T/'H1_STEP270_THREE_GPU_NATIVE_CONTINUATION_RESOURCE_V86B_20261026/current_baseline_closed_models/h1/model_update138.pt'
sys.argv=[str(entry),'--stage',str(N),'--prepared-report',str(R/'NATIVE88_TWO_PAYLOADS_SOURCE_PREPARED_ACTUAL.json'),'--detached-report',str(R/'NATIVE88C_ACTUAL_OWNER_NODES_DETACHED.json'),'--collected-report',str(R/'NATIVE88_FINALS_AND_ORIGINAL_COST_RETURNED_ACTUAL.json'),'--cpu-report',str(R/'NATIVE88_ACTUAL_TWO_SOURCE_CPU_AND_RESOURCE_RETURNED_ACTUAL.json'),'--bootstrap-witness',str(witness),'--bootstrap-bytes','16868635']
runpy.run_path(str(entry),run_name='__main__')
