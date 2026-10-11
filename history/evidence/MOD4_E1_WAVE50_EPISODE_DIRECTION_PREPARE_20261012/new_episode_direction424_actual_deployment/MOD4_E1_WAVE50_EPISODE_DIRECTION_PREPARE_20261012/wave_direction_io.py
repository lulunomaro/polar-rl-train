"""Distinct name avoids collision with the inherited CURB direction I/O module."""
from pathlib import Path
import sys,json,time,hashlib,shlex,traceback
D=Path(__file__).resolve().parent;W=D.parent;R=D/'reports';R.mkdir(exist_ok=True)
PRIOR=W/'MOD4_E1_WAVE50_ENTRY_SECOND_BOUNDED_20261012';sys.path.insert(0,str(PRIOR))
import entry_second_io as previous
io=previous.io;H=previous.H
OLD=previous.ROOT
ROOT='/home/egde/rl_candidates/MOD4_S3_E1_WAVE50_EPISODE_DIRECTION_REVIEWED_20261012'
SOURCE=previous.old.SOURCE;SOURCE_SHA=previous.old.SOURCE_SHA
def save(name,value):
 p=R/name;assert not p.exists(),p;p.write_bytes(json.dumps(value,ensure_ascii=False,indent=2).encode());return p
def run(n,code):
 _,o,e=n.exec_command(io.PY+' -c '+shlex.quote(code),timeout=180);raw=o.read();err=e.read();rc=o.channel.recv_exit_status()
 if rc:
  value=dict(returncode=rc,stdout=raw.decode('utf8','replace'),stderr=err.decode('utf8','replace'))
  save('REMOTE_ERROR_'+str(time.time_ns())+'.json',value);raise RuntimeError(json.dumps(value))
 return json.loads(raw)
