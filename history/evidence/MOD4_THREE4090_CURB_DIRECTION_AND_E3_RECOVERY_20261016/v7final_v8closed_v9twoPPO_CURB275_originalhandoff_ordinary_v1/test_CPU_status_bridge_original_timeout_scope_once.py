from pathlib import Path
import sys,time,json
D=Path(__file__).resolve().parent;sys.path.insert(0,str(D));from native_CPU_status_bridge_v1 import run_CPU_with_status
def main():
 cfg=dict(key='recovery',manifest_SHA='fixture-only');frames=[];receipts=[]
 def send(c,row):frames.append(row);return dict(stop=False)
 def put(p,v):receipts.append(v)
 def audit(c):time.sleep(.16);return dict(actual_fixture_CPU_passed=True)
 start=time.monotonic();r=run_CPU_with_status(cfg,audit,send,put,D,period=.005,max_ack_gap=.05);assert r['actual_fixture_CPU_passed'] and time.monotonic()-start>.05 and len(frames)>=3 and all(x['phase']=='native_CPU_review_running' and x['native_CPU'] is None and x['not_CPU_admitted_or_PPO'] for x in frames);assert receipts[-1]['actual_ack_age']<.05 and receipts[-1]['CPU_function_succeeded'];bad=0
 for sender in (lambda c,row:dict(stop=True),lambda c,row:(_ for _ in ()).throw(ConnectionError('fixture transport failure'))):
  try:run_CPU_with_status(cfg,audit,sender,put,D,period=.005,max_ack_gap=.05)
  except AssertionError:bad+=1
  else:raise AssertionError('Failed source stop/transport was not rejected')
 assert bad==2 and all(not x['CPU_function_succeeded'] for x in receipts[1:]);p=D/'reports/NATIVE_CPU_BLOCKED_WAIT_ACTUAL_STATUS_BRIDGE_CPU_NEGATIVES.json';assert not p.exists();p.write_text(json.dumps(dict(epoch=time.time(),passed_CPU_fixture_only=True,legacy_blocked_audit_exceeds_simulated_timeout=True,actual_ack_status_preserves_original_timeout=True,status_frames=len(frames),source_stop_and_real_transport_failure_rejected=bad,never_reports_CPU_admitted_before_actual_audit_return=True,no_target_native_GPU_or_PPO_pass_claimed=True,no_extra_watcher_process_or_SSH=True),indent=2),encoding='utf8');print(json.dumps(dict(passed_CPU_fixture_only=True,status_frames=len(frames),negatives=bad)))
if __name__=='__main__':main()
