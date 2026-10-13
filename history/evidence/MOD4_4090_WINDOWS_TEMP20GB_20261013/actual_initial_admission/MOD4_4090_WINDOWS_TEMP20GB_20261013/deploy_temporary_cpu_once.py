from pathlib import Path
import json,zipfile,hashlib,time,base64,sys,traceback
D=Path(__file__).resolve().parent;Q=D/'payload';W=D.parent
sys.path.insert(0,str(W/'MOD4_4090_WINDOWS_REPAIR_20261013'))
from windows4090_native_transport import connect,powershell,upload
R='C:/Users/Win10/Documents/MOD4_WAVE50_WINDOWS_4090_20261013'
T=R+'/temporary_scope2048_memory20GB_left_repair_20261013'
H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def remote_py(s,code,timeout):
 b=base64.b64encode(code.encode()).decode()
 return powershell(s,"[Console]::OutputEncoding=[System.Text.Encoding]::UTF8;& '"+R+"/env/python.exe' -c \"import base64;exec(base64.b64decode('"+b+"'))\"",timeout=timeout)
def main():
 receipt=D/'reports/TEMP2048_REMOTE_TARGET_CPU_ACTUAL.json';assert not receipt.exists()
 rows=[]
 for p in sorted(Q.iterdir()):
  if p.is_file():
   if p.suffix=='.py':compile(p.read_text(encoding='utf8'),str(p),'exec')
   rows.append(dict(archive=p.name,bytes=p.stat().st_size,sha256=H(p)))
 package=D/'WINDOWS4090_TEMP2048_MEMORY20GB_PAYLOAD_20261013.zip';assert not package.exists()
 with zipfile.ZipFile(package,'w',zipfile.ZIP_DEFLATED) as z:
  for row in rows:z.write(Q/row['archive'],row['archive'])
  z.writestr('BUNDLE_MANIFEST.json',json.dumps(dict(epoch=time.time(),file_rows=rows,requested20GBtemporarybranch=True),indent=2))
 s=connect();remote=R+'/packages/'+package.name
 pre=json.loads(remote_py(s,"from pathlib import Path;import json,psutil;print(json.dumps(dict(scope_exists=Path('"+T+"').exists(),upload_exists=Path('"+R+"/temporary2048_payload').exists(),package_exists=Path('"+remote+"').exists(),RAM_available_bytes=psutil.virtual_memory().available)))",35))
 assert not any(pre[k] for k in ('scope_exists','upload_exists','package_exists')) and pre['RAM_available_bytes']>=22000000000
 upload(package,remote,timeout=60)
 assert powershell(s,"(Get-FileHash -LiteralPath '"+remote+"' -Algorithm SHA256).Hash.ToLower()",timeout=30)==H(package)
 code="""from pathlib import Path;import zipfile,json,hashlib,subprocess,sys,time,os
r=Path('"""+R+"""');p=r/'packages/"""+package.name+"""';assert hashlib.sha256(p.read_bytes()).hexdigest()=='"""+H(package)+"""'
q=r/'temporary2048_payload';assert not q.exists();q.mkdir()
with zipfile.ZipFile(p) as z:
 m=json.loads(z.read('BUNDLE_MANIFEST.json'));assert z.testzip() is None
 for row in m['file_rows']:
  assert Path(row['archive']).name==row['archive'];b=z.read(row['archive']);assert len(b)==row['bytes'] and hashlib.sha256(b).hexdigest()==row['sha256']
  with (q/row['archive']).open('xb') as f:f.write(b);f.flush();os.fsync(f.fileno())
c=subprocess.run([sys.executable,str(q/'materialize_temporary_target_cpu_once.py')],capture_output=True,text=True,encoding='utf8',timeout=180)
assert c.returncode==0,dict(exit_code=c.returncode,stdout=c.stdout,stderr=c.stderr)
print(c.stdout)
"""
 actual=json.loads(remote_py(s,code,220))
 receipt.write_text(json.dumps(dict(epoch=time.time(),pre=pre,package=dict(path=str(package),bytes=package.stat().st_size,sha256=H(package),remote=remote),actual=actual,actual_GPU_started=False),indent=2),encoding='utf8')
 print(json.dumps(dict(report=str(receipt),targetCPU=actual['passed'],actualGPU=False,scope=T)))
if __name__=='__main__':
 try:main()
 except BaseException:
  (D/'reports'/('TEMP2048_CPU_DEPLOY_ORIGINAL_ERROR_'+str(time.time_ns())+'.json')).write_text(json.dumps(dict(epoch=time.time(),error=traceback.format_exc(),unknownoutcome_inspect_no_replay=True),indent=2),encoding='utf8');raise
