"""Read immutable current positive ownsave and exact validator assets, CPU only."""
from pathlib import Path
import sys,json,time,hashlib,subprocess,base64
D=Path(__file__).resolve().parent;sys.path.insert(0,str(D.parent/'MOD4_4090_WINDOWS_REPAIR_20261013'))
from windows4090_native_transport import connect,powershell,upload,base
R='C:/Users/Win10/Documents/MOD4_WAVE50_WINDOWS_4090_20261013'
def H(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 decision=json.loads((D/'reports/CAPACITY_SELECTED_PRODUCTION_DISPATCH_ACTUAL.json').read_bytes());s=decision['actual']['scope'].replace(chr(92),'/');dest=D/f'SELECTED_PRODUCTION_CPU_INPUTS_{time.time_ns()}';dest.mkdir()
 code="""from pathlib import Path;import json,hashlib,base64,time
s=Path('"""+s+"""');a=s/'attempts/temporary2048_train_v1';o=a/'output'
def j(p):return json.loads(p.read_bytes())
def ref(p):return dict(path=str(p),bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest())
mf=j(s/'TEMPORARY_GPU_SEQUENCE_MANIFEST_GRANTED.json');latest=j(o/'WINDOWS4090_LATEST_COMPLETE.json');assert latest['actual_updates']>0
out=dict(epoch=time.time(),scope=str(s),manifest=mf,latest=latest,startup=j(o/'WINDOWS4090_FULLSTATE_STARTUP_VERIFIED.json'),left=j(o/'LEFT_HEAD_ACTUAL_INIT_VERIFIED.json'),guardian=j(a/'GUARDIAN_CURRENT.json'),dispatch=j(a/'DISPATCH_RECEIPT.json'),files=[ref(Path(mf['source']['path'])),ref(Path(latest['path']))])
raw=(a/'worker_stdout.log').read_bytes();assert not any(x in raw for x in (b'buffer overflow detected',b'Contacts have been dropped',b'PhysX scene is corrupted',b'PhysX error:'));out['whole_current_stdout']=dict(bytes=len(raw),sha256=hashlib.sha256(raw).hexdigest(),base64=base64.b64encode(raw).decode(),no_PhysX_error=True,activity_snapshot_not_final=True)
out['payload']={p.name:dict(bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest(),base64=base64.b64encode(p.read_bytes()).decode()) for p in (s/'payload').iterdir() if p.suffix in ('.py','.json')}
print(json.dumps(out))
"""
 reader=dest/'readonly_positive_save_remote.py';compile(code,str(reader),'exec');reader.write_text(code,encoding='utf8');remote=R+'/READONLY_SELECTED_PRODUCTION_'+dest.name+'.py';upload(reader,remote,60)
 a=json.loads(powershell(connect(),"[Console]::OutputEncoding=[Text.Encoding]::UTF8;& '"+R+"/env/python.exe' '"+remote+"'",60))
 for i,row in enumerate(a['files']):
  p=dest/('VALID_PRE_PPO_SOURCE.pt' if i==0 else 'OWN_POSITIVE_PPO_SAVE.pt');subprocess.run(base('scp')+['-q','Win10@10.24.4.210:'+row['path'],str(p)],check=True,capture_output=True,timeout=60);assert H(p)==row['sha256'] and p.stat().st_size==row['bytes'];row['local_actual_path']=str(p)
 (dest/'payload').mkdir()
 for name,row in a.pop('payload').items():
  raw=base64.b64decode(row['base64']);assert len(raw)==row['bytes'] and hashlib.sha256(raw).hexdigest()==row['sha256'];(dest/'payload'/name).write_bytes(raw)
 row=a['whole_current_stdout'];raw=base64.b64decode(row.pop('base64'));p=dest/'WHOLE_CURRENT_STDOUT.log';assert len(raw)==row['bytes'] and hashlib.sha256(raw).hexdigest()==row['sha256'];p.write_bytes(raw);row['actual_local_path']=str(p)
 p=dest/'ACTUAL_COLLECTION.json';p.write_text(json.dumps(a,indent=2),encoding='utf8');print(str(p))
if __name__=='__main__':main()
