from pathlib import Path
import sys,json,time,hashlib,shlex,traceback
D=Path(__file__).resolve().parent;W=D.parent;R=D/'reports';R.mkdir(exist_ok=True)
PRIOR=W/'MOD4_E1_WAVE50_INDEPENDENT_PREPARE_20261012'
sys.path.insert(0,str(PRIOR));import wave50_io as old
io=old.io;H=old.H
OLD=old.ROOT
CPU_ROOT='/home/egde/rl_candidates/MOD4_S3_E1_WAVE50_CPU_PREPARED_20261012'
ROOT='/home/egde/rl_candidates/MOD4_S3_E1_WAVE50_SECOND_BOUNDED_20261012'
SOURCE_SHA='219faeadcceaa3e015b6a50ccdbf7614cd0f7e0b1cafe2cea04fad0d59b0c550'
SOURCE=json.loads((PRIOR/'reports/WAVE50_146_COMPLETE_SCOPE_DECISION.json').read_bytes())['own_checkpoint']['path']
def save(name,value):
 p=R/name;assert not p.exists(),p;p.write_bytes(json.dumps(value,ensure_ascii=False,indent=2).encode());return p
def run(n,code):
 _,o,e=n.exec_command(io.PY+' -c '+shlex.quote(code),timeout=180);raw=o.read();err=e.read();rc=o.channel.recv_exit_status()
 if rc:
  error=dict(returncode=rc,stdout=raw.decode('utf8','replace'),stderr=err.decode('utf8','replace'))
  save('REMOTE_ERROR_'+str(time.time_ns())+'.json',error);raise RuntimeError(json.dumps(error))
 return json.loads(raw)
