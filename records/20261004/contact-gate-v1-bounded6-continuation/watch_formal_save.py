"""One finite SSH stream waiting for this explicitly launched trainer's own save."""
import json,shlex,sys
from pathlib import Path
D=Path(__file__).resolve().parent
sys.path.insert(0,str(D.parent/'MOD4_AUTONOMY_SLEEP_20261003'))
from remote_io import connect
code=r'''import json,sys,time
from pathlib import Path
P=Path('/home/egde/rl_candidates/MOD4_scut_spin_rate_20261002');C=Path('/home/egde/rl_candidates/MOD4_SPIN_ROLLING_REPAIR_20261004')
sys.path.insert(0,str(P/'isaac/mod4'));import supervise_autonomy as ctl
owner=ctl.read(C/'reports/CONTACT_CONTINUATION_LAUNCHED.json');begin=time.time()
while time.time()-begin<480:
 s=ctl.read(P/'status.json');parent=ctl.helpers.identity(owner['pid'])
 assert parent and parent['start_ticks']==owner['start_ticks'],'Controller exited; inspect instead of restarting'
 assert s['stage']=='training','Unexpected phase; inspect actual status'
 child=ctl.helpers.identity(s['training_pid']);assert child and child['pid']==4146674 and child['start_ticks']==25141740
 try:run=ctl.rate.trainer_run(P/'logs',child['pid'])
 except AssertionError:run=None
 if run:
  saved=ctl.read(run/'latest_complete.json');assert saved['pid']==child['pid']
  assert saved['iteration']>19078
  print(json.dumps(dict(stage='own_complete_save_ready',run=str(run),receipt=saved,elapsed=time.time()-begin)),flush=True);break
 print(json.dumps(dict(stage='awaiting_own_complete_save',elapsed=round(time.time()-begin))),flush=True)
 time.sleep(30)
else:raise AssertionError('Finite own-save wait expired; inspect actual log without relaunch')
'''
c=connect()
try:
 _,o,e=c.exec_command('python3 -u -c '+shlex.quote(code),timeout=510)
 for line in iter(o.readline,''):print(line.strip(),flush=True)
 err=e.read().decode();assert o.channel.recv_exit_status()==0,err
finally:c.close()
