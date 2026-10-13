"""Read frozen copies of actual reports/logs and artifact indexes; no GPU replay."""
from pathlib import Path
import base64,hashlib,json,time,sys,subprocess
D=Path(__file__).resolve().parent;sys.path.insert(0,str(D.parent/'MOD4_4090_WINDOWS_REPAIR_20261013'))
from windows4090_native_transport import connect,powershell,base
R='C:/Users/Win10/Documents/MOD4_WAVE50_WINDOWS_4090_20261013'
def collect():
 stamp=str(time.time_ns());dest=D/('REMOTE_ACTUAL_EVIDENCE_'+stamp);dest.mkdir()
 code="""from pathlib import Path;import json,hashlib,time,zipfile
r=Path('"""+R+"""');out=r/'TEMP20GB_SAVED_EVIDENCE_"""+stamp+""".zip';rows=[];artifacts=[]
def H(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(4*1024*1024),b''):h.update(b)
 return h.hexdigest()
with zipfile.ZipFile(out,'x',zipfile.ZIP_DEFLATED) as z:
 for scope in sorted(r.glob('temporary_scope*memory20GB*')):
  for p in sorted(scope.rglob('*')):
   if not p.is_file() or any(x in p.parts for x in ('runtime2048','source_snapshot','__pycache__')) or p.name.endswith('.partial'):continue
   if p.suffix.lower() in ('.pt','.npz','.usd','.zip'):
    before=p.stat();sha=H(p);after=p.stat()
    if (before.st_size,before.st_mtime_ns)==(after.st_size,after.st_mtime_ns):artifacts.append(dict(path=str(p),bytes=after.st_size,sha256=sha,actual_original_retained=True))
    continue
   b=p.read_bytes();name=p.relative_to(r).as_posix();z.writestr(name,b);rows.append(dict(path=str(p),archive=name,bytes=len(b),sha256=hashlib.sha256(b).hexdigest(),atomic_snapshot_bytes_not_permanent_process_state=True))
 z.writestr('ACTUAL_COLLECTION_INDEX.json',json.dumps(dict(epoch=time.time(),file_rows=rows,large_original_artifacts=artifacts,actual_only_no_GPU_or_oldonce_replay=True),indent=2))
print(json.dumps(dict(path=str(out),bytes=out.stat().st_size,sha256=H(out),reports=len(rows),artifacts=len(artifacts))))
"""
 b=base64.b64encode(code.encode()).decode();actual=json.loads(powershell(connect(),"[Console]::OutputEncoding=[Text.Encoding]::UTF8;& '"+R+"/env/python.exe' -c \"import base64;exec(base64.b64decode('"+b+"'))\"",90))
 local=D/Path(actual['path']).name
 result=subprocess.run(base('scp')+['-q','Win10@10.24.4.210:'+actual['path'],str(local)],capture_output=True,timeout=120);assert result.returncode==0,result.stderr
 assert hashlib.sha256(local.read_bytes()).hexdigest()==actual['sha256']
 import zipfile
 with zipfile.ZipFile(local) as z:
  index=json.loads(z.read('ACTUAL_COLLECTION_INDEX.json'))
  for row in index['file_rows']:
   name=Path(row['archive']);assert '..' not in name.parts and not name.is_absolute();raw=z.read(row['archive']);assert len(raw)==row['bytes'] and hashlib.sha256(raw).hexdigest()==row['sha256'];p=dest/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(raw)
  (dest/'ACTUAL_COLLECTION_INDEX.json').write_bytes(z.read('ACTUAL_COLLECTION_INDEX.json'))
 report=D/'reports'/('ALL_TEMP20GB_SAVED_REMOTE_EVIDENCE_'+stamp+'.json');report.write_text(json.dumps(dict(epoch=time.time(),actual=actual,local_original_archive=str(local),actual_extracted_reports=str(dest),full_report_log_snapshot_byteSHA_exact=True,artifact_originals_retained_index_only=True),indent=2),encoding='utf8')
 print(json.dumps(dict(report=str(report),remote_reports=actual['reports'],remote_artifacts=actual['artifacts'],exact=True)))
if __name__=='__main__':collect()
