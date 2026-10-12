from pathlib import Path
import sys,json,time,hashlib,shlex,traceback
D=Path(__file__).resolve().parent;W=D.parent;R=D/'reports';R.mkdir(exist_ok=True)
PRIOR=W/'MOD4_E1_WAVE50_DIRECTION_SECOND_BOUNDED_20261012';sys.path.insert(0,str(PRIOR))
import wave_direction_second_io as previous
io=previous.io;H=previous.H;OLD=previous.ROOT
ROOT='/home/egde/rl_candidates/MOD4_S3_E1_WAVE50_ROUTE_LIFECYCLE_REPAIR_20261012'
SOURCE_SHA='b026ade6c98f2f4e5d2cd4c9208cdbc9b0749a3f8df4e0b29f31f4495d3047bd'
SOURCE='/home/egde/rl_candidates/MOD4_S3_E1_WAVE35_SECOND_BOUNDED_20261011/learning_logs/2026-10-11_23-27-01_e1_WAVE35_second_bounded_observation_1791732224672851875/model_32259.pt'
def save(name,value):
 p=R/name;assert not p.exists(),p;p.write_bytes(json.dumps(value,ensure_ascii=False,indent=2).encode());return p
def run(n,code):
 _,o,e=n.exec_command(io.PY+' -c '+shlex.quote(code),timeout=180);raw=o.read();err=e.read();rc=o.channel.recv_exit_status()
 if rc:
  save('REMOTE_ERROR_'+str(time.time_ns())+'.json',dict(returncode=rc,stdout=raw.decode('utf8','replace'),stderr=err.decode('utf8','replace'),no_GPU_by_CPU_command=True));raise RuntimeError('Remote command failed, original error preserved.')
 return json.loads(raw)
