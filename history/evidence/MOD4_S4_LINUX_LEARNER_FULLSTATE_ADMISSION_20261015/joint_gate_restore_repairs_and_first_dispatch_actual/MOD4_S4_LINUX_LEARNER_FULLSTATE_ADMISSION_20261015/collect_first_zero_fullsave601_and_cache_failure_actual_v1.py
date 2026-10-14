"""Retain valid first fullsave and failed cache restore separately; no GPU work."""
from pathlib import Path
import json,sys,time,hashlib,shlex
D=Path(__file__).resolve().parent;W=D.parent
sys.path.insert(0,str(W/'MOD4_LINUX_WAVE50_BODYFRAME_RESET_INTEGRATION_20261014'))
import transport_bodyframe_root_owned as t
ROOT='/mnt/mod4_linux_durable_20261013/MOD4_S4_E0_WAVE35_LINUX_ZERO_FULLSAVE_HEALTH_V3_20261015'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 c=None;sf=None;stamp=str(time.time_ns())
 try:
  c=t.connect();code='''from pathlib import Path
import psutil,json,hashlib,time,fcntl
r=Path('''+repr(ROOT)+''');owner=json.loads((r/'PARENT_IDENTITY_ACTUAL.json').read_bytes());assert not psutil.pid_exists(owner['pid'])
rows=[]
for phase in ('own_first_fullsave0_healthschema','own_fullrestore0_healthschema'):
 a=r/phase/'attempt';e=json.loads((a/'EXIT_ACTUAL.json').read_bytes());assert e['actual_child_absent'] and not psutil.pid_exists(e['child']['pid'])
 for p in sorted(a.glob('*')):
  if p.is_file():
   raw=p.read_bytes();rows.append(dict(path=str(p),relative=phase+'/attempt/'+p.name,bytes=len(raw),sha256=hashlib.sha256(raw).hexdigest()))
for name in ('PIPELINE_ORIGINAL_ERROR.json','PARENT_EXIT_ACTUAL.json','ROOT_GPU_FIXED_TWO_DISPATCH_ACTUAL.json','PARENT_IDENTITY_ACTUAL.json','S4_NATIVE_FULLSTATE_TARGET_CPU_ACTUAL.json'):
 p=r/name;raw=p.read_bytes();rows.append(dict(path=str(p),relative=name,bytes=len(raw),sha256=hashlib.sha256(raw).hexdigest()))
b=Path('/home/egde/rl_candidates/MOD4_native_floor_continue10h_20260930/TRAINING_BUDGET_10H.json')
for p in (b.parent/'native_floor_supervisor.lock',Path('/home/egde/rl_candidates/MOD4_scut_spin_rate_20261002/autonomy_controller.lock')):
 with p.open('r+b') as f:fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);fcntl.flock(f,fcntl.LOCK_UN)
print(json.dumps(dict(epoch=time.time(),root=str(r),files=rows,own_parent_child_absent_two_locks_free=True,canonical_SHA=hashlib.sha256(b.read_bytes()).hexdigest(),canonical_active=json.loads(b.read_bytes())['active_segment'])))
'''
  si,so,se=c.exec_command('CUDA_VISIBLE_DEVICES= '+shlex.quote(t.PY)+' -',timeout=60);si.write(code);si.flush();si.channel.shutdown_write();raw=so.read();err=se.read();rc=so.channel.recv_exit_status()
  p=D/'reports'/('S4_601_AND_CACHE_FAILURE_COLLECTION_TRANSPORT_'+stamp+'.json');p.write_text(json.dumps(dict(rc=rc,stdout=raw.decode('utf8','replace'),stderr=err.decode('utf8','replace')),indent=2));assert rc==0,str(p)
  v=json.loads(raw);out=D/'zero_fullsave601_and_cache_failure_actual'/stamp;out.mkdir(parents=True);sf=c.open_sftp();sf.get_channel().settimeout(60)
  for row in v['files']:
   rel=Path(row['relative']);download=(rel.suffix in ('.json','.log')) or (rel.parts[0]=='own_first_fullsave0_healthschema' and rel.name=='S4_OWN_INTEGRATION_FULLSAVE.pt') or rel.name=='S4_PRE_RESET_OWN_STATE_ACTUAL_CUDA_DISK.pt'
   if download:
    p=out/rel;p.parent.mkdir(parents=True,exist_ok=True);sf.get(row['path'],str(p),max_concurrent_prefetch_requests=16)
    assert p.stat().st_size==row['bytes'] and sha(p)==row['sha256'];row.update(local_path=str(p),twohost_SHA_exact=True)
   else:row.update(remote_original_retained=True,large_index_only=True)
  p=D/'reports'/('S4_VALID_FIRST_ZERO_FULLSAVE_AND_FAILED_CACHE_ALL_ACTUAL_'+stamp+'.json');p.write_text(json.dumps(v,indent=2));print(json.dumps(dict(report=str(p),files=len(v['files']),actual_exit_locksfree=True)))
 finally:
  if sf:sf.close()
  t.close(c)
if __name__=='__main__':main()
