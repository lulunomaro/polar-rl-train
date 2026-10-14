"""Bounded full collection only after the new own0 actually closes."""
from pathlib import Path
import sys,json,time,shlex,hashlib
D=Path(__file__).resolve().parent;W=D.parent
sys.path.insert(0,str(W/'MOD4_LINUX_WAVE50_BODYFRAME_RESET_INTEGRATION_20261014'))
import transport_bodyframe_root_owned as t
ROOT='/mnt/mod4_linux_durable_20261013/MOD4_S4_E0_WAVE35_DIRECT_OWN_RESTORE_CACHE_V4_20261015'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 c=None;sf=None;stamp=str(time.time_ns())
 try:
  c=t.connect();code='''from pathlib import Path
import json,time,hashlib,psutil,fcntl
r=Path('''+repr(ROOT)+''');p=r/'PIPELINE_COMPLETE_ACTUAL.json';owner=json.loads((r/'PARENT_IDENTITY_ACTUAL.json').read_bytes())
if not p.exists() or psutil.pid_exists(owner['pid']):
 print(json.dumps(dict(epoch=time.time(),pending=True,root=str(r),parent=owner,error=json.loads((r/'PIPELINE_ORIGINAL_ERROR.json').read_bytes()) if (r/'PIPELINE_ORIGINAL_ERROR.json').exists() else None)))
else:
 complete=json.loads(p.read_bytes());assert complete['passed'] and complete['own_fullrestore0_from_valid601_complete'] and len(complete['stages'])==1
 b=Path('/home/egde/rl_candidates/MOD4_native_floor_continue10h_20260930/TRAINING_BUDGET_10H.json')
 for q in (b.parent/'native_floor_supervisor.lock',Path('/home/egde/rl_candidates/MOD4_scut_spin_rate_20261002/autonomy_controller.lock')):
  with q.open('r+b') as f:fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);fcntl.flock(f,fcntl.LOCK_UN)
 rows=[];a=r/'own_fullrestore0_cacheABI_v4/attempt'
 for q in [*a.glob('*'),r/'PIPELINE_COMPLETE_ACTUAL.json',r/'PARENT_EXIT_ACTUAL.json',r/'PARENT_IDENTITY_ACTUAL.json',r/'ROOT_GPU_FIXED_TWO_DISPATCH_ACTUAL.json',r/'S4_NATIVE_FULLSTATE_TARGET_CPU_ACTUAL.json']:
  if q.is_file():
   raw=q.read_bytes();rows.append(dict(relative=str(q.relative_to(r)),path=str(q),bytes=len(raw),sha256=hashlib.sha256(raw).hexdigest()))
 e=json.loads((a/'EXIT_ACTUAL.json').read_bytes());assert e['actual_child_absent'] and not psutil.pid_exists(e['child']['pid'])
 assert json.loads(b.read_bytes())['active_segment'] is None
 print(json.dumps(dict(epoch=time.time(),pending=False,root=str(r),complete=complete,files=rows,
  own_parent_child_absent_two_locks_free=True,canonical_SHA=hashlib.sha256(b.read_bytes()).hexdigest(),canonical_active=None)))
'''
  si,so,se=c.exec_command('CUDA_VISIBLE_DEVICES= '+shlex.quote(t.PY)+' -',timeout=60);si.write(code);si.flush();si.channel.shutdown_write();raw=so.read();err=se.read();rc=so.channel.recv_exit_status()
  p=D/'reports'/('S4_DIRECT_OWN0_COLLECTION_TRANSPORT_'+stamp+'.json');p.write_text(json.dumps(dict(rc=rc,stdout=raw.decode('utf8','replace'),stderr=err.decode('utf8','replace')),indent=2));assert rc==0,str(p)
  v=json.loads(raw)
  if v['pending']:
   print(json.dumps(v));return
  out=D/'direct_own0_cache_v4_actual'/stamp;out.mkdir(parents=True);sf=c.open_sftp();sf.get_channel().settimeout(60)
  for row in v['files']:
   rel=Path(row['relative']);download=rel.suffix in ('.json','.log') or rel.name in ('S4_OWN_INTEGRATION_FULLSAVE.pt','S4_PRE_RESET_OWN_STATE_ACTUAL_CUDA_DISK.pt')
   if download:
    p=out/rel;p.parent.mkdir(parents=True,exist_ok=True);sf.get(row['path'],str(p),max_concurrent_prefetch_requests=16)
    assert p.stat().st_size==row['bytes'] and sha(p)==row['sha256'];row.update(local_path=str(p),twohost_SHA_exact=True)
   else:row.update(remote_original_retained=True,large_index_only=True)
  p=D/'reports'/('S4_DIRECT_OWN0_FULLSTATE_ALL_ACTUAL_'+stamp+'.json');p.write_text(json.dumps(v,indent=2));print(json.dumps(dict(report=str(p),pending=False,files=len(v['files']),source=v['complete']['stages'][0]['checkpoint_SHA'])))
 finally:
  if sf:sf.close()
  t.close(c)
if __name__=='__main__':main()
