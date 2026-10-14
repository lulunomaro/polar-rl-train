"""Explicit root finite three NEW candidate cases. No native/old case replay."""
from pathlib import Path
import argparse,json,sys,subprocess,time,os,hashlib,traceback
D=Path(__file__).resolve().parent;W=D.parent;R=D/'reports';ROOT='D:/MOD4_async_eval/MOD4_3060_BODYFRAME_PHASE_FINAL_RETENTION_20261015'
CPU='C:/Users/lulu/miniconda3/envs/env_isaaclab/python.exe'
def save(name,value):
 p=R/name;tmp=p.with_suffix('.partial');tmp.write_text(json.dumps(value,indent=2),encoding='utf8');os.replace(tmp,p)
def command(argv,env=None):
 p=subprocess.run(argv,capture_output=True,text=True,encoding='utf8',env=env)
 assert p.returncode==0,dict(argv=argv,exit_code=p.returncode,stdout=p.stdout[-2500:],stderr=p.stderr[-6000:])
 return json.loads(p.stdout.strip().splitlines()[-1])
def main():
 p=argparse.ArgumentParser();p.add_argument('--execute-root-fixed-three-cases',action='store_true');a=p.parse_args();assert a.execute_root_fixed_three_cases,'Explicit root execution flag required'
 assert json.loads((R/'BODYFRAME_PHASE_FINAL_RETENTION_TARGET_SOURCE_UPLOAD_CPU_ACTUAL.json').read_bytes())['source_whole20k_195_107_99_CPU_verified']
 started=R/'BODYFRAME_PHASE_FINAL_RETENTION_FIXED_THREE_STARTED_ACTUAL.json';assert not started.exists()
 sys.path.insert(0,str(D));import transport_249_own_phase_final_retention as t;t.ROOT=ROOT
 save(started.name,dict(epoch=time.time(),pid=os.getpid(),argv=sys.argv,script_SHA=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),no_PPO=True,no_retry_or_signal=True,newcases_only=3,three_native120_reused_no_new_native=True,no_210_connection=True))
 results=[]
 for kind in ('flat','spin','world'):
  inputs=json.loads((R/(kind+'_BASELINE_AND_REUSED_NATIVE_INPUTS_CPU_PREPARED.json')).read_bytes());case=f'retention_bodyframe_phase_final_cf_{kind}_1500_v8';out=R/(case+'_FULL_CPU_REVIEW.json');assert not out.exists()
  save('BODYFRAME_PHASE_FINAL_RETENTION_FIXED_THREE_CURRENT.json',dict(epoch=time.time(),pid=os.getpid(),phase='newcase_admission',case=case))
  dispatch=command([sys.executable,str(D/'dispatch_new_bodyframe_retention_case_actual.py'),'--kind',kind,'--steps','1500','--source','bodyframe_phase_final_cf','--native-proof',inputs['native_proof'],'--execute-root-dispatch'])
  save('BODYFRAME_PHASE_FINAL_RETENTION_FIXED_THREE_CURRENT.json',dict(epoch=time.time(),pid=os.getpid(),phase='waiting_own_parent_exit',case=case,dispatch=dispatch))
  for _ in range(3):time.sleep(60)
  ended=None
  for _ in range(20):
   c=t.connect()
   try:
    code='from pathlib import Path\nimport json\np=Path('+repr(ROOT+'/attempts/'+case+'/PARENT_EXIT_RECEIPT.json')+')\nprint(json.dumps(dict(ended=p.exists(),parent_exit=json.loads(p.read_bytes()) if p.exists() else None)))'
    ended=t.py(c,code)
   finally:t.close(c)
   if ended['ended']:
    assert ended['parent_exit']['exit_code']==0 and not ended['parent_exit']['original_error_present'],ended;break
   time.sleep(60)
  assert ended and ended['ended'],'No parent exit: stop batch, inspect actual identity; do not replay or signal'
  collected=command([sys.executable,str(D/'collect_bodyframe_retention_actual_boundary.py'),'--case',case,'--execute-root-readonly-collection']);assert collected['complete'] and collected['lock_free']
  env=os.environ.copy();env['CUDA_VISIBLE_DEVICES']=''
  review=command([CPU,str(D/'review_bodyframe_retention_full_actual_CPU.py'),'--attempt',collected['local_attempt'],'--boundary',collected['boundary'],'--output',str(out),'--baseline-attempt',inputs['baseline_attempt'],'--baseline-boundary',inputs['baseline_boundary']],env)
  result=dict(case=case,review=str(out),collected=collected);results.append(result);save('BODYFRAME_PHASE_FINAL_RETENTION_FIXED_THREE_CURRENT.json',dict(epoch=time.time(),pid=os.getpid(),phase='complete_own_case_CPU_pair_review',**result));print(json.dumps(dict(case_complete=case,review=str(out))),flush=True)
 save('BODYFRAME_PHASE_FINAL_RETENTION_FIXED_THREE_COMPLETE_ACTUAL.json',dict(epoch=time.time(),all_three_new_candidates_complete=True,results=results,no_PPO_no_budgetwrite=True,no_qualification_claimed=True));print(json.dumps(dict(complete=True,reports=[r['review'] for r in results])),flush=True)
if __name__=='__main__':
 try:main()
 except BaseException:
  save('BODYFRAME_PHASE_FINAL_RETENTION_FIXED_THREE_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(epoch=time.time(),error=traceback.format_exc(),unknown_outcome_requires_readonly_recovery=True,no_retry_no_signal=True));raise
