"""Unused V2 frozen cases from CPU-verified exact140 source bindings."""
from pathlib import Path
import sys,os,time,json,importlib.util,traceback
D=Path(__file__).resolve().parent;E=D/'curb140_frozen35_3060_v2';R=D/'reports';sys.path.insert(0,str(E));import transport_249_exact_desktop_role_stdin_v5 as t
def put(n,v):
 with (R/n).open('x',encoding='utf8') as f:json.dump(v,f,indent=2)
def load(path,name):
 s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def main():
 assert json.loads((R/'CURB140_V6_EXACT_SOURCE_BINDINGS_LOCAL_CONSTRUCTOR_NEGATIVE_CPU_ACTUAL.json').read_bytes())['passed_CPU_only'];put('CURB140_BINDING_FIXED_V6_FINITE_STARTED_ACTUAL.json',dict(epoch=time.time(),pid=os.getpid(),actual_alive_only_exclusive_210_72_249_transport_owner=True,no_PPO_or_budget=True));finite=load(E/'run_new_CURB35_native_full_finite_v3_once.py','v2_finite_helpers')
 for steps in (120,1500):
  m=load(E/'dispatch_curb113_frozen3060_unused_case_once.py','v2_dispatch_'+str(steps));sys.argv=[str(E/'dispatch_curb113_frozen3060_unused_case_once.py'),'--steps',str(steps),'--execute-own-unused-case'];m.main();finite.wait(steps);finite.run('collect_curb113_own_case_actual_readonly.py',['--steps',str(steps)]);finite.run('review_curb35_learned140_actual_physical_CPU_v2.py',['--steps',str(steps)],finite.CPU);print(json.dumps(dict(actual_complete_CPU_admitted=steps,source='CURB140',case_namespace='v2',no_PPO=True)),flush=True)
 put('CURB140_BINDING_FIXED_V6_NATIVE_FULL_FINITE_COMPLETE_ACTUAL.json',dict(epoch=time.time(),native120_full1500_actual_CPU_complete=True,no_PPO_or_budget=True))
if __name__=='__main__':
 try:main()
 except BaseException:put('CURB140_BINDING_FIXED_V6_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(epoch=time.time(),error=traceback.format_exc(),unknown_mutation_readonly_first_no_blind_replay=True));raise
