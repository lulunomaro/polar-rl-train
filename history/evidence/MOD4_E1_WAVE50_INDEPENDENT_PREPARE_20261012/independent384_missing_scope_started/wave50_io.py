from pathlib import Path
import sys,json,time,hashlib,shlex,traceback
D=Path(__file__).resolve().parent;W=D.parent;R=D/'reports';R.mkdir(exist_ok=True)
PRIOR=W/'MOD4_E1_WAVE35_SECOND_BOUNDED_20261011'
sys.path.insert(0,str(PRIOR));import second_io as old
io=old.io;H=old.H
OLD=old.ROOT
CPU_ROOT='/home/egde/rl_candidates/MOD4_S3_E1_WAVE50_CPU_PREPARED_20261012'
ROOT='/home/egde/rl_candidates/MOD4_S3_E1_WAVE50_INDEPENDENT_REVIEWED_20261012'
SOURCE_SHA='b026ade6c98f2f4e5d2cd4c9208cdbc9b0749a3f8df4e0b29f31f4495d3047bd'
SOURCE=json.loads((PRIOR/'reports/WAVE50_LEARNING_TARGET_CPU_PASSED.json').read_bytes())['source_checkpoint']['path']
def save(name,value):
 p=R/name;assert not p.exists(),p;p.write_bytes(json.dumps(value,ensure_ascii=False,indent=2).encode());return p
def run(n,code):
 _,o,e=n.exec_command(io.PY+' -c '+shlex.quote(code),timeout=180);raw=o.read();err=e.read();rc=o.channel.recv_exit_status()
 if rc:
  error=dict(returncode=rc,stdout=raw.decode('utf8','replace'),stderr=err.decode('utf8','replace'))
  save('REMOTE_ERROR_'+str(time.time_ns())+'.json',error);raise RuntimeError(json.dumps(error))
 return json.loads(raw)
