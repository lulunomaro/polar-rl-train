from pathlib import Path
import sys,json,time,hashlib,shlex,traceback
D=Path(__file__).resolve().parent;W=D.parent;R=D/'reports';R.mkdir(exist_ok=True)
PRIOR=W/'MOD4_E1_WAVE50_INDEPENDENT_PREPARE_20261012'
sys.path.insert(0,str(PRIOR));import wave50_io as old
io=old.io;H=old.H
OLD='/home/egde/rl_candidates/MOD4_S3_E1_WAVE50_ENTRY_INITIALIZATION_REVIEWED_20261012'
CPU_ROOT='/home/egde/rl_candidates/MOD4_S3_E1_WAVE50_CPU_PREPARED_20261012'
ROOT='/home/egde/rl_candidates/MOD4_S3_E1_WAVE50_ENTRY_SECOND_BOUNDED_20261012'
SOURCE_SHA='ea9fd8558079ec690b0a483e3620c27201ed1afc36cfac56ec2a5c74f42c1f5a'
ENTRY_LOCAL=W/'MOD4_E1_WAVE50_ENTRY_PREPARE_20261012'
SOURCE=json.loads((ENTRY_LOCAL/'reports/ENTRY148_COMPLETE_SCOPE_DECISION.json').read_bytes())['own_checkpoint']['path']
def save(name,value):
 p=R/name;assert not p.exists(),p;p.write_bytes(json.dumps(value,ensure_ascii=False,indent=2).encode());return p
def run(n,code):
 _,o,e=n.exec_command(io.PY+' -c '+shlex.quote(code),timeout=180);raw=o.read();err=e.read();rc=o.channel.recv_exit_status()
 if rc:
  error=dict(returncode=rc,stdout=raw.decode('utf8','replace'),stderr=err.decode('utf8','replace'))
  save('REMOTE_ERROR_'+str(time.time_ns())+'.json',error);raise RuntimeError(json.dumps(error))
 return json.loads(raw)
