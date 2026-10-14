"""Finite root-owned original three-skill pair execution, no PPO or retry loop.

Each new case waits for actual parent exit, then independently audits the saved
data before the next lease. This is one bounded experiment batch, not a monitor.
"""
from pathlib import Path
import json,sys,subprocess,time,os,hashlib,traceback
D=Path(__file__).resolve().parent;W=D.parent;R=D/'reports'
PY=sys.executable;CPU='C:/Users/lulu/miniconda3/envs/env_isaaclab/python.exe'
sys.path.insert(0,str(W/'MOD4_3060_LINUX_RESUME_REFERENCE_20261014'));import transport_249_only as t
ROOT='D:/MOD4_async_eval/MOD4_3060_LEFT_REPAIR_RETENTION_20261014';t.ROOT=ROOT
def save(name,v):
 p=R/name;tmp=p.with_suffix('.partial');tmp.write_text(json.dumps(v,indent=2),encoding='utf8');os.replace(tmp,p)
def command(argv,env=None):
 p=subprocess.run(argv,capture_output=True,text=True,encoding='utf8',env=env)
 assert p.returncode==0,dict(argv=argv,exit=p.returncode,stdout=p.stdout[-2000:],stderr=p.stderr[-6000:])
 return json.loads(p.stdout.strip().splitlines()[-1])
def wait_own_parent(case,steps):
 # No frequent probing: wait locally for the expected bounded workload first.
 for _ in range(1 if steps==120 else 3):time.sleep(60)
 for _ in range(20):
  c=t.connect()
  try:
   code='from pathlib import Path\nimport json\np=Path('+repr(ROOT+'/attempts/'+case+'/PARENT_EXIT_RECEIPT.json')+')\nprint(json.dumps(dict(ended=p.exists(),parent_exit=json.loads(p.read_bytes()) if p.exists() else None)))'
   value=t.py(c,code)
  finally:t.close(c)
  if value['ended']:
   assert value['parent_exit']['exit_code']==0 and not value['parent_exit']['original_error_present'],value
   return value
  time.sleep(60)
 raise AssertionError('Own case has no parent exit yet; stop batch without signals/replay; inspect actual state')
def run_case(kind,steps,source,native,baseline=None):
 case=f'retention_{source}_{kind}_{steps}_v8';out=R/(case+'_FULL_CPU_REVIEW.json');assert not out.exists()
 save('RETENTION_V8_FIXED_BATCH_CURRENT.json',dict(epoch=time.time(),pid=os.getpid(),phase='new_case_admission',case=case,no_PPO=True))
 argv=[PY,str(D/'dispatch_new_retention_v8_CPU_schema_reviewed_case_actual.py'),'--kind',kind,'--steps',str(steps),'--source',source]
 if steps==1500:argv+=['--native-proof',str(native)]
 dispatch=command(argv);save('RETENTION_V8_FIXED_BATCH_CURRENT.json',dict(epoch=time.time(),pid=os.getpid(),phase='waiting_own_case_parent',case=case,dispatch=dispatch,no_PPO=True))
 wait_own_parent(case,steps)
 collected=command([PY,str(D/'collect_retention_V8_actual_boundary.py'),'--case',case]);assert collected['complete'] and collected['lock_free']
 argv=[CPU,str(D/'review_retention_full_actual_CPU_v8.py'),'--attempt',collected['local_attempt'],'--boundary',collected['boundary'],'--output',str(out)]
 if baseline:argv+=['--baseline-attempt',baseline['local_attempt'],'--baseline-boundary',baseline['boundary']]
 env=os.environ.copy();env['CUDA_VISIBLE_DEVICES']='';review=command(argv,env=env)
 save('RETENTION_V8_FIXED_BATCH_CURRENT.json',dict(epoch=time.time(),pid=os.getpid(),phase='own_case_complete_independent_CPU_review',case=case,review=review,collected=collected,no_PPO=True))
 print(json.dumps(dict(case_complete=case,review=str(out))),flush=True)
 return collected,out
def main():
 started=R/'RETENTION_V8_FIXED_BATCH_STARTED_ACTUAL.json';assert not started.exists()
 native=R/'retention_baseline1aa_flat_120_v8_FULL_CPU_REVIEW.json';value=json.loads(native.read_bytes())['result'];assert value['kind']=='flat' and value['steps']==120 and value['data']['complete_data_contract']
 save(started.name,dict(epoch=time.time(),pid=os.getpid(),argv=sys.argv,source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),fixed_new_cases_only=True,no_PPO=True,no_210_connection=True,no_retry_or_signals=True,first_native_proof=str(native)))
 complete=[]
 for kind in ('flat','spin','world'):
  if kind!='flat':_,native=run_case(kind,120,'baseline1aa',None)
  baseline,out=run_case(kind,1500,'baseline1aa',native);complete.append(str(out))
  candidate,out=run_case(kind,1500,'repair2b',native,baseline);complete.append(str(out))
 save('RETENTION_V8_FIXED_BATCH_COMPLETE_ACTUAL.json',dict(epoch=time.time(),all_three_actual_paired_full1500_complete=True,reports=complete,no_PPO=True,no_qualification_claim=True));print(json.dumps(dict(fixed_batch_complete=True,reports=complete)),flush=True)
if __name__=='__main__':
 try:main()
 except BaseException:
  save('RETENTION_V8_FIXED_BATCH_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(epoch=time.time(),error=traceback.format_exc(),no_replay_no_signal=True));raise
