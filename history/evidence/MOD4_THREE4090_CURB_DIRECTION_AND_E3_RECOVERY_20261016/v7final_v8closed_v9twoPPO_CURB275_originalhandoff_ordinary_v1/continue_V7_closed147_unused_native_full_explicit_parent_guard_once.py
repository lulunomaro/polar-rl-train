from pathlib import Path
import sys,json,time,os,importlib.util,traceback
D=Path(__file__).resolve().parent;R=D/'reports';E=D/'curb_v7final147_frozen35_3060_v1';sys.path.insert(0,str(E))
def load(p,name):
 s=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def put(n,v):
 with (R/n).open('x',encoding='utf8') as f:json.dump(v,f,indent=2)
def main():
 assert json.loads((R/'V7_CLOSED147_DIRECTION_FROZEN3060_SOURCE_CPU_PREPARED_ACTUAL.json').read_bytes())['passed_CPU_only'];put('CURB_V7FINAL147_PARENTGUARD_FROZEN_FINITE_TRANSPORT_STARTED_ACTUAL.json',dict(epoch=time.time(),pid=os.getpid(),actual_alive_only_exclusive_210_72_249_transport_owner=True,no_learning_or_budget=True));f=load(E/'run_new_CURB35_native_full_finite_v3_once.py','v7final147_finite')
 for steps in (120,1500):
  m=load(E/'dispatch_curb_v7final147_parentguard_v8_unused_case_once.py','v7final147_dispatch'+str(steps));sys.argv=[str(E/'dispatch_curb_v7final147_parentguard_v8_unused_case_once.py'),'--steps',str(steps),'--execute-own-unused-case'];m.main();f.wait(steps);f.run('collect_curb113_own_case_actual_readonly.py',['--steps',str(steps)]);f.run('review_curb35_v7final147_actual_physical_CPU_v2.py',['--steps',str(steps)],f.CPU);print(json.dumps(dict(actual_CPU_admitted=steps,model='CURB35_V7_direction_final147',not_future_pass=True)),flush=True)
 put('CURB_V7FINAL147_PARENTGUARD_FROZEN_NATIVE_FULL_FINITE_COMPLETE_ACTUAL.json',dict(epoch=time.time(),own_native120_full1500_CPU_complete=True,no_PPO_or_budget=True))
if __name__=='__main__':
 try:main()
 except BaseException:put('CURB_V7FINAL147_PARENTGUARD_FROZEN_FINITE_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(epoch=time.time(),error=traceback.format_exc(),unknown_mutation_actual_readonly_no_replay=True));raise
