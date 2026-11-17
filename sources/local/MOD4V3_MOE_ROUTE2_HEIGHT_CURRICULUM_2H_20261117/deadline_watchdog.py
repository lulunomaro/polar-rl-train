"""Only supervise the exact launched Route2 training process; never restart."""
from pathlib import Path
import json,time,os,signal,sys
root=Path(sys.argv[1]);pid=int(sys.argv[2]);job=root/'train_route2_2h'
def alive():
    f=Path('/proc')/str(pid)/'cmdline'
    return f.exists() and b'mod4v3_ppo_v1.route2_train' in f.read_bytes() and str(root).encode() in f.read_bytes()
while not (job/'TRAINING_CLOCK.json').exists():
    if not alive():raise SystemExit(0)
    time.sleep(1)
clock=json.loads((job/'TRAINING_CLOCK.json').read_text());deadline=clock['deadline_monotonic']
while alive():
    now=time.monotonic()
    if now>=deadline:
        (job/'DEADLINE_GUARD.json').write_text(json.dumps(dict(epoch=time.time(),pid=pid,hard_deadline_reached=True,action='SIGKILL own process group',FINAL_exists=(job/'FINAL.json').exists())))
        os.killpg(pid,signal.SIGKILL);break
    if now>=deadline-50 and not (job/'REQUEST_STOP').exists():
        (job/'REQUEST_STOP').write_text('Deadline reserve: save and close. No restart.\n')
    time.sleep(min(1,max(.01,deadline-now)))
(root/'WATCHDOG_EXIT.json').write_text(json.dumps(dict(epoch=time.time(),training_process_exited=not alive(),automatic_restart=False)))
