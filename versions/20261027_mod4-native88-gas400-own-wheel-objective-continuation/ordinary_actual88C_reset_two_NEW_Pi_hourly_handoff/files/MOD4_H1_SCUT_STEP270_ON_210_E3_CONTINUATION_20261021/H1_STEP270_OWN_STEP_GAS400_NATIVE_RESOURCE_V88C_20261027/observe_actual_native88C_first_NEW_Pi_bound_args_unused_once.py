from pathlib import Path
import sys,runpy,hashlib
N=Path(__file__).resolve().parent;R=N/'reports';T=N.parent
D=T/'MOD4_H1_OVERNIGHT_FUDAN_SUPERMIMIC_REPAIR_GOAL_20261027/native88C_exact_reset_bank_lifecycle_source_v1'
entry=D/'observe_native88_first_new_policy_finite_unused_once.py'
assert hashlib.sha256(entry.read_bytes()).hexdigest()=='33a1a6ead645f3e22110db0f36c7d6c20ec78a4bea8d1934ec0a4a3acfbd5fb6'
assert not (R/'NATIVE88_FIRST_NEW_POLICY_OBSERVER_STARTED_ACTUAL.json').exists(),'no first-observer rearm'
sys.argv=[str(entry),'--stage',str(N),'--prepared-report',str(R/'NATIVE88_TWO_PAYLOADS_SOURCE_PREPARED_ACTUAL.json'),'--detached-report',str(R/'NATIVE88C_ACTUAL_OWNER_NODES_DETACHED.json'),'--go-report',str(R/'NATIVE88C_ACTUAL_SIGNED_TWO_GO_METADATA_ACTUAL.json')]
runpy.run_path(str(entry),run_name='__main__')
