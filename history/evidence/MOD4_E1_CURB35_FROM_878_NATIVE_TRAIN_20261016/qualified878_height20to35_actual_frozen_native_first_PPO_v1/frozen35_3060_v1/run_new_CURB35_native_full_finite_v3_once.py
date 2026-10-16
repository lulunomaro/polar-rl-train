"""Finite own two-case completion; never repeat the existing native dispatch."""
from pathlib import Path
import importlib.util,json,subprocess,sys,time,traceback
E=Path(__file__).resolve().parent;R=E/'reports';ROOT='D:/MOD4_async_eval/'+E.parent.name
CPU='C:/Users/lulu/miniconda3/envs/env_isaaclab/python.exe'
def write(n,x):
 with (R/n).open('x',encoding='utf8') as f:json.dump(x,f,indent=2)
def run(name,args,exe=sys.executable):
 p=subprocess.run([exe,'-B','-X','utf8',str(E/name)]+args,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
 write(name.split('.')[0]+'_'+args[1]+'_FINITE_CHILD_EXIT.json',dict(epoch=time.time(),exit=p.returncode,output=p.stdout.decode('utf8',errors='replace')))
 assert p.returncode==0,p.stdout.decode('utf8',errors='replace')[-5000:]
def wait(steps):
 s=importlib.util.spec_from_file_location('own_collector_pure',E/'collect_curb113_own_case_actual_readonly.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
 c=None;case=f'curb35_source878_{steps}_v1';start=time.monotonic()
 try:
  c=m.t.connect()
  code="from pathlib import Path;import json;R=Path("+repr(ROOT)+");p=R/'attempts'/"+repr(case)+"/'PARENT_EXIT_RECEIPT.json';q=R/"+repr(case+'_LAUNCH_EXIT.json')+";print(json.dumps(dict(parent=json.loads(p.read_bytes()) if p.exists() else None,launcher=json.loads(q.read_bytes()) if q.exists() else None)))"
  while time.monotonic()-start<900:
   v=m.t.py(c,code,25)
   if v['parent'] and v['launcher']:
    assert v['parent']['exit_code']==v['launcher']['exit_code']==0,v
    return
   time.sleep(15)
  raise TimeoutError('Own case bounded900s; no signal or redispatch')
 finally:m.t.close(c)
def main():
 write('CURB35_SOURCE878_TWOCASE_FINITE_STARTED.json',dict(epoch=time.time(),pid=__import__('os').getpid(),creation_UTC=subprocess.check_output(['powershell','-NoProfile','-Command',"(Get-Process -Id %d).StartTime.ToUniversalTime().ToString('o')"%__import__('os').getpid()]).decode().strip(),only_existing_native_and_unused_full=True,no_learning=True))
 run('dispatch_curb113_frozen3060_unused_case_once.py',['--steps','120','--execute-own-unused-case'])
 for steps in (120,1500):
  if steps==1500:run('dispatch_curb113_frozen3060_unused_case_once.py',['--steps','1500','--execute-own-unused-case'])
  wait(steps)
  run('collect_curb113_own_case_actual_readonly.py',['--steps',str(steps)])
  run('review_curb35_source878_actual_physical_CPU_v2.py',['--steps',str(steps)],CPU)
  print(json.dumps(dict(actual_complete_CPU_admitted=steps)),flush=True)
 write('CURB35_SOURCE878_TWOCASE_FINITE_COMPLETE.json',dict(epoch=time.time(),native120_and_full1500_actual_CPU_complete=True,no_PPO=True))
if __name__=='__main__':
 try:main()
 except BaseException:
  write('CURB35_SOURCE878_TWOCASE_FINITE_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),unknown_outcome_readonly_no_replay=True));raise
