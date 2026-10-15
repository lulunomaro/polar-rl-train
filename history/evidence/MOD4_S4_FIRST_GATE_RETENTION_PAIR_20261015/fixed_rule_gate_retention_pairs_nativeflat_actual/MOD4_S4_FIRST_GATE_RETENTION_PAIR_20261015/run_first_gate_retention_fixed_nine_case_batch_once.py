"""One finite root-owned 3 native + 6 full cases. Never repeats a task or learns.

While actually alive this process owns sequential210/249 transport. Each native
and full saved dataset is independently admitted before the next dispatch.
"""
from pathlib import Path
import argparse,hashlib,json,os,subprocess,sys,time,traceback
D=Path(__file__).resolve().parent;R=D/'reports'
TRANSPORT=sys.executable
CPU='C:/Users/lulu/miniconda3/envs/env_isaaclab/python.exe'
H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
import transport_s4_retention_pair_actual as t

def put(name,value,unique=False):
    p=R/name
    if unique:assert not p.exists()
    tmp=p.with_name(p.name+'.partial');tmp.write_text(json.dumps(value,indent=2),encoding='utf8');os.replace(tmp,p)

def run(argv):
    proc=subprocess.run(argv,cwd=D,capture_output=True,text=True,encoding='utf8',errors='replace')
    stamp=str(time.time_ns())
    put('FINITE_NINE_COMMAND_'+stamp+'.json',dict(argv=argv,returncode=proc.returncode,stdout=proc.stdout,stderr=proc.stderr),True)
    assert proc.returncode==0,argv

def case_name(mode,kind,steps):return f's4_retention_{mode}_{kind}_{steps}_v1'

def wait_actual_closed(case):
    c=None
    try:
        c=t.connect()
        code=r'''
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
  locators=[read(R/(CASE+'_START_INTENT.json')),read(R/(CASE+'_PARENT_PID.json')),read(A/'DISPATCH_RECEIPT.json')]
  if not any(alive(v) for v in locators if v):
   with Path('D:/MOD4_async_eval/worker.lock').open('r+b') as f:
    f.seek(0);msvcrt.locking(f.fileno(),msvcrt.LK_NBLCK,1);f.seek(0);msvcrt.locking(f.fileno(),msvcrt.LK_UNLCK,1)
   print(json.dumps(dict(actual_parent_launcher_child_absent=True,shared_OS_lock_free=True,parent_exit=ex,complete_exists=(A/'output/COMPLETE_ACTUAL.json').exists(),original_error=read(A/'output/ORIGINAL_ERROR.json'),no_signal_retry_GPU_or_budget=True)));break
 time.sleep(15)
else:raise TimeoutError('Only this own finite case did not close within900s; do not retry task or signal')
'''
        value=t.py(c,'ROOT='+repr(t.ROOT)+'\nCASE='+repr(case)+'\n'+code,930)
        put(case+'_FINITE_WAIT_ACTUAL_CLOSED.json',value,True)
        assert value['parent_exit']['exit_code']==0 and value['complete_exists'] and value['original_error'] is None
    finally:t.close(c)

def consume(mode,kind,steps,native_data=None,native_router=None):
    case=case_name(mode,kind,steps)
    put('FIRST_GATE_RETENTION_FIXED_NINE_CURRENT.json',dict(epoch=time.time(),pid=os.getpid(),phase='dispatching_own_unused_case',case=case))
    argv=[TRANSPORT,'-X','utf8',str(D/'dispatch_first_gate_retention_new_case_actual.py'),'--execute-root-dispatch',
          '--kind',kind,'--steps',str(steps),'--source','pair_anchor','--mode',mode]
    if steps==1500:argv+=['--native-proof',str(native_data),'--routing-proof',str(native_router)]
    run(argv)
    put('FIRST_GATE_RETENTION_FIXED_NINE_CURRENT.json',dict(epoch=time.time(),pid=os.getpid(),phase='bounded_wait_own_case_exit_no_new_connections_by_root',case=case))
    wait_actual_closed(case)
    run([TRANSPORT,'-X','utf8',str(D/'collect_s4_retention_pair_actual_boundary.py'),'--case',case,'--execute-root-readonly-collection'])
    collection=json.loads(sorted(R.glob(case+'_CURRENT_ACTUAL_*.json'))[-1].read_bytes())
    assert collection['outputs']['COMPLETE_ACTUAL.json'] and collection['shared_OS_lock_free']
    boundary=R/(case+'_INDEPENDENT_BOUNDARY.json')
    attempt=Path(next(v['local_path'] for v in collection['collected_files'] if v['relative']=='attempts/'+case+'/PARENT_EXIT_RECEIPT.json')).parent
    data=R/(case+'_ORIGINAL_PHYSICAL_CPU_REVIEW.json')
    run([CPU,'-X','utf8',str(D/'review_s4_retention_original_physical_and_metrics_CPU.py'),'--attempt',str(attempt),'--boundary',str(boundary),'--output',str(data)])
    run([CPU,'-X','utf8',str(D/'review_s4_retention_pair_routing_CPU.py'),'--case',case])
    routing=R/(case+'_S4_ROUTING_CPU_ADMITTED.json')
    return dict(case=case,mode=mode,kind=kind,steps=steps,attempt=str(attempt),boundary=str(boundary),data=str(data),routing=str(routing))

def main():
    p=argparse.ArgumentParser();p.add_argument('--execute-root-fixed-nine-new-cases',action='store_true');a=p.parse_args();assert a.execute_root_fixed_nine_new_cases
    assert json.loads((R/'FIRST_GATE_RETENTION_PAIR_UPLOAD_TARGET_CPU_ACTUAL.json').read_bytes())['actual_targetCPU']
    started=R/'FIRST_GATE_RETENTION_FIXED_NINE_STARTED.json';assert not started.exists()
    identity=subprocess.run(['powershell','-NoProfile','-Command',
        '$p=Get-CimInstance Win32_Process -Filter "ProcessId = '+str(os.getpid())+'";$p|Select-Object ProcessId,CreationDate,CommandLine|ConvertTo-Json -Compress'],capture_output=True,text=True,encoding='utf8',check=True)
    put(started.name,dict(epoch=time.time(),pid=os.getpid(),CIM_actual=json.loads(identity.stdout),argv=sys.argv,
        script_SHA=H(__file__),plan=[dict(kind=k,native='gate_eval120',full=['rule_eval1500','gate_eval1500']) for k in ('flat','spin','world')],
        sole_sequential_210_249_transport_owner_while_actual_alive=True,no_PPO_no_budget_no_oldcase_replay=True),True)
    completed=[];pairs=[]
    for kind in ('flat','spin','world'):
        native=consume('gate_eval',kind,120);completed.append(native)
        rule=consume('rule_eval',kind,1500,Path(native['data']),Path(native['routing']));completed.append(rule)
        gate=consume('gate_eval',kind,1500,Path(native['data']),Path(native['routing']));completed.append(gate)
        pair=R/(kind+'_COMPLETE_RULE_VS_GATE_ORIGINAL_PHYSICAL_PAIR_CPU_REVIEW.json')
        run([CPU,'-X','utf8',str(D/'review_s4_retention_original_physical_and_metrics_CPU.py'),
            '--attempt',gate['attempt'],'--boundary',gate['boundary'],'--baseline-attempt',rule['attempt'],
            '--baseline-boundary',rule['boundary'],'--output',str(pair)])
        pairs.append(dict(kind=kind,path=str(pair),sha256=H(pair)))
        put('FIRST_GATE_RETENTION_FIXED_NINE_CURRENT.json',dict(epoch=time.time(),pid=os.getpid(),phase='own_kind_complete_actual',completed=completed,pairs=pairs))
    run([CPU,'-X','utf8',str(D/'aggregate_s4_retention_three_pairs_CPU_actual.py')])
    put('FIRST_GATE_RETENTION_FIXED_NINE_COMPLETE.json',dict(epoch=time.time(),pid=os.getpid(),completed=completed,pairs=pairs,
        all_nine_closed_and_CPU_admitted=True,no_additional_cases_or_learning=True,transport_owner_handoff_requires_actual_CIM_absence=True),True)

if __name__=='__main__':
    try:main()
    except BaseException:
        put('FIRST_GATE_RETENTION_FIXED_NINE_ORIGINAL_ERROR.json',dict(epoch=time.time(),pid=os.getpid(),error=traceback.format_exc(),no_retry_replay_signal_or_GPU_restart=True),True)
        raise
