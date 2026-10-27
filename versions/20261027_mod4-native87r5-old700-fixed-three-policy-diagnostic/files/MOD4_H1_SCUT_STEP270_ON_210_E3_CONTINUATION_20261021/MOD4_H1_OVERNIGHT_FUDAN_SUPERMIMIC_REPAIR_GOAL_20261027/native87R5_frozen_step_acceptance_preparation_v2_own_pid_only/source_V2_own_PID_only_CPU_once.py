"""New V2 pure process-factory spies + actual collected identity metadata, no host queries."""
from pathlib import Path
import json,sys,ast
D=Path(__file__).resolve().parent;N=D.parent.parent/'H1_STEP270_THREE_GPU_OWN_FUDAN_NATIVE_V87_20261027'
sys.path.insert(0,str(D))
from native87R5_own_pid_out_guard_v1 import *
first=json.loads((N/'reports/AVAILABLE_TWO_NATIVE87R5_FIRST_GO_ACTUAL_NEW_PREUPDATE_PI_RETURNED_ACTUAL.json').read_bytes())
detached=json.loads((N/'reports/AVAILABLE_TWO_NATIVE87R5_ACTUAL_OWNER_NODES_DETACHED.json').read_bytes())
rows=records_from_evidence(dict(first_identity=first,detached=detached));checks=[]
def yes(v,name):assert v,name;checks.append(name)
def refuse(fn,name):
    try:fn()
    except (ValueError,KeyError):checks.append(name);return
    raise AssertionError(name)
class Missing(Exception):pass
calls=[]
def missing(pid):calls.append(pid);raise Missing()
value=assert_recorded_own_out(rows,missing,Missing,execution_backend='target72')
yes(value['passed'] and calls==[r['pid'] for r in rows if not r['role'].startswith('h1_')],'only_actual_recorded_own_PIDs_probed')
calls.clear()
assert_recorded_own_out(rows,missing,Missing,execution_backend='source210')
yes(calls==[r['pid'] for r in rows if r['role'].startswith('h1_')],'source210_never_probes_72_owner_or_recovery_PIDs')
refuse(lambda:assert_recorded_own_out(rows,missing,Missing,execution_backend='unknown'),'unknown_backend_refused_before_process_probe')
class Recycled:
    def __init__(self,pid):self.pid=pid
    def create_time(self):return next(r['creation'] for r in rows if r['pid']==self.pid)+100
    def __getattr__(self,k):raise AssertionError('forbidden foreign attribute '+k)
yes(assert_recorded_own_out(rows,Recycled,Missing,execution_backend='target72')['passed'],'recycled_PID_no_foreign_argv_or_exe_query')
class OwnAlive(Recycled):
    def create_time(self):return next(r['creation'] for r in rows if r['pid']==self.pid)
refuse(lambda:assert_recorded_own_out(rows,OwnAlive,Missing,execution_backend='target72'),'still_live_original_own_PID_refused')
refuse(lambda:validate_rows(rows[:-1]),'missing_identity_refused')
bad=[dict(r) for r in rows];bad[-1]['pid']=bad[0]['pid'];refuse(lambda:validate_rows(bad),'duplicate_PID_refused')
bad=[dict(r) for r in rows];bad[1]['creation']=float('nan');refuse(lambda:validate_rows(bad),'nonfinite_creation_refused')
entry=(D/'native87R5_frozen_single_sdk_entry_unused_once.py').read_text()
yes('psutil.process_iter' not in entry and "assert_recorded_own_out(q['known_qualified_own_processes']" in entry,'active_entry_no_global_process_scan')
yes("records_from_evidence(values)" in entry,'own_PID_rows_bound_to_copied_actual_first_and_detached_reports')
old=ast.parse((D/'V1_ENTRY_BEFORE_OWN_PID_ONLY_GUARD.original_bytes.txt').read_bytes());new=ast.parse(entry)
# All other top-level functions exact, except evidence binding and resources.
def funcs(t):return {n.name:ast.dump(n,include_attributes=False) for n in t.body if isinstance(n,ast.FunctionDef)}
a=funcs(old);b=funcs(new)
yes(all(a[k]==b[k] for k in a if k not in ('validate_evidence','resource_admission')),'other_entry_functions_AST_unchanged')
out=dict(passed=True,count=len(checks),checks=checks,actual_identity_source_metadata_only=True,
 any_process_or_remote_or_model_or_GPU_query=False,V1_tests_not_rerun=True,
 V1_source_privacy_rejection_preserved=True)
with (D/'V2_OWN_PID_ONLY_SOURCE_CPU_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(out,f,indent=2)
print(json.dumps(dict(passed=True,count=len(checks))))

