"""Snapshot own unchanged sources and already saved failure logs for Git; no training action."""
from pathlib import Path
import json,os,hashlib,zipfile,time
from deploy_original_linux20k_formal_once import S as BASE,D
from read_linux_resume_boundary_actual import connect_linux_only
S=BASE.replace('_v1','_runtime_assets_complete_v3')
c=connect_linux_only()
try:
    src=r'''
from pathlib import Path
import json,zipfile,hashlib,time
base=Path(S).parent
roots=[base/'fullscale20k_pureCPU_import_reviewed_v6',base/'original_Linux20k_d05_continuation_v1',base/'original_Linux20k_d05_continuation_EULA_environment_v2',Path(S)]
z=base/('OWN_SOURCE_FAILURE_SNAPSHOT_'+str(time.time_ns())+'.zip');rows=[]
with zipfile.ZipFile(z,'w',zipfile.ZIP_DEFLATED) as f:
 for R in roots:
  for p in R.rglob('*'):
   if not p.is_file() or '__pycache__' in p.parts or p.suffix not in ('.py','.json','.log','.txt','.kit'):continue
   if p.stat().st_size>8000000:continue
   raw=p.read_bytes();name=(Path(R.name)/p.relative_to(R)).as_posix();f.writestr(name,raw);rows.append(dict(remote_path=str(p),archive_path=name,bytes=len(raw),sha256=hashlib.sha256(raw).hexdigest()))
 index=json.dumps(dict(epoch=time.time(),files=rows,read_only_evidence_snapshot=True,no_GPU_or_budget_action=True),indent=2).encode();f.writestr('SOURCE_CAPTURE_INDEX.json',index)
print(json.dumps(dict(path=str(z),bytes=z.stat().st_size,sha256=hashlib.sha256(z.read_bytes()).hexdigest(),files=len(rows))))
'''
    si,so,se=c.exec_command('python3 -',timeout=60);si.write('S='+repr(S)+'\n'+src);si.flush();si.channel.shutdown_write();out=so.read();err=se.read();rc=so.channel.recv_exit_status()
    p=D/'reports/ORIGINAL_SOURCE_AND_FAILURE_ARCHIVE_COLLECTION_ACTUAL.json';p.write_bytes(json.dumps(dict(code=rc,stdout=out.decode(),stderr=err.decode()),indent=2).encode());assert rc==0,str(p);row=json.loads(out)
    q=D/Path(row['path']).name;sf=c.open_sftp();sf.get(row['path'],str(q));sf.close();assert q.stat().st_size==row['bytes'] and hashlib.sha256(q.read_bytes()).hexdigest()==row['sha256']
    target=D/'ORIGINAL_LINUX_AND_V6_SOURCE_FAILURE_SNAPSHOTS';assert not target.exists();target.mkdir()
    with zipfile.ZipFile(q) as z:
        idx=json.loads(z.read('SOURCE_CAPTURE_INDEX.json'))
        for x in idx['files']:
            raw=z.read(x['archive_path']);assert len(raw)==x['bytes'] and hashlib.sha256(raw).hexdigest()==x['sha256'];p=target/x['archive_path'];p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(raw)
        (target/'SOURCE_CAPTURE_INDEX.json').write_bytes(z.read('SOURCE_CAPTURE_INDEX.json'))
    print(json.dumps(row))
finally:c.close();os.environ.pop('RM_SSH_PASSWORD',None)
