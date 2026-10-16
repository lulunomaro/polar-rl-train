from pathlib import Path
import sys,json,time,os,importlib.util,traceback
N=Path(__file__).resolve().parent;R=N/'reports';E=N/'curb275_final87_frozen3060_v1';sys.path.insert(0,str(E))
def load(p,name):
 s=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def put(n,v):
 with (R/n).open('x',encoding='utf8') as f:json.dump(v,f,indent=2)
def main():
 assert json.loads((R/'CURB275_FINAL87_FROZEN3060_NEW_SOURCE_GEOMETRY_CPU_PREPARED_ACTUAL.json').read_bytes())['passed_CPU_only'];put('CURB275_3060_NATIVE_FULL_FINITE_TRANSPORT_STARTED_ACTUAL.json',dict(epoch=time.time(),pid=os.getpid(),actual_alive_only_exclusive_210_72_249_transport=True,no_learning_or_accounting=True));path=E/'dispatch_curb275_final87_parentguard_v8_unused_case_once.py';s=path.read_text('utf8');s=s.replace("f'MOD4_CURB275_FINAL87_3060_{steps}_v2_20261016'","f'MOD4_CURB275_FINAL87_3060_{steps}_v2_20261017'");path.write_text(s,encoding='utf8');f=load(E/'run_new_CURB35_native_full_finite_v3_once.py','new_curb275_own_wait')
 for steps in (120,1500):
  m=load(path,'new_curb275_dispatch'+str(steps));sys.argv=[str(path),'--steps',str(steps),'--execute-own-unused-case'];m.main();f.wait(steps);f.run('collect_curb113_own_case_actual_readonly.py',['--steps',str(steps)]);f.run('review_curb275_final87_actual_physical_CPU_v2.py',['--steps',str(steps)],f.CPU);print(json.dumps(dict(actual_CPU_admitted=steps,not_future_full_pass=True)),flush=True)
 put('CURB275_3060_NATIVE_FULL_FINITE_ALL_CPU_ACTUAL_COMPLETE.json',dict(epoch=time.time(),own_native120_and_full1500_actual_CPU_admitted=True,no_PPO_or_budget=True))
if __name__=='__main__':
 try:main()
 except BaseException:put('CURB275_3060_FINITE_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(epoch=time.time(),error=traceback.format_exc(),actual_readonly_before_any_retry_no_old_once_replay=True));raise
