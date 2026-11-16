"""One process guard for this exact experiment; never restart or extend training."""
from pathlib import Path
import time,json,sys,os,signal
job=Path(sys.argv[1]);pid=int(sys.argv[2]);experiment=job.parent.name
while True:
 if(job/'SAFE_CLOSED.json').exists():break
 proc=Path('/proc')/str(pid)/'cmdline'
 if not proc.exists():break
 command=proc.read_bytes().replace(bytes([0]),b' ').decode(errors='replace')
 if 'mod4v3_ppo_v1.history_train'not in command or experiment not in command:break
 f=job/'TRAINING_CLOCK.json'
 if f.exists():
  d=json.loads(f.read_text());remaining=d['monotonic_start']+d['requested_seconds']-time.monotonic()
  if remaining<=0:
   os.kill(pid,signal.SIGKILL);(job/'DEADLINE_WATCHDOG.json').write_text(json.dumps(dict(epoch=time.time(),action='killed_exact_training_process_at7200s',pid=pid,no_restart=True))+'\n');break
 time.sleep(.2)
