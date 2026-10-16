"""Only unused native/full, same package and source, precise desktop role fix."""
from pathlib import Path
import sys,json,time,os,subprocess,importlib.util,traceback
D=Path(__file__).resolve().parent;E=D/'curb140_frozen35_3060_v1';R=D/'reports';sys.path.insert(0,str(E));import transport_249_exact_deepseek_desktop_role_v4 as t
def put(n,v):
 with (R/n).open('x',encoding='utf8') as f:json.dump(v,f,indent=2)
def module(path,name):
 s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def dispatch(steps):
 m=module(E/'dispatch_curb113_frozen3060_unused_case_once.py','unused_dispatch_'+str(steps));m.t=t;sys.argv=[str(E/'dispatch_curb113_frozen3060_unused_case_once.py'),'--steps',str(steps),'--execute-own-unused-case'];m.main()
def main():
 assert json.loads((R/'EXACT_DESKTOP_ROLE_GUARD_NEGATIVES_AND_EVAL_UNUSED_CPU_ACTUAL.json').read_bytes())['passed_CPU_only'];put('CURB140_EXACT_ROLE_NEW_FINITE_V4_STARTED_ACTUAL.json',dict(epoch=time.time(),pid=os.getpid(),creation_UTC=subprocess.check_output(['powershell','-NoProfile','-Command',"(Get-Process -Id %d).StartTime.ToUniversalTime().ToString('o')"%os.getpid()]).decode().strip(),actual_alive_only_exclusive_210_72_249_transport_owner=True,no_PPO_or_budget=True));c=None
 try:
  c=t.connect();g=t.py(c,t.guard_code());assert g['shared_OS_lock_free'] and g['new_root_unused'];parent=str(Path(t.ROOT).parent).replace('\\','/');created=t.py(c,"from pathlib import Path;import json;B=Path("+repr(parent)+");assert B.resolve().is_relative_to(Path('D:/MOD4_async_eval').resolve()) and not B.exists();B.mkdir();print(json.dumps(dict(new_parent=str(B),no_GPU=True)))");put('CURB140_EXACT_DESKTOP_ROLE_RESOURCE_ADMITTED_ACTUAL.json',dict(epoch=time.time(),guard=g,new_parent=created,original_unknown_rejection_preserved=True,no_other_application_changed=True))
 finally:t.close(c)
 f=module(E/'run_new_CURB35_native_full_finite_v3_once.py','original_unused_finite_helpers')
 for steps in (120,1500):
  dispatch(steps);f.wait(steps);f.run('collect_curb113_own_case_actual_readonly.py',['--steps',str(steps)]);f.run('review_curb35_learned140_actual_physical_CPU_v2.py',['--steps',str(steps)],f.CPU);print(json.dumps(dict(actual_complete_CPU_admitted=steps,source='CURB140',no_PPO=True)),flush=True)
 put('CURB140_EXACT_ROLE_UNUSED_NATIVE_FULL_V4_COMPLETE_ACTUAL.json',dict(epoch=time.time(),native120_and_full1500_CPU_complete=True,allown_cases_consumed_no_repeat=True,no_PPO_or_budget=True))
if __name__=='__main__':
 try:main()
 except BaseException:put('CURB140_EXACT_ROLE_FINITE_V4_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(epoch=time.time(),error=traceback.format_exc(),unknown_mutation_readonly_first_no_blind_replay=True));raise
