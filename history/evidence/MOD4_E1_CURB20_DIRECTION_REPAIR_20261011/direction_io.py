from pathlib import Path
import sys,json,time,hashlib,shlex
D=Path(__file__).resolve().parent;W=D.parent;R=D/'reports';R.mkdir(exist_ok=True)
sys.path.insert(0,str(W/'MOD4_E1_CURB20_ENTRY_REPAIR_20261011'));import repair_io as io
OLD='/home/egde/rl_candidates/MOD4_S3_E1_CURB20_ENTRY_SEED_REVIEWED_20261011'
NEW='/home/egde/rl_candidates/MOD4_S3_E1_CURB20_DIRECTION_REPAIR_20261011'
SHA=io.SHA;H=io.H
def save(name,v):
 p=R/name;assert not p.exists(),p;p.write_bytes(json.dumps(v,ensure_ascii=False,indent=2).encode());return p
def run(n,code):
 _,o,e=n.exec_command(io.PY+' -c '+shlex.quote(code),timeout=180);b=o.read();err=e.read();rc=o.channel.recv_exit_status()
 if rc:
  p=save('CPU_EXECUTION_ERROR_'+str(time.time_ns())+'.json',dict(epoch=time.time(),returncode=rc,stdout=b.decode('utf8','replace'),stderr=err.decode('utf8','replace'),no_GPU_or_budget_write=True));raise RuntimeError(str(p))
 return json.loads(b)
