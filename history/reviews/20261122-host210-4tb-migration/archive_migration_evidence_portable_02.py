from pathlib import Path
import sys,json,hashlib,tarfile,io,datetime,shlex
from connection import open_connection,run_python
P=Path(__file__).resolve().parent;REPO=Path('C:/Users/lulu/Desktop/claude/mjcf/polar-rl-train');OUT=REPO/'history/reviews/20261122-host210-4tb-migration';OUT.mkdir(parents=True,exist_ok=True)
sys.path.insert(0,str(REPO/'archive_tools'));from capture_history import redact
assert not (OUT/'EVIDENCE_INDEX_01.json').exists(),'Archive already exists; append later reports instead of duplicating the snapshot'
remote_code=r"""from pathlib import Path
import tarfile,json,hashlib
D=Path('/mnt/robowork4t/workspaces/robomaster/migration');W=D.parent;out=Path('/tmp/robomaster_migration_remote_evidence_01.tar.gz');assert not out.exists()
files=[p for p in D.rglob('*') if p.is_file() and not p.is_symlink() and p.suffix.lower() in ['.json','.jsonl','.log','.txt','.md','.py','.ps1','.gz','.bin']]
with tarfile.open(out,'w:gz') as tar:
 for p in sorted(files):tar.add(p,arcname='migration/'+str(p.relative_to(D)),recursive=False)
 for p in [W/'README.md',W/'robomaster.code-workspace']:
  if p.is_file():tar.add(p,arcname='workspace/'+p.name,recursive=False)
print(json.dumps({'path':str(out),'bytes':out.stat().st_size,'sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'files':len(files)}))
"""
c,restore,secret=open_connection();secret=None
try:
 _,o,e=c.exec_command('/usr/bin/python3 -c '+shlex.quote(remote_code),timeout=None);raw=o.read().decode();err=e.read().decode();rc=o.channel.recv_exit_status();assert rc==0,(rc,err,raw);meta=json.loads(raw)
finally:c.close()
download=P/'remote_evidence_download_01.tar.gz'
c,restore,secret=open_connection();secret=None
try:
 with c.open_sftp() as s:s.get(meta['path'],str(download))
finally:c.close()
assert hashlib.sha256(download.read_bytes()).hexdigest()==meta['sha256']
meta['local_copy']=str(download)
index={'captured_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'remote_transport':meta,'files':[],'archives':[],'large_payloads':'Models and raw training payloads remain in migrated server workspace. Per-file path/bytes/SHA appear in compressed manifests.'}
def add(tar,data,name,source,mtime):
 original=hashlib.sha256(data).hexdigest();original_bytes=len(data);redactions=0
 try:
  text=data.decode('utf-8');clean,redactions=redact(text)
  if redactions:data=clean.encode('utf-8')
 except UnicodeDecodeError:pass
 item=tarfile.TarInfo(name);item.size=len(data);item.mtime=int(mtime);item.mode=0o644;tar.addfile(item,io.BytesIO(data))
 index['files'].append({'source':source,'source_bytes':original_bytes,'source_sha256':original,'archive_path':Path(tar.name).relative_to(REPO).as_posix(),'archive_entry':name,'archive_bytes':len(data),'archive_sha256':hashlib.sha256(data).hexdigest(),'redactions':redactions})
local=OUT/'LOCAL_CONTROL_01.tar.gz'
with tarfile.open(local,'w:gz') as tar:
 for p in sorted(P.iterdir()):
  if not p.is_file() or p.name.startswith('remote_evidence_download_') or p.suffix.lower()=='.tmp':continue
  add(tar,p.read_bytes(),'local_control/'+p.name,str(p),p.stat().st_mtime)
remote=OUT/'REMOTE_CONTROL_01.tar.gz'
with tarfile.open(download,'r:gz') as inp,tarfile.open(remote,'w:gz') as tar:
 for item in inp:
  if not item.isfile():continue
  data=inp.extractfile(item).read();source='/mnt/robowork4t/workspaces/robomaster/'+item.name
  add(tar,data,'remote_control/'+item.name,source,item.mtime)
for p in [local,remote]:
 assert p.stat().st_size<50_000_000,'Split evidence archive before Git recording'
 index['archives'].append({'path':p.relative_to(REPO).as_posix(),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
(OUT/'EVIDENCE_INDEX_01.json').write_text(json.dumps(index,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'files':len(index['files']),'archives':index['archives']},ensure_ascii=False))
