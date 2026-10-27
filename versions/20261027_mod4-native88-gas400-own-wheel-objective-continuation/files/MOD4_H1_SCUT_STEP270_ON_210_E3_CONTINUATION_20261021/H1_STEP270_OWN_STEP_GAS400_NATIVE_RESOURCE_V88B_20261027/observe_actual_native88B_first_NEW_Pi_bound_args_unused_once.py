"""Exact-bound wrapper: original transport intentionally resets sys.argv."""
from pathlib import Path
import sys,runpy,hashlib
N=Path(__file__).resolve().parent;R=N/'reports';T=N.parent
D=T/'MOD4_H1_OVERNIGHT_FUDAN_SUPERMIMIC_REPAIR_GOAL_20261027/native88_first_policy_closure_review_source_v1'
entry=D/'observe_native88_first_new_policy_finite_unused_once.py'
assert hashlib.sha256(entry.read_bytes()).hexdigest()=='318eb3b05de59d692f6f8560d3a728d1140e1af37241abff5fd4bd1f20d49078'
assert not (R/'NATIVE88_FIRST_NEW_POLICY_OBSERVER_STARTED_ACTUAL.json').exists(),'No actual first-observer rearm'
sys.argv=[str(entry),'--stage',str(N),'--prepared-report',str(R/'NATIVE88_TWO_PAYLOADS_SOURCE_PREPARED_ACTUAL.json'),'--detached-report',str(R/'NATIVE88B_ACTUAL_OWNER_NODES_DETACHED.json'),'--go-report',str(R/'NATIVE88B_ACTUAL_SIGNED_TWO_GO_METADATA_ACTUAL.json')]
runpy.run_path(str(entry),run_name='__main__')
