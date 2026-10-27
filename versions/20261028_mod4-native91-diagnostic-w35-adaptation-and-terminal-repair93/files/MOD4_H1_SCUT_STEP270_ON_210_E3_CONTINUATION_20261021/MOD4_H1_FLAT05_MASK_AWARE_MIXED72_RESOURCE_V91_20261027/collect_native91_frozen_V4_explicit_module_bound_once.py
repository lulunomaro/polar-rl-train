"""Bind the exact frozen reader module after a local import-only failure.

No original900/850/180 guard, remote body, account or model check changes.
"""
from pathlib import Path
import hashlib,json,runpy,sys,time,types,traceback
N=Path(__file__).resolve().parent;T=N.parent;R=N/'reports'
F=T/'MOD4_H1_OVERNIGHT_FUDAN_SUPERMIMIC_REPAIR_GOAL_20261027/H1_W35_native91_correct_normal900_collector_v4_source'
CORE=F/'collect_native91_H1_formal_and_W35_failed_original_cost_UNUSED_once_v4.py'
MODULE=F/'native91_H1_W35_natural_closing_remote_CODE_v4.py'

def put(name,value):
 with (R/name).open('x',encoding='utf8') as f:json.dump(value,f,indent=2)

def main():
 assert not (R/'NATIVE91_NORMAL_CLOSING_CONSUMED_ACTUAL_V4.json').exists()
 assert hashlib.sha256(CORE.read_bytes()).hexdigest()=='0f18e2c9153f8923b473afeb87132f05e85c818538a100dfab9f6bd91f07ed61'
 assert hashlib.sha256(MODULE.read_bytes()).hexdigest()=='e4d9728012cfecf97d83bfa7597ccc141fa03b2a2e4496670e08fe9007d3f0be'
 put('NATIVE91_LOCAL_COLLECTOR_IMPORT_ONLY_FAILURE_AND_BOUND_FIX_ACTUAL.json',dict(epoch=time.time(),original_error='ModuleNotFoundError: native91_H1_W35_natural_closing_remote_CODE_v4',before_main_consumed_marker_network_or_account=True,frozen_remote_module_exists=True,Python_safe_path_false=True,underlying_import_lookup_cause_not_proven=True,fix='Load only exact frozen module bytes into expected sys.modules name before invoking unchanged frozen V4 main',no_remote_body_guard_or_model_changes=True))
 name='native91_H1_W35_natural_closing_remote_CODE_v4'
 module=types.ModuleType(name);module.__file__=str(MODULE);exec(compile(MODULE.read_bytes(),str(MODULE),'exec'),module.__dict__);sys.modules[name]=module
 runpy.run_path(str(CORE),run_name='__main__')

if __name__=='__main__':
 try:main()
 except BaseException:put('NATIVE91_BOUND_CLOSE_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(traceback=traceback.format_exc(),no_rearm_kill_or_account_write=True));raise
