"""Install a unique non-GPU source publisher, preserving all training source files."""
from pathlib import Path
import sys,json,shlex,hashlib
D=Path(__file__).resolve().parent;R=D/'reports';W=D.parent;assert not (R/'SENSOR_COMPLETE_ASYNC_PUBLICATION_LAUNCHED.json').exists()
ROOT='/home/egde/rl_candidates/MOD4_E0_SENSOR_ASYNC_DEPENDENCY_PUBLICATION_20261007'
sys.path.insert(0,str(W/'MOD4_AUTONOMY_SLEEP_20261003'));from remote_io import connect
c=connect()
try:
 with c.open_sftp() as s:
  try:s.stat(ROOT);raise AssertionError('Publisher root already exists; audit instead of relaunch')
  except FileNotFoundError:pass
  s.mkdir(ROOT);s.mkdir(ROOT+'/reports');s.put(str(D/'supervise_sensor_async_publication_review.py'),ROOT+'/supervise_sensor_async_publication_review.py')
 code=r'''
from pathlib import Path
import sys,json,hashlib,time,subprocess,os
D=Path('/home/egde/rl_candidates/MOD4_E0_SENSOR_ASYNC_DEPENDENCY_PUBLICATION_20261007');R=D/'reports';file=D/'supervise_sensor_async_publication_review.py'
compile(file.read_text(),str(file),'exec');freeze=dict(sha256={file.name:hashlib.sha256(file.read_bytes()).hexdigest()},CPU_only=True,no_training_runtime_changes=True)
(R/'SOURCE_FREEZE.json').write_text(json.dumps(freeze,indent=2))
with (D/'publisher.log').open('x') as log:p=subprocess.Popen(['/home/egde/anaconda3/envs/fangzhen-isaaclab/bin/python',str(file)],cwd=D,stdin=subprocess.DEVNULL,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
time.sleep(.5);assert p.poll() is None
proc=Path('/proc')/str(p.pid);fields=(proc/'stat').read_text().rsplit(')',1)[1].split()
identity=dict(pid=p.pid,start_ticks=int(fields[19]),ppid=int(fields[1]),cwd=str((proc/'cwd').resolve()),argv=(proc/'cmdline').read_bytes().split(b'\0')[:-1])
identity['argv']=[x.decode() for x in identity['argv']]
receipt=dict(epoch=time.time(),root=str(D),owner=identity,source_freeze=freeze,CPU_only=True,canonical_write_authority=False,training_launch_authority=False,existing_evaluator_unchanged=True)
(R/'LAUNCHED.json').write_text(json.dumps(receipt,indent=2));(Path('/home/egde/rl_candidates/MOD4_MOE_PLAN_EXECUTION_20261007/reports')/'SENSOR_COMPLETE_ASYNC_PUBLICATION_LAUNCHED.json').write_text(json.dumps(receipt,indent=2))
print(json.dumps(receipt))
'''
 _,o,e=c.exec_command('/usr/bin/python3 -c '+shlex.quote(code),timeout=30);raw=o.read();err=e.read();assert o.channel.recv_exit_status()==0,(raw+err).decode()
 v=json.loads(raw);(R/'SENSOR_COMPLETE_ASYNC_PUBLICATION_LAUNCHED.json').write_text(json.dumps(v,indent=2));print(json.dumps(v))
finally:c.close()
