from pathlib import Path
import sys,json,time,hashlib,shlex,traceback
D=Path(__file__).resolve().parent;W=D.parent;R=D/'reports';R.mkdir(exist_ok=True)
PRIOR=W/'MOD4_E1_WAVE50_INDEPENDENT_PREPARE_20261012'
PREV=W/'MOD4_E1_WAVE50_SECOND_BOUNDED_20261012'
sys.path.insert(0,str(PRIOR));import wave50_io as old
io=old.io;H=old.H;BASE=old.ROOT
OLD='/home/egde/rl_candidates/MOD4_S3_E1_WAVE50_SECOND_BOUNDED_20261012'
ROOT='/home/egde/rl_candidates/MOD4_S3_E1_WAVE50_ENTRY_REVIEWED_20261012'
SOURCE_SHA=old.SOURCE_SHA;SOURCE=old.SOURCE
def save(name,value):
 p=R/name
 with p.open('xb') as f:f.write(json.dumps(value,ensure_ascii=False,indent=2).encode())
 return p
def run(n,code):
 _,o,e=n.exec_command(io.PY+' -c '+shlex.quote(code),timeout=180);raw=o.read();err=e.read();rc=o.channel.recv_exit_status()
 if rc:
  error=dict(returncode=rc,stdout=raw.decode('utf8','replace'),stderr=err.decode('utf8','replace'))
  save('REMOTE_ERROR_'+str(time.time_ns())+'.json',error);raise RuntimeError(json.dumps(error))
 return json.loads(raw)
