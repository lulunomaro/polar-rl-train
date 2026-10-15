"""Fixed 15 new development-seed cases; frozen only, exclusive finite transport."""
from pathlib import Path
import argparse,hashlib,json,os,subprocess,sys,time,traceback
D=Path(__file__).resolve().parent;R=D/'reports';PY=sys.executable;CPU='C:/Users/lulu/miniconda3/envs/env_isaaclab/python.exe'
import transport_devseed03_ABC_actual as t
H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def put(n,v,unique=False):
 p=R/n
 if unique:assert not p.exists()
 q=p.with_name(p.name+'.partial');q.write_text(json.dumps(v,indent=2),encoding='utf8');os.replace(q,p)
def run(argv):
 p=subprocess.run(argv,cwd=D,capture_output=True,text=True,encoding='utf8',errors='replace');put('FINITE15_COMMAND_'+str(time.time_ns())+'.json',dict(argv=argv,returncode=p.returncode,stdout=p.stdout,stderr=p.stderr),True);assert p.returncode==0,argv
def wait_closed(case):
 c=None
 try:
  c=t.connect();code=r'''
from pathlib import Path
import json,time,psutil,msvcrt
R=Path(ROOT);A=R/'attempts'/CASE;end=time.time()+900
def read(p):return json.loads(p.read_bytes()) if p.exists() else None
def alive(row):
 for pk,ck in (('pid','creation'),('parent_pid','parent_creation'),('child_pid','child_creation')):
  if pk not in row:continue
  try:
   p=psutil.Process(row[pk])
   if p.create_time()==row[ck]:return True
  except psutil.NoSuchProcess:pass
 return False
while time.time()<end:
 ex=read(A/'PARENT_EXIT_RECEIPT.json');launch=read(R/(CASE+'_LAUNCH_EXIT.json'))
 if ex is not None and launch is not None:
  ids=[read(R/(CASE+'_START_INTENT.json')),read(R/(CASE+'_PARENT_PID.json')),read(A/'DISPATCH_RECEIPT.json')]
  if not any(alive(v) for v in ids if v):
   with Path('D:/MOD4_async_eval/worker.lock').open('r+b') as f:
    f.seek(0);msvcrt.locking(f.fileno(),msvcrt.LK_NBLCK,1);f.seek(0);msvcrt.locking(f.fileno(),msvcrt.LK_UNLCK,1)
   print(json.dumps(dict(actual_parent_launcher_child_absent=True,shared_OS_lock_free=True,parent_exit=ex,complete_exists=(A/'output/COMPLETE_ACTUAL.json').exists(),original_error=read(A/'output/ORIGINAL_ERROR.json'),no_signal_retry_GPU_or_budget=True)));break
 time.sleep(15)
else:raise TimeoutError('Own case failed to close within900s; do not replay or signal')
'''
  value=t.py(c,'ROOT='+repr(t.ROOT)+'\nCASE='+repr(case)+'\n'+code,930);put(case+'_FINITE_WAIT_ACTUAL_CLOSED.json',value,True)
  assert value['parent_exit']['exit_code']==0 and value['complete_exists'] and value['original_error'] is None
 finally:t.close(c)
def consume(mode,kind,steps,native=None):
 case=f's5_dev03_{mode}_{kind}_{steps}_v1';put('DEVSEED03_ABC_FIXED15_CURRENT.json',dict(epoch=time.time(),pid=os.getpid(),phase='dispatch_own_unused',case=case))
 argv=[PY,'-X','utf8',str(D/'dispatch_devseed03_ABC_new_case_actual.py'),'--execute-root-dispatch','--kind',kind,'--steps',str(steps),'--source','pair_anchor','--mode',mode]
 if steps==1500:argv+=['--native-proof',native['data'],'--routing-proof',native['routing']]
 run(argv);put('DEVSEED03_ABC_FIXED15_CURRENT.json',dict(epoch=time.time(),pid=os.getpid(),phase='bounded_wait_own_scope_exclusive_transport',case=case));wait_closed(case)
 run([PY,'-X','utf8',str(D/'collect_devseed03_ABC_actual_boundary.py'),'--case',case,'--execute-root-readonly-collection'])
 c=json.loads(sorted(R.glob(case+'_CURRENT_ACTUAL_*.json'))[-1].read_bytes());assert c['outputs']['COMPLETE_ACTUAL.json'] and c['shared_OS_lock_free']
 attempt=Path(next(x['local_path'] for x in c['collected_files'] if x['relative']=='attempts/'+case+'/PARENT_EXIT_RECEIPT.json')).parent;boundary=R/(case+'_INDEPENDENT_BOUNDARY.json');data=R/(case+'_ORIGINAL_PHYSICAL_CPU_REVIEW.json')
 run([CPU,'-X','utf8',str(D/'review_devseed03_original_physical_and_metrics_CPU.py'),'--attempt',str(attempt),'--boundary',str(boundary),'--output',str(data)])
 reader='review_devseed03_single_source_history_CPU.py' if mode=='single_eval' else 'review_devseed03_pair_routing_CPU.py';run([CPU,'-X','utf8',str(D/reader),'--case',case]);routing=R/(case+('_S5_SINGLE_CONTROL_CPU_ADMITTED.json' if mode=='single_eval' else '_S4_ROUTING_CPU_ADMITTED.json'))
 return dict(case=case,mode=mode,kind=kind,steps=steps,attempt=str(attempt),boundary=str(boundary),data=str(data),routing=str(routing))
def main():
 p=argparse.ArgumentParser();p.add_argument('--execute-root-fixed15-new-devseed-cases',action='store_true');a=p.parse_args();assert a.execute_root_fixed15_new_devseed_cases
 assert json.loads((R/'DEVSEED03_ABC_UPLOAD_TARGET_CPU_ACTUAL.json').read_bytes())['actual_targetCPU'] and not (R/'DEVSEED03_ABC_FIXED15_STARTED.json').exists()
 ci=subprocess.run(['powershell','-NoProfile','-Command','$p=Get-CimInstance Win32_Process -Filter "ProcessId = '+str(os.getpid())+'";$p|Select-Object ProcessId,CreationDate,CommandLine|ConvertTo-Json -Compress'],capture_output=True,text=True,encoding='utf8',check=True)
 put('DEVSEED03_ABC_FIXED15_STARTED.json',dict(epoch=time.time(),pid=os.getpid(),actual_CIM=json.loads(ci.stdout),argv=sys.argv,scriptSHA=H(__file__),seed=20261003,profile='white_v3',plan='perkind single native120+full1500, gate native120, rulefull1500+gatefull1500, actual3way initialpairs; 15newcases total',sole_sequential210_249_transport_owner_while_actual_alive=True,no_PPO_budget_or_oldcase_replay=True),True)
 completed=[];pairs=[]
 for kind in ('flat','spin','world'):
  an=consume('single_eval',kind,120);completed.append(an);single=consume('single_eval',kind,1500,an);completed.append(single)
  cn=consume('gate_eval',kind,120);completed.append(cn);rule=consume('rule_eval',kind,1500,cn);completed.append(rule);gate=consume('gate_eval',kind,1500,cn);completed.append(gate)
  for name,cand,base in [('A_VS_B',single,rule),('C_VS_B',gate,rule),('A_VS_C',single,gate)]:
   out=R/(kind+'_'+name+'_COMPLETE_ORIGINAL_PAIR_CPU_REVIEW.json');run([CPU,'-X','utf8',str(D/'review_devseed03_original_physical_and_metrics_CPU.py'),'--attempt',cand['attempt'],'--boundary',cand['boundary'],'--baseline-attempt',base['attempt'],'--baseline-boundary',base['boundary'],'--output',str(out)]);pairs.append(dict(kind=kind,pair=name,path=str(out),sha256=H(out)))
  put('DEVSEED03_ABC_FIXED15_CURRENT.json',dict(epoch=time.time(),pid=os.getpid(),phase='kind_complete_3way_initialpairs_CPU',completed=completed,pairs=pairs))
 put('DEVSEED03_ABC_FIXED15_COMPLETE.json',dict(epoch=time.time(),pid=os.getpid(),completed=completed,pairs=pairs,all15_closed_and_CPU_admitted=True,actual_three_initial_pairs_per_kind=True,no_extra_case_learning_or_budget=True,handoff_requires_actual_local_CIM_absence=True),True)
if __name__=='__main__':
 try:main()
 except BaseException:put('DEVSEED03_ABC_FIXED15_ORIGINAL_ERROR.json',dict(epoch=time.time(),pid=os.getpid(),error=traceback.format_exc(),no_retry_replay_signal_or_GPU_restart=True),True);raise
