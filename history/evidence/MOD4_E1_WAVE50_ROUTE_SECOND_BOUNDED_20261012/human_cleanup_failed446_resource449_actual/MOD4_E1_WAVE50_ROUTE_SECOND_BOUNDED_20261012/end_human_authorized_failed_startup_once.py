from route_second_io import *
AUTH='允许结束这个失败进程并继续修复'

def main():
    assert not (R/'FAILED_STARTUP_HUMAN_END_ACTUAL.json').exists()
    save('FAILED_STARTUP_HUMAN_END_AUTHORIZATION.json',dict(epoch=time.time(),human_text=AUTH,scope=dict(pid=3340979,start_ticks=94499270,SIGTERM_then_SIGKILL_if_needed=True),no_parent_guardian_other_process_signal=True,original_parent_accounts_own_failed_startup=True))
    n,w=io.connect_both()
    try:
        v=run(n,r'''import os,json,time,signal,hashlib
from pathlib import Path
ROOT=Path('/home/egde/rl_candidates/MOD4_S3_E1_WAVE50_ROUTE_SECOND_BOUNDED_20261012')
out=ROOT/'reports/HUMAN_AUTHORIZED_FAILED_STARTUP_END_ACTUAL.json'
assert not out.exists()
pid=3340979;expected=94499270;p=Path('/proc')/str(pid)
def identity():
 if not p.exists():return None
 s=(p/'stat').read_text();fields=s[s.rfind(')')+2:].split()
 return dict(pid=pid,state=fields[0],ppid=int(fields[1]),start_ticks=int(fields[19]),argv=(p/'cmdline').read_bytes().split(bytes([0])))
def sha(q):return hashlib.sha256(q.read_bytes()).hexdigest()
initial=identity();assert initial and initial['start_ticks']==expected and initial['ppid']==3340858
assert b'/home/egde/rl_candidates/MOD4_S3_E1_WAVE50_ROUTE_SECOND_BOUNDED_20261012/isaac/mod4/train_wave50_route_same_scope_resume_ppo.py' in initial['argv']
error=ROOT/'e1_WAVE50_route_second_bounded_observation_1791789813907214471.error.txt';raw=error.read_bytes();assert b'wheel_friction_error' in raw
log=ROOT/'e1_WAVE50_route_second_bounded_observation_1791789813907214471.log';lb=log.read_bytes();assert b'PxgPinnedMemoryAllocate failed' in lb and b'Scene state is corrupted' in lb
runs=list((ROOT/'learning_logs').glob('*e1_WAVE50_route_second_bounded*'));assert len(runs)==1
assert not list(runs[0].rglob('model_*.pt')) and not (runs[0]/'run_manifest.json').exists()
source=Path('/home/egde/rl_candidates/MOD4_S3_E1_WAVE50_ROUTE_FIXTURE_REVIEWED_20261012/learning_logs/2026-10-12_12-52-16_e1_WAVE50_route_lifecycle_observation_1791780538491241968/model_32264.pt')
assert sha(source)=='68401cae6402c5aa38797dabdbb7043f8036ed6fcbacd9c34fda0bdd95a813c5'
receipt=dict(epoch=time.time(),human_text='允许结束这个失败进程并继续修复',pid=pid,start_ticks=expected,error_SHA=sha(error),log_SHA_before_signal=sha(log),source_SHA=sha(source),own_checkpoint_present=False,manifest_present=False,no_control_or_PPO_startup_completed=True,signals=[],only_exact_failed_child=True,no_budget_write=True)
def write():
 with out.open('w') as f:json.dump(receipt,f,indent=2);f.flush();os.fsync(f.fileno())
write()
for sig in (signal.SIGTERM,signal.SIGKILL):
 now=identity()
 if not now or now['state']=='Z':break
 assert now['start_ticks']==expected and now['ppid']==3340858
 receipt['signals'].append(dict(epoch=time.time(),signal=sig.name,intent_before_send=True));write()
 os.kill(pid,sig)
 receipt['signals'][-1]['sent']=True;write()
 end=time.monotonic()+12
 while time.monotonic()<end:
  now=identity()
  if not now or now['state']=='Z':break
  time.sleep(.5)
receipt['final_identity']=identity();receipt['source_SHA_after']=sha(source);assert receipt['source_SHA_after']==receipt['source_SHA']
assert not receipt['final_identity'] or receipt['final_identity']['state']=='Z'
receipt['failed_child_ended']=True;receipt['original_parent_accounting_pending']=True;write()
print(json.dumps(receipt))
''',timeout=50)
        save('FAILED_STARTUP_HUMAN_END_ACTUAL.json',v)
        print(json.dumps(v))
    finally:io.cleanup(n,w)

if __name__=='__main__':
    try:main()
    except BaseException:save('HUMAN_END_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),unknown_outcome_inspect_remote_receipt_before_any_retry=True,no_blind_signal_replay=True));raise
