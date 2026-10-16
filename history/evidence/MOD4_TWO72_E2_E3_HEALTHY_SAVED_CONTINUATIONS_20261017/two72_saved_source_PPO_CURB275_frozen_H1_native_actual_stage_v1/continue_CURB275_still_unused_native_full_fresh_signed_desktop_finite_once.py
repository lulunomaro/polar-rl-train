from pathlib import Path
import sys,json,time,os,importlib.util,traceback
N=Path(__file__).resolve().parent;E=N/'curb275_final87_frozen3060_v1';R=N/'reports';sys.path.insert(0,str(E))
def load(p,name):
 s=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def put(n,v):
 with (R/n).open('x',encoding='utf8') as f:json.dump(v,f,indent=2)
def main():
 assert json.loads((R/'FRESH_SIGNED_EXACT_DESKTOP_GUARD_7ROLES_28NEGATIVES_CPU_ACTUAL.json').read_bytes())['passed_CPU_identity_negative_fixture_only'];assert not (E/'reports/curb275_final87_120_v2_PARENTFIX_DISPATCH_INTENT.json').exists();put('CURB275_FRESH_SIGNED_DESKTOP_UNUSED_NATIVE_FULL_FINITE_STARTED.json',dict(epoch=time.time(),pid=os.getpid(),actual_alive_only_exclusive_210_72_249_transport_owner=True,no_old_case_replay_no_process_UI_or_budget_mutation=True));f=load(E/'run_new_CURB35_native_full_finite_v3_once.py','fresh_curb275_finite')
 for steps in (120,1500):
  p=E/'dispatch_CURB275_final87_fresh_signed_desktop_v9_unused_once.py';m=load(p,'fresh_curb275_unused'+str(steps));sys.argv=[str(p),'--steps',str(steps),'--execute-own-unused-case'];m.main();f.wait(steps);f.run('collect_curb113_own_case_actual_readonly.py',['--steps',str(steps)]);f.run('review_curb275_final87_actual_physical_CPU_v2.py',['--steps',str(steps)],f.CPU);print(json.dumps(dict(actual_closed_CPU_admitted_steps=steps)),flush=True)
 put('CURB275_FRESH_SIGNED_DESKTOP_UNUSED_NATIVE_FULL_FINITE_ACTUAL_COMPLETE.json',dict(epoch=time.time(),native120_and_full1500_all_CPU_actually_complete=True,no_PPO_or_budget=True))
if __name__=='__main__':
 try:main()
 except BaseException:put('CURB275_FRESH_SIGNED_DESKTOP_FINITE_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(epoch=time.time(),error=traceback.format_exc(),unknown_outcome_actual_readonly_before_unused_continuation=True));raise
