from pathlib import Path
import hashlib,json,shlex,sys,time,traceback,threading
D=Path(__file__).resolve().parent;R=D/'reports';W=D.parent
sys.path.insert(0,str(W/'MOD4_LINUX_WAVE50_BODYFRAME_RESET_INTEGRATION_20261014'))
import transport_bodyframe_root_owned as t
CODE=r'''
from pathlib import Path,PurePosixPath
import hashlib,json,sys,tarfile,time
C=CONTEXT
def sha(p):
 h=hashlib.sha256()
 with Path(p).open('rb') as f:
  for b in iter(lambda:f.read(4*1024*1024),b''):h.update(b)
 return h.hexdigest()
rows=[]
for i,x in enumerate(C['original_snapshots']):
 manifest=Path(x['path']);run=manifest.parent;root=run.parent.parent
 for rel,h in x['source_map'].items():
  q=PurePosixPath(rel);assert not q.is_absolute() and '..' not in q.parts
  candidates=[run/'src_snapshot'/rel,root/rel,run/'src_snapshot'/q.name]
  found=next((p for p in candidates if p.is_file() and sha(p)==h),None)
  assert found is not None,dict(job=i,relative=rel,expected=h,candidates=[str(p) for p in candidates])
  rows.append(dict(archive='job'+str(i)+'/runtime/'+rel,path=str(found),bytes=found.stat().st_size,sha256=h))
 p=Path(C['checkpoints'][i]['path']);assert sha(p)==C['checkpoints'][i]['sha256']
 rows.append(dict(archive='job'+str(i)+'/source/source.pt',path=str(p),bytes=p.stat().st_size,sha256=sha(p)))
 rows.append(dict(archive='job'+str(i)+'/original_run_manifest.json',path=str(manifest),bytes=manifest.stat().st_size,sha256=sha(manifest)))
 p=Path(x['metadata']['robot_usd']);assert sha(p)==x['metadata']['robot_usd_sha256']
 rows.append(dict(archive='job'+str(i)+'/assets/robot.usd',path=str(p),bytes=p.stat().st_size,sha256=sha(p)))
old=Path('/mnt/mod4_linux_durable_20261013/MOD4_S4_E0_WAVE35_FIRST_SUPPORTED_GATE45M_V1_20261015')
proof=json.loads((old/'S4_FIRST_FORMAL_TARGET_CPU_ACTUAL.json').read_bytes())
banks=[(name,h) for name,h in proof['sourcefreeze'].items() if name.endswith('.npz')];assert len(banks)==1,banks
name,h=banks[0];bank=old/name;assert sha(bank)==h=='78af9fa47686204ef370271a2da580d762aa9fda1c7a49844ced318b264e6b83'
for i in range(2):rows.append(dict(archive='job'+str(i)+'/runtime/'+name,path=str(bank),bytes=bank.stat().st_size,sha256=h))
meta=json.dumps(dict(epoch=time.time(),rows=rows,source_readonly=True),indent=2).encode()
with tarfile.open(fileobj=sys.stdout.buffer,mode='w|gz') as z:
 import io
 for row in rows:
  m=tarfile.TarInfo(row['archive']);m.size=row['bytes'];m.mode=0o600
  with Path(row['path']).open('rb') as f:z.addfile(m,f)
 m=tarfile.TarInfo('SOURCE_SNAPSHOT_FILES_ACTUAL.json');m.size=len(meta);m.mode=0o600;z.addfile(m,io.BytesIO(meta))
'''
def main():
 v=json.loads((R/'SOURCE210_CHECKPOINTS_CANONICAL_AND_ORIGINAL_CONTRACT_ACTUAL.json').read_bytes())
 assert v['canonical']['active'] is None and all(x['free'] for x in v['actual_two_fcntl'])
 out=D/'original_CURB410_SLOPE404_and_full_sources_assets_v1.tar.gz';assert not out.exists()
 c=None
 try:
  c=t.connect();si,so,se=c.exec_command('CUDA_VISIBLE_DEVICES= PYTHONDONTWRITEBYTECODE=1 '+shlex.quote(t.PY)+' -B -',timeout=300)
  code=CODE.replace('CONTEXT',repr(v));si.write(code);si.flush();si.channel.shutdown_write()
  errors=[];thread=threading.Thread(target=lambda:errors.append(se.read()),daemon=True);thread.start()
  h=hashlib.sha256();size=0
  with out.open('xb') as f:
   for b in iter(lambda:so.read(4*1024*1024),b''):f.write(b);h.update(b);size+=len(b)
  thread.join();rc=so.channel.recv_exit_status();err=b''.join(errors).decode(errors='replace')
  with (R/'ORIGINAL_JOB_SOURCE_ARCHIVE_STREAM_ACTUAL.json').open('x') as f:json.dump(dict(epoch=time.time(),path=str(out),bytes=size,sha256=h.hexdigest(),rc=rc,stderr=err,original_retained=True,no_source_write_GPU_PPO_or_budget=True),f,indent=2)
  assert rc==0,err
  import tarfile
  with tarfile.open(out,'r:gz') as z:
   q=z.extractfile('SOURCE_SNAPSHOT_FILES_ACTUAL.json');meta=json.load(q)
   for m in z:
    assert m.isfile() and not m.name.startswith('/') and '..' not in Path(m.name).parts
  with (R/'ORIGINAL_JOB_SOURCE_FILES_ACTUAL.json').open('x') as f:json.dump(meta,f,indent=2)
  print(json.dumps(dict(bytes=size,sha256=h.hexdigest(),files=len(meta['rows']),source_originals_unchanged=True)),flush=True)
 finally:t.close(c)
if __name__=='__main__':
 try:main()
 except BaseException:
  with (R/('ORIGINAL_JOB_SOURCE_COLLECTION_ORIGINAL_ERROR_'+str(time.time_ns())+'.json')).open('x') as f:json.dump(dict(error=traceback.format_exc(),partial_archive_kept_no_blind_replay=True),f,indent=2)
  raise
