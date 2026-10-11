from pathlib import Path
import sys,json,time
D=Path(__file__).resolve().parent;W=D.parent;R=D/'reports'
sys.path.insert(0,str(D));from stage_entry_fullstate_and_cpu_once import NEW,save
sys.path.insert(0,str(W/'MOD4_E1_CURB20_ENTRY_REPAIR_20261011'));import repair_io as io
n,w=io.connect_both()
try:
 v=io.linux_json(n,r'''from pathlib import Path
import json,time,hashlib,fcntl
D=Path(ROOT);B=Path(BUDGET);j=lambda p:json.loads(p.read_bytes());a=j(D/'reports/E1_ATTENTION.json');assert not a['own_child_still_alive'] and j(B)['active_segment'] is None
paths=[D/'ENTRY_FRESH_SAME_SCOPE.log',D/'reports/FRESH_PROCESS_PROBE_ERROR.txt']
logs={str(p):p.read_text(errors='replace')[-16000:] for p in paths if p.exists()}
startup={p.name:j(p) for p in (D/'fresh_same_scope').glob('*STARTUP_VERIFIED.json') if p.stat().st_size<300000}
indices=[dict(path=str(p),bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest()) for p in (D/'fresh_same_scope').glob('*') if p.is_file()]
locks=[]
for p in (B.parent/'native_floor_supervisor.lock',Path('/home/egde/rl_candidates/MOD4_scut_spin_rate_20261002/autonomy_controller.lock')):
 with p.open('r') as f:fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);fcntl.flock(f,fcntl.LOCK_UN)
 locks.append(str(p))
print(json.dumps(dict(epoch=time.time(),attention=a,error_logs=logs,startup=startup,all_fresh_files_actual_SHA=indices,two_OS_locks_free=locks,canonical_SHA=hashlib.sha256(B.read_bytes()).hexdigest(),canonical=j(B),no_PPO_or_mutation=True)))
'''.replace('ROOT',repr(NEW)).replace('BUDGET',repr(io.B)))
 p=save('ENTRY_FRESH_ACTUAL_FAILURE_REVIEW_'+str(time.time_ns())+'.json',v)
 print(json.dumps(dict(report=str(p),error_logs=v['error_logs'],startup_marker_names=list(v['startup']),two_OS_locks_free=v['two_OS_locks_free'])))
finally:io.cleanup(n,w)
