"""Read-only whole saved CPU evidence, never collect keys or large weights."""
from pathlib import Path
import base64,hashlib,json,subprocess,time,zipfile
from windows4090_native_transport import connect,powershell,base
D=Path(__file__).resolve().parent
R='C:/Users/Win10/Documents/MOD4_WAVE50_WINDOWS_4090_20261013'
def main():
    stamp=str(time.time_ns());s=connect()
    code="""from pathlib import Path
import hashlib,json,time,zipfile
r=Path('"""+R+"""');scope=r/'training_scope_full20k_left_repair_audited_v6a_20261013'
folders=[r/'install_reports',r/'install_logs',scope/'reports',scope/'prepared']
p=r/'CPU_EVIDENCE_SNAPSHOT_"""+stamp+""".zip';assert not p.exists();rows=[];large=[]
with zipfile.ZipFile(p,'x',compression=zipfile.ZIP_DEFLATED) as z:
 for folder in folders:
  if not folder.exists():continue
  for f in sorted(folder.rglob('*')):
   if not f.is_file():continue
   assert f.resolve().is_relative_to(r.resolve())
   before=f.stat();b=f.read_bytes();after=f.stat();assert (before.st_size,before.st_mtime_ns)==(after.st_size,after.st_mtime_ns)
   row=dict(path=str(f),archive=f.relative_to(r).as_posix(),bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
   if f.suffix.lower() in ('.pt','.npz','.npy','.usd','.zip','.whl','.dmp'):large.append(dict(row,original_retained=True,index_only=True));continue
   assert f.suffix.lower() in ('.json','.log','.txt','.xml','.ndjson'),f
   z.writestr(row['archive'],b);rows.append(row)
 m=dict(epoch=time.time(),all_current_saved_CPU_reports_and_full_logs_snapshotted=True,rows=rows,large_originals_index_only=large,no_GPU_or_Task_or_budget_mutation=True)
 z.writestr('CPU_EVIDENCE_SNAPSHOT_INDEX.json',json.dumps(m,indent=2))
print(json.dumps(dict(path=str(p),bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest(),reports=len(rows),large=len(large))))
"""
    b=base64.b64encode(code.encode()).decode()
    remote=json.loads(powershell(s,"$OutputEncoding=[Console]::OutputEncoding=[Text.UTF8Encoding]::new();& '"+R+"/env/python.exe' -c \"import base64;exec(base64.b64decode('"+b+"'))\"",timeout=60))
    target=D/('REMOTE_CPU_EVIDENCE_EXACT_'+stamp);target.mkdir();package=target/Path(remote['path']).name
    result=subprocess.run(base('scp')+['-q','Win10@10.24.4.210:'+remote['path'].replace('\\','/'),str(package)],capture_output=True,timeout=60)
    assert result.returncode==0,result.stderr.decode('utf8','replace')
    assert package.stat().st_size==remote['bytes'] and hashlib.sha256(package.read_bytes()).hexdigest()==remote['sha256']
    with zipfile.ZipFile(package) as z:
        assert z.testzip() is None;m=json.loads(z.read('CPU_EVIDENCE_SNAPSHOT_INDEX.json'))
        for row in m['rows']:
            b=z.read(row['archive']);assert len(b)==row['bytes'] and hashlib.sha256(b).hexdigest()==row['sha256']
            p=target/row['archive'];assert p.resolve().is_relative_to(target.resolve());p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(b)
        (target/'CPU_EVIDENCE_SNAPSHOT_INDEX.json').write_bytes(z.read('CPU_EVIDENCE_SNAPSHOT_INDEX.json'))
    out=D/'reports'/('ALL_REMOTE_CPU_REPORTS_LOGS_BYTEEXACT_COLLECTED_'+stamp+'.json')
    out.write_text(json.dumps(dict(epoch=time.time(),passed=True,remote_package=remote,local_collection=str(target),full_reports_and_logs=len(m['rows']),large_originals_retained_and_indexed=len(m['large_originals_index_only']),all_remote_to_local_byteSHA_exact=True,Git_supplement_pending=True,no_GPU_or_Task_or_budget_mutation=True),indent=2),encoding='utf8')
    print(json.dumps(dict(report=str(out),remote_files=len(m['rows']),large_indices=len(m['large_originals_index_only']))))
if __name__=='__main__':main()
