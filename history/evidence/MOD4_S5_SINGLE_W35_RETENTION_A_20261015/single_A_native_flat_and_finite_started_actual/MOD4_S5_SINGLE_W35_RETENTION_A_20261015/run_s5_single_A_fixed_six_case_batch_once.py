"""Exactly six new single-A cases; exclusive sequential transport while alive."""
from pathlib import Path
import argparse,hashlib,json,os,subprocess,sys,time,traceback
D=Path(__file__).resolve().parent;W=D.parent;R=D/'reports';OLD=W/'MOD4_S4_FIRST_GATE_RETENTION_PAIR_20261015'
import transport_s5_single_retention_A_actual as t
PY=sys.executable;CPU='C:/Users/lulu/miniconda3/envs/env_isaaclab/python.exe'
H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def put(n,v,unique=False):
 p=R/n
 if unique:assert not p.exists()
 q=p.with_name(p.name+'.partial');q.write_text(json.dumps(v,indent=2),encoding='utf8');os.replace(q,p)
def run(argv):
 p=subprocess.run(argv,cwd=D,capture_output=True,text=True,encoding='utf8',errors='replace')
 put('FINITE_SIX_COMMAND_'+str(time.time_ns())+'.json',dict(argv=argv,returncode=p.returncode,stdout=p.stdout,stderr=p.stderr),True);assert p.returncode==0,argv
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
def consume(kind,steps,native=None):
 case=f's5_single_W35_{kind}_{steps}_v1';put('S5_SINGLE_A_FIXED_SIX_CURRENT.json',dict(epoch=time.time(),pid=os.getpid(),phase='dispatching_own_unused_case',case=case))
 argv=[PY,'-X','utf8',str(D/'dispatch_s5_single_A_new_case_actual.py'),'--kind',kind,'--steps',str(steps),'--execute-root-new-single-case']
 if native:argv+=['--native-proof',native['data'],'--source-proof',native['source']]
 run(argv);put('S5_SINGLE_A_FIXED_SIX_CURRENT.json',dict(epoch=time.time(),pid=os.getpid(),phase='bounded_wait_own_case_exit_exclusive_transport',case=case));wait_closed(case)
 run([PY,'-X','utf8',str(D/'collect_s5_single_A_actual_boundary.py'),'--case',case,'--execute-root-readonly-collection'])
 receipt=json.loads(sorted(R.glob(case+'_CURRENT_ACTUAL_*.json'))[-1].read_bytes());assert receipt['outputs']['COMPLETE_ACTUAL.json'] and receipt['shared_OS_lock_free']
 boundary=R/(case+'_INDEPENDENT_BOUNDARY.json');attempt=Path(next(x['local_path'] for x in receipt['collected_files'] if x['relative']=='attempts/'+case+'/PARENT_EXIT_RECEIPT.json')).parent
 data=R/(case+'_ORIGINAL_PHYSICAL_CPU_REVIEW.json')
 run([CPU,'-X','utf8',str(D/'review_s5_single_A_original_physical_and_metrics_CPU.py'),'--attempt',str(attempt),'--boundary',str(boundary),'--output',str(data)])
 run([CPU,'-X','utf8',str(D/'review_s5_single_A_actual_source_history_CPU.py'),'--case',case]);source=R/(case+'_S5_SINGLE_CONTROL_CPU_ADMITTED.json')
 return dict(case=case,kind=kind,steps=steps,attempt=str(attempt),boundary=str(boundary),data=str(data),source=str(source))
def old_case(kind,mode):
 case=f's4_retention_{mode}_{kind}_1500_v1';p=OLD/'reports'/(case+'_INDEPENDENT_BOUNDARY.json');boundary=json.loads(p.read_bytes())
 assert boundary['actual_parent_absent'] and boundary['actual_child_absent'] and boundary['shared_OS_lock_free']
 c=json.loads(sorted((OLD/'reports').glob(case+'_CURRENT_ACTUAL_*.json'))[-1].read_bytes());assert c['outputs']['COMPLETE_ACTUAL.json'] and c['shared_OS_lock_free']
 attempt=Path(next(x['local_path'] for x in c['collected_files'] if x['relative']=='attempts/'+case+'/PARENT_EXIT_RECEIPT.json')).parent
 return dict(case=case,attempt=str(attempt),boundary=str(p),boundary_SHA=H(p))
def main():
 p=argparse.ArgumentParser();p.add_argument('--execute-root-six-new-A-cases',action='store_true');a=p.parse_args();assert a.execute_root_six_new_A_cases
 assert json.loads((R/'S5_SINGLE_A_UPLOAD_TARGET_CPU_ACTUAL.json').read_bytes())['actual_targetCPU'] and not (R/'S5_SINGLE_A_FIXED_SIX_STARTED.json').exists()
 ci=subprocess.run(['powershell','-NoProfile','-Command','$p=Get-CimInstance Win32_Process -Filter "ProcessId = '+str(os.getpid())+'";$p|Select-Object ProcessId,CreationDate,CommandLine|ConvertTo-Json -Compress'],capture_output=True,text=True,encoding='utf8',check=True)
 put('S5_SINGLE_A_FIXED_SIX_STARTED.json',dict(epoch=time.time(),pid=os.getpid(),actual_CIM=json.loads(ci.stdout),argv=sys.argv,scriptSHA=H(__file__),fixed_new_cases=[dict(kind=k,steps=s) for k in ('flat','spin','world') for s in (120,1500)],sole_sequential210_249_transport_owner_while_actual_alive=True,no_PPO_budget_oldcase_replay=True),True)
 completed=[];pairs=[]
 for kind in ('flat','spin','world'):
  native=consume(kind,120);completed.append(native);full=consume(kind,1500,native);completed.append(full)
  for mode in ('rule_eval','gate_eval'):
   old=old_case(kind,mode);out=R/(kind+'_SINGLE_A_VS_'+mode.upper()+'_COMPLETE_ORIGINAL_PAIR_CPU_REVIEW.json')
   run([CPU,'-X','utf8',str(D/'review_s5_single_A_original_physical_and_metrics_CPU.py'),'--attempt',full['attempt'],'--boundary',full['boundary'],'--baseline-attempt',old['attempt'],'--baseline-boundary',old['boundary'],'--output',str(out)])
   pairs.append(dict(kind=kind,baseline_mode=mode,path=str(out),sha256=H(out),old_actual_scope=old))
  put('S5_SINGLE_A_FIXED_SIX_CURRENT.json',dict(epoch=time.time(),pid=os.getpid(),phase='own_kind_complete_and_two_actual_old_pairs_CPU',completed=completed,pairs=pairs))
 run([CPU,'-X','utf8',str(D/'aggregate_s5_single_A_three_retention_matched_cells_CPU.py')])
 put('S5_SINGLE_A_FIXED_SIX_COMPLETE.json',dict(epoch=time.time(),pid=os.getpid(),completed=completed,pairs=pairs,all_six_new_A_cases_and_six_old_B_C_actual_pairs_CPU_complete=True,old_B_C_cases_not_GPU_replayed=True,no_additional_case_or_learning=True,handoff_requires_actual_local_CIM_absence=True),True)
if __name__=='__main__':
 try:main()
 except BaseException:
  put('S5_SINGLE_A_FIXED_SIX_ORIGINAL_ERROR.json',dict(epoch=time.time(),pid=os.getpid(),error=traceback.format_exc(),no_retry_replay_signal_or_GPU_restart=True),True);raise
