"""Root gives this finite coordinator sole 249 transport ownership until its actual exit."""
from pathlib import Path
import json,os,subprocess,sys,time,hashlib,psutil
D=Path(__file__).resolve().parent;R=D/'reports';SCRIPT=D/'run_bodyframe_retention_fixed_three_candidate_batch_once.py'
def main():
 target=json.loads((R/'BODYFRAME_FIRST_RETENTION_TARGET_SOURCE_UPLOAD_CPU_ACTUAL.json').read_bytes())
 assert target['source_whole20k_195_107_99_CPU_verified'] and target['source_owned_body_state_independently_validated'] and target['no_GPU_no_PPO_no_budgetwrite']
 assert target['source_SHA']=='f5166509d297814e3c3fe4f457ae064d9b02a8bd62702914759dc430f20d2139'
 receipt=R/'BODYFRAME_FIRST_RETENTION_FINITE_BATCH_ROOT_DISPATCH_ACTUAL.json';assert not receipt.exists() and not (R/'BODYFRAME_FIRST_RETENTION_FIXED_THREE_STARTED_ACTUAL.json').exists()
 current=[]
 for p in psutil.process_iter(['pid','name','cmdline','create_time']):
  if p.pid==os.getpid() or 'python' not in (p.info['name'] or '').lower():continue
  argv=p.info['cmdline'] or [];joined=' '.join(argv)
  if 'run_' in joined and 'retention' in joined and ('batch' in joined or 'fixed_three' in joined):current.append(p.info)
 assert not current,('Another finite coordinator already owns transport',current)
 compile(SCRIPT.read_text(encoding='utf8'),str(SCRIPT),'exec')
 argv=[sys.executable,'-X','utf8',str(SCRIPT),'--execute-root-fixed-three-cases']
 with (D/'finite_fixed_three.stdout.log').open('xb') as out,(D/'finite_fixed_three.stderr.log').open('xb') as err:
  child=subprocess.Popen(argv,cwd=D,stdout=out,stderr=err,creationflags=subprocess.CREATE_NO_WINDOW)
 value=dict(epoch=time.time(),pid=child.pid,creation=psutil.Process(child.pid).create_time(),argv=argv,script_SHA=hashlib.sha256(SCRIPT.read_bytes()).hexdigest(),sole_transport_owner_210_and249_until_actual_exit=True,coordinator_uses249_only=True,root_and_agents_must_not_connect_210_or249_while_actual_owner_alive=True,fixed_three_new_candidate_case_ids=[f'retention_bodyframe_first_f516_{k}_1500_v8' for k in ('flat','spin','world')],reused_native120_no_GPU_replay=True,new_source_SHA=target['source_SHA'],baseline_e3_complete_same_initial_pair_required=True,no_PPO_no_budgetwrite=True,no_retry_no_signal_no_qualification=True)
 with receipt.open('x',encoding='utf8') as out:json.dump(value,out,indent=2)
 print(json.dumps(value))
if __name__=='__main__':main()
