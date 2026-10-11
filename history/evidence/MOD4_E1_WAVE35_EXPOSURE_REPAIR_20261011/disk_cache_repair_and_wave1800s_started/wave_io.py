from pathlib import Path
import sys,json,time,hashlib,shlex,traceback
D=Path(__file__).resolve().parent;W=D.parent;R=D/'reports';R.mkdir(exist_ok=True)
sys.path.insert(0,str(W/'MOD4_E1_CURB20_DIRECTION_REPAIR_20261011'))
import direction_io as prior
io=prior.io;H=prior.H
OLD='/home/egde/rl_candidates/MOD4_S3_E1_WAVE_G3_INDEPENDENT_20261010'
ROOT='/home/egde/rl_candidates/MOD4_S3_E1_WAVE35_EXPOSURE_REPAIR_20261011'
SOURCE_SHA='3c97c14e91a5483d03cb979cd0de0858f7fd1f2a1758e8469c88b7546b02921e'
def save(name,value):
 p=R/name;assert not p.exists(),p;p.write_bytes(json.dumps(value,ensure_ascii=False,indent=2).encode());return p
def run(n,code):
 try:
  _,o,e=n.exec_command(io.PY+' -c '+shlex.quote(code),timeout=180);raw=o.read();err=e.read();rc=o.channel.recv_exit_status()
  if rc:raise RuntimeError(json.dumps(dict(returncode=rc,stdout=raw.decode('utf8','replace'),stderr=err.decode('utf8','replace'))))
  return json.loads(raw)
 except BaseException:
  save('REMOTE_CPU_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),no_old_GPU_or_once_replay=True));raise
