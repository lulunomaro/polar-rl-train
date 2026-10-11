from pathlib import Path
import sys,json,time,hashlib,shlex,traceback
D=Path(__file__).resolve().parent;W=D.parent;R=D/'reports';R.mkdir(exist_ok=True)
PRIOR=W/'MOD4_E1_WAVE35_EXPOSURE_REPAIR_20261011'
sys.path.insert(0,str(PRIOR));import wave_io as previous
io=previous.io;H=previous.H
OLD=previous.ROOT
ROOT='/home/egde/rl_candidates/MOD4_S3_E1_WAVE35_SECOND_BOUNDED_20261011'
SOURCE_SHA='7f1032ad33b87671dcb6450f19c15122de45e3d76a8700d92ab5dcd8be3ee0e4'
SOURCE=OLD+'/learning_logs/2026-10-11_21-35-32_e1_WAVE35_exposure_005_observation_1791725534301979732/model_32160.pt'
def save(name,value):
 p=R/name;assert not p.exists(),p;p.write_bytes(json.dumps(value,ensure_ascii=False,indent=2).encode());return p
def run(n,code):
 try:
  _,o,e=n.exec_command(io.PY+' -c '+shlex.quote(code),timeout=180);raw=o.read();err=e.read();rc=o.channel.recv_exit_status()
  if rc:raise RuntimeError(json.dumps(dict(returncode=rc,stdout=raw.decode('utf8','replace'),stderr=err.decode('utf8','replace'))))
  return json.loads(raw)
 except BaseException:
  save('REMOTE_CPU_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),no_old_once_or_GPU_replay=True));raise
