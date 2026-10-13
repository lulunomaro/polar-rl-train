from pathlib import Path
import sys,json,base64,time,subprocess,hashlib,zipfile
D=Path(__file__).resolve().parent;sys.path.insert(0,str(D.parent/'MOD4_4090_WINDOWS_REPAIR_20261013'))
from windows4090_native_transport import connect,powershell,base
R='C:/Users/Win10/Documents/MOD4_WAVE50_WINDOWS_4090_20261013'
def main():
 out=D/'OWN128_FINAL_FULLTRACE';assert not out.exists();out.mkdir()
 code="""from pathlib import Path;import zipfile,json,hashlib,time
r=Path('"""+R+"""');o=r/'temporary_scope128_memory20GB_logger_ready_v12_20261013/attempts/temporary2048_train_v1/output';z=r/'OWN128_FINAL_FULLTRACE_FOR_CAPACITY.zip';assert not z.exists()
rows=[]
with zipfile.ZipFile(z,'x',zipfile.ZIP_DEFLATED) as f:
 for p in sorted(o.glob('retention_prefix_*.npz')):
  b=p.read_bytes();f.writestr(p.name,b);rows.append(dict(path=str(p),name=p.name,bytes=len(b),sha256=hashlib.sha256(b).hexdigest()))
 for name in ('WINDOWS4090_PPO_FORMAL_FINAL_ACTUAL.json','WINDOWS4090_PPO_UNIQUE_COST_ENDED.json'):
  p=o/name;f.writestr(name,p.read_bytes())
 f.writestr('ACTUAL_INDEX.json',json.dumps(dict(epoch=time.time(),rows=rows),indent=2))
print(json.dumps(dict(path=str(z),bytes=z.stat().st_size,sha256=hashlib.sha256(z.read_bytes()).hexdigest(),NPZ_files=len(rows))))
"""
 b=base64.b64encode(code.encode()).decode();a=json.loads(powershell(connect(),"[Console]::OutputEncoding=[Text.Encoding]::UTF8;& '"+R+"/env/python.exe' -c \"import base64;exec(base64.b64decode('"+b+"'))\"",60));p=D/'OWN128_FINAL_FULLTRACE_FOR_CAPACITY.zip';subprocess.run(base('scp')+['-q','Win10@10.24.4.210:'+a['path'],str(p)],check=True,capture_output=True,timeout=60);assert hashlib.sha256(p.read_bytes()).hexdigest()==a['sha256']
 with zipfile.ZipFile(p) as f:
  ix=json.loads(f.read('ACTUAL_INDEX.json'))
  for row in ix['rows']:
   b=f.read(row['name']);assert hashlib.sha256(b).hexdigest()==row['sha256'];(out/row['name']).write_bytes(b)
  for n in ('ACTUAL_INDEX.json','WINDOWS4090_PPO_FORMAL_FINAL_ACTUAL.json','WINDOWS4090_PPO_UNIQUE_COST_ENDED.json'):(out/n).write_bytes(f.read(n))
 (D/'reports/OWN128_FINAL_FULLTRACE_TWOHOST_COLLECTION_ACTUAL.json').write_text(json.dumps(dict(epoch=time.time(),actual=a,twohost_SHA_exact=True,local=str(out)),indent=2),encoding='utf8');print(json.dumps(a))
if __name__=='__main__':main()
