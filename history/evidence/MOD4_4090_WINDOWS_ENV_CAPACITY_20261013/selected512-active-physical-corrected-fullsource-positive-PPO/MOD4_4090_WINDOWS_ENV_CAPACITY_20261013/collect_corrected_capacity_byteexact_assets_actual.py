"""Read completed capacity evidence and immutable own states; no GPU launch."""
from pathlib import Path
import json,time,sys,base64,subprocess,hashlib
D=Path(__file__).resolve().parent
sys.path.insert(0,str(D.parent/'MOD4_4090_WINDOWS_REPAIR_20261013'))
from windows4090_native_transport import connect,powershell,base,upload
R='C:/Users/Win10/Documents/MOD4_WAVE50_WINDOWS_4090_20261013'
def H(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 n=int(sys.argv[1]);assert n in (256,512,640,768,1024)
 version=sys.argv[2];assert version in ('v7','v8');s=R+f'/capacity{n}_own128_expanded_benchmark_'+version+'_20261013'
 dest=D/f'CAPACITY{n}_COMPLETED_INPUTS_{time.time_ns()}';dest.mkdir()
 code="""from pathlib import Path;import json,hashlib,psutil,time,msvcrt,base64
s=Path('"""+s+"""');r=s.parent
def j(p):return json.loads(p.read_bytes())
def ref(p):return dict(path=str(p),bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest())
out=dict(epoch=time.time(),scope=str(s),manifest=j(s/'TEMPORARY_GPU_SEQUENCE_MANIFEST_GRANTED.json'),stages={},whole_stdout_bytes={})
assert j(s/'SEQUENCE_FINAL_ACTUAL.json')['passed'];rel=j(s/'SEQUENCE_PARENT_OSLOCK_RELEASED_ACTUAL.json');assert rel['OSlock_released'] and rel['all_own_descendants_actual_absent']
out['release']=rel
for name in ('native','fullrestore','train'):
 a=s/'attempts'/('temporary2048_'+name+'_v1');o=a/'output';row={};out['stages'][name]=row
 for p in list(a.glob('*.json'))+list(o.glob('*.json')):row[p.relative_to(a).as_posix()]=j(p)
 assert row['EXIT_RECEIPT.json']['passed'] and row['EXIT_RECEIPT.json']['own_child_and_descendants_actual_absent']
 raw=(a/'worker_stdout.log').read_bytes();assert not any(x in raw for x in (b'buffer overflow detected',b'Contacts have been dropped',b'PhysX scene is corrupted',b'PhysX error:'));row['whole_stdout_capacity_check']=dict(bytes=len(raw),sha256=hashlib.sha256(raw).hexdigest(),no_PhysX_capacity_error=True);out['whole_stdout_bytes'][name]=base64.b64encode(raw).decode()
 for v in (row['DISPATCH_RECEIPT.json']['parent'],row['DISPATCH_RECEIPT.json']['child']):
  try:q=psutil.Process(v['pid']);assert q.create_time()!=v['created'],'Actual old owner still active'
  except psutil.NoSuchProcess:pass
try:
 with (r/'WINDOWS4090_GPU_EXCLUSIVE.lock').open('r+b') as f:f.seek(0);msvcrt.locking(f.fileno(),msvcrt.LK_NBLCK,1);f.seek(0);msvcrt.locking(f.fileno(),msvcrt.LK_UNLCK,1)
 out['actual_shared_lock_free']=True
except OSError:out['actual_shared_lock_free']=False
out['completed_scope_lock_release_actual']=True
out['files']=[ref(Path(out['stages'][k]['output/WINDOWS4090_LATEST_COMPLETE.json']['path'])) for k in ('fullrestore','train')]
out['payload']={p.name:dict(bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest(),base64=base64.b64encode(p.read_bytes()).decode()) for p in [p for p in (s/'payload').iterdir() if p.suffix in ('.py','.json')]}
print(json.dumps(out))
"""
 b=base64.b64encode(code.encode()).decode()
 reader=dest/'readonly_completed_remote_reader.py';compile(code,str(reader),'exec');reader.write_text(code,encoding='utf8')
 remote_reader=R+'/CAPACITY_COMPLETE_READONLY_'+dest.name+'.py';upload(reader,remote_reader,60)
 a=json.loads(powershell(connect(),"[Console]::OutputEncoding=[Text.Encoding]::UTF8;& '"+R+"/env/python.exe' '"+remote_reader+"'",60))
 for name,encoded in a.pop('whole_stdout_bytes').items():
  p=dest/(name+'_complete_worker_stdout.log');raw=base64.b64decode(encoded);row=a['stages'][name]['whole_stdout_capacity_check'];assert len(raw)==row['bytes'] and hashlib.sha256(raw).hexdigest()==row['sha256'];p.write_bytes(raw);row['actual_local_stdout_path']=str(p)
 for i,row in enumerate(a['files']):
  p=dest/('PRE_PPO_SOURCE.pt' if i==0 else 'DISCARD_BENCHMARK_SAVE.pt')
  subprocess.run(base('scp')+['-q','Win10@10.24.4.210:'+row['path'],str(p)],check=True,capture_output=True,timeout=60)
  assert H(p)==row['sha256'] and p.stat().st_size==row['bytes'];row['local_actual_path']=str(p)
 (dest/'payload').mkdir()
 for name,row in a.pop('payload').items():
  raw=base64.b64decode(row['base64']);assert len(raw)==row['bytes'] and hashlib.sha256(raw).hexdigest()==row['sha256'];(dest/'payload'/name).write_bytes(raw)
  frozen=next(r for r in a['manifest']['sourcefreeze_files'] if r['path'].replace(chr(92),'/').endswith('/payload/'+name));assert frozen['sha256']==row['sha256']
 p=dest/'ACTUAL_COLLECTION.json';p.write_text(json.dumps(a,indent=2),encoding='utf8');print(str(p))
if __name__=='__main__':main()
