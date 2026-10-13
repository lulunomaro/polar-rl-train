"""Read completed capacity evidence and immutable own states; no GPU launch."""
from pathlib import Path
import json,time,sys,base64,subprocess,hashlib
D=Path(__file__).resolve().parent
sys.path.insert(0,str(D.parent/'MOD4_4090_WINDOWS_REPAIR_20261013'))
from windows4090_native_transport import connect,powershell,base
R='C:/Users/Win10/Documents/MOD4_WAVE50_WINDOWS_4090_20261013'
def H(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 n=int(sys.argv[1]);assert n in (256,512,1024)
 s=R+f'/capacity{n}_own128_expanded_benchmark_v2_20261013'
 dest=D/f'CAPACITY{n}_COMPLETED_INPUTS_{time.time_ns()}';dest.mkdir()
 code="""from pathlib import Path;import json,hashlib,psutil,time,msvcrt
s=Path('"""+s+"""');r=s.parent
def j(p):return json.loads(p.read_bytes())
def ref(p):return dict(path=str(p),bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest())
out=dict(epoch=time.time(),scope=str(s),manifest=j(s/'TEMPORARY_GPU_SEQUENCE_MANIFEST_GRANTED.json'),stages={})
assert j(s/'SEQUENCE_FINAL_ACTUAL.json')['passed'];rel=j(s/'SEQUENCE_PARENT_OSLOCK_RELEASED_ACTUAL.json');assert rel['OSlock_released'] and rel['all_own_descendants_actual_absent']
out['release']=rel
for name in ('native','fullrestore','train'):
 a=s/'attempts'/('temporary2048_'+name+'_v1');o=a/'output';row={};out['stages'][name]=row
 for p in list(a.glob('*.json'))+list(o.glob('*.json')):row[p.relative_to(a).as_posix()]=j(p)
 assert row['EXIT_RECEIPT.json']['passed'] and row['EXIT_RECEIPT.json']['own_child_and_descendants_actual_absent']
 for v in (row['DISPATCH_RECEIPT.json']['parent'],row['DISPATCH_RECEIPT.json']['child']):
  try:q=psutil.Process(v['pid']);assert q.create_time()!=v['created'],'Actual old owner still active'
  except psutil.NoSuchProcess:pass
try:
 with (r/'WINDOWS4090_GPU_EXCLUSIVE.lock').open('r+b') as f:f.seek(0);msvcrt.locking(f.fileno(),msvcrt.LK_NBLCK,1);f.seek(0);msvcrt.locking(f.fileno(),msvcrt.LK_UNLCK,1)
 out['actual_shared_lock_free']=True
except OSError:out['actual_shared_lock_free']=False
out['completed_scope_lock_release_actual']=True
out['files']=[ref(Path(out['stages'][k]['output/WINDOWS4090_LATEST_COMPLETE.json']['path'])) for k in ('fullrestore','train')]
out['payload']={p.name:p.read_text(encoding='utf8') for p in (s/'payload').glob('*.py')}
print(json.dumps(out))
"""
 b=base64.b64encode(code.encode()).decode()
 a=json.loads(powershell(connect(),"[Console]::OutputEncoding=[Text.Encoding]::UTF8;& '"+R+"/env/python.exe' -c \"import base64;exec(base64.b64decode('"+b+"'))\"",60))
 for i,row in enumerate(a['files']):
  p=dest/('PRE_PPO_SOURCE.pt' if i==0 else 'DISCARD_BENCHMARK_SAVE.pt')
  subprocess.run(base('scp')+['-q','Win10@10.24.4.210:'+row['path'],str(p)],check=True,capture_output=True,timeout=60)
  assert H(p)==row['sha256'] and p.stat().st_size==row['bytes'];row['local_actual_path']=str(p)
 (dest/'payload').mkdir()
 for name,code in a.pop('payload').items():(dest/'payload'/name).write_text(code,encoding='utf8')
 p=dest/'ACTUAL_COLLECTION.json';p.write_text(json.dumps(a,indent=2),encoding='utf8');print(str(p))
if __name__=='__main__':main()
