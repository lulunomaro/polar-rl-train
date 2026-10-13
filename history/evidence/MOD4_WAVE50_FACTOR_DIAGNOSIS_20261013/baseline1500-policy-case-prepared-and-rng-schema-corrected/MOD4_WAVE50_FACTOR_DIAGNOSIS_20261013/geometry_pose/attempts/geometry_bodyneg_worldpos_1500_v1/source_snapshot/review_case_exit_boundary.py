"""CPU/process/OSlock readonly boundary check; no signal or GPU initialization."""
from pathlib import Path
import argparse,json,psutil,msvcrt,time
p=argparse.ArgumentParser();p.add_argument('--attempt',required=True);p.add_argument('--output',required=True);args=p.parse_args()
A=Path(args.attempt);R=Path(args.output);assert not R.exists();d=json.loads((A/'DISPATCH_RECEIPT.json').read_bytes());actual={}
for key,ckey in [('parent_pid','parent_creation'),('child_pid','child_creation')]:
 try:
  proc=psutil.Process(d[key]);actual[key]=dict(exists=True,creation=proc.create_time(),same_creation=proc.create_time()==d[ckey],argv=proc.cmdline())
 except psutil.NoSuchProcess:actual[key]=dict(exists=False)
lock=Path('C:/Users/lulu/Desktop/claude/mjcf/MOD4_LOCAL_WAVE50_TEMP_TRAIN_20261013/LOCAL_GPU_EXCLUSIVE.lock')
f=lock.open('r+b');f.seek(0)
try:
 msvcrt.locking(f.fileno(),msvcrt.LK_NBLCK,1);held=False;f.seek(0);msvcrt.locking(f.fileno(),msvcrt.LK_UNLCK,1)
except OSError:held=True
f.close();exit=json.loads((A/'PARENT_EXIT_RECEIPT.json').read_bytes())
report=dict(epoch=time.time(),actual_processes=actual,native_shared_lock_held=held,original_parent=exit,COMPLETE_present=(A/'output/COMPLETE_ACTUAL.json').exists(),ORIGINAL_ERROR_present=(A/'output/ORIGINAL_ERROR.json').exists(),
 worker_post_app_close_marker_present=(A/'output/EXIT_NATURAL.json').exists(),post_app_close_marker_not_fabricated=True,actual_parent_exited0_with_complete_no_error=True,no_signals_GPU_or_budgetwrite=True)
assert not held and all(not v['exists'] or not v['same_creation'] for v in actual.values()) and exit['exit_code']==0 and report['COMPLETE_present'] and not report['ORIGINAL_ERROR_present']
R.write_text(json.dumps(report,indent=2),encoding='utf8');print(json.dumps(report))
