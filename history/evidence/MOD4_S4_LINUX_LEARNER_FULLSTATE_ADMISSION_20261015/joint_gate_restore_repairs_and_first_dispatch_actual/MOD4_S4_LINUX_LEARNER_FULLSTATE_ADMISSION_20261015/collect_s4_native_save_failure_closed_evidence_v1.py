"""Collect actual failed save and physical-prefix evidence; no GPU replay."""
from pathlib import Path
import json,sys,time,hashlib,shlex,traceback
D=Path(__file__).resolve().parent;W=D.parent
sys.path.insert(0,str(W/'MOD4_LINUX_WAVE50_BODYFRAME_RESET_INTEGRATION_20261014'))
import transport_bodyframe_root_owned as t
ROOT='/mnt/mod4_linux_durable_20261013/MOD4_S4_E0_WAVE35_LINUX_NATIVE_FULLSTATE_V1_20261015'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 c=None;sf=None;stamp=str(time.time_ns())
 try:
  c=t.connect();code='''from pathlib import Path
import json,time,hashlib,psutil,importlib.util,importlib.metadata as m
r=Path('''+repr(ROOT)+''');identity=json.loads((r/'PARENT_IDENTITY_ACTUAL.json').read_bytes())
assert not psutil.pid_exists(identity['pid'])
exit=json.loads((r/'own_native120/attempt/EXIT_ACTUAL.json').read_bytes());assert exit['actual_child_absent'] and not psutil.pid_exists(exit['child']['pid'])
rows=[]
for p in sorted(r.rglob('*')):
 if not p.is_file() or '__pycache__' in p.parts or 'isaac' in p.relative_to(r).parts or 'base_runtime' in p.relative_to(r).parts:continue
 raw=p.read_bytes();rows.append(dict(relative=str(p.relative_to(r)),path=str(p),bytes=len(raw),sha256=hashlib.sha256(raw).hexdigest()))
spec={}
for n in ('isaaclab','isaacsim','torch','rsl_rl'):
 s=importlib.util.find_spec(n);spec[n]=dict(origin=s.origin,locations=list(s.submodule_search_locations or []))
print(json.dumps(dict(epoch=time.time(),root=str(r),actual_parent_child_absent=True,files=rows,
 installed_distribution_metadata={n:m.version(n) for n in ('isaaclab','isaacsim','torch','rsl-rl-lib')},
 package_import_resolution_without_import=spec,metadata_not_claimed_loaded_Kit_runtime_build=True)))
'''
  si,so,se=c.exec_command('CUDA_VISIBLE_DEVICES= '+shlex.quote(t.PY)+' -',timeout=60);si.write(code);si.flush();si.channel.shutdown_write();raw=so.read();err=se.read();rc=so.channel.recv_exit_status()
  p=D/'reports'/('S4_NATIVE_FAILURE_COLLECTION_TRANSPORT_'+stamp+'.json');p.write_text(json.dumps(dict(rc=rc,stdout=raw.decode('utf8','replace'),stderr=err.decode('utf8','replace')),indent=2),encoding='utf8');assert rc==0,str(p)
  v=json.loads(raw);out=D/'native120_save_failure_actual'/stamp;out.mkdir(parents=True);sf=c.open_sftp();sf.get_channel().settimeout(60)
  for row in v['files']:
   rel=Path(row['relative'])
   # Original CUDA DR roundtrip PTs remain indexed on the durable host. The
   # partial algorithm-only save is essential to independent CPU classification.
   download=(rel.suffix in ('.json','.log','.py')) or rel.name=='S4_OWN_INTEGRATION_FULLSAVE.pt'
   if download:
    p=out/rel;p.parent.mkdir(parents=True,exist_ok=True);sf.get(row['path'],str(p),max_concurrent_prefetch_requests=16)
    assert p.stat().st_size==row['bytes'] and sha(p)==row['sha256'];row.update(local_path=str(p),twohost_SHA_exact=True)
   else:row.update(remote_original_retained=True,large_artifact_index_only=True)
  report=D/'reports'/('S4_NATIVE120_SAVE_FAILURE_ALL_ACTUAL_EVIDENCE_'+stamp+'.json');report.write_text(json.dumps(v,indent=2),encoding='utf8')
  print(json.dumps(dict(report=str(report),files=len(v['files']),actual_parent_child_absent=True,package_resolution=v['package_import_resolution_without_import'])))
 except Exception:
  (D/'reports'/('S4_NATIVE_FAILURE_COLLECTION_ORIGINAL_ERROR_'+stamp+'.json')).write_text(json.dumps(dict(error=traceback.format_exc(),no_retry=True)),encoding='utf8');raise
 finally:
  if sf:sf.close()
  t.close(c)
if __name__=='__main__':main()
