"""UNUSED bound closing wrapper; no remote imports before original900 gate."""
from pathlib import Path
import sys,runpy,hashlib,json,time
N=Path(__file__).resolve().parent;R=N/'reports';T=N.parent
D=T/'MOD4_H1_OVERNIGHT_FUDAN_SUPERMIMIC_REPAIR_GOAL_20261027/native88C_exact_reset_bank_lifecycle_source_v1'
entry=D/'collect_native88_finals_actual_cost_unused_once.py'
assert hashlib.sha256(entry.read_bytes()).hexdigest()=='707b202c333cf91c9af7e9982213e5827ede498a8b23f88ef4c5ffe0c5ec5b48'
go=json.loads((R/'NATIVE88C_ACTUAL_SIGNED_TWO_GO_METADATA_ACTUAL.json').read_bytes())['go']
assert set(go)=={'h1','recovery'} and max(x['nominal_end_epoch'] for x in go.values())-time.time()<=900,'Original actual-GO900 gate, do not execute early'
assert not (R/'NATIVE88_CLOSING_COLLECTOR_STARTED_ACTUAL.json').exists(),'No collector rearm'
sys.argv=[str(entry),'--stage',str(N),'--prepared-report',str(R/'NATIVE88_TWO_PAYLOADS_SOURCE_PREPARED_ACTUAL.json'),'--detached-report',str(R/'NATIVE88C_ACTUAL_OWNER_NODES_DETACHED.json'),'--go-report',str(R/'NATIVE88C_ACTUAL_SIGNED_TWO_GO_METADATA_ACTUAL.json')]
runpy.run_path(str(entry),run_name='__main__')
