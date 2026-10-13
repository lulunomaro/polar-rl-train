from pathlib import Path;import json,hashlib,psutil,time,msvcrt,base64
s=Path('C:/Users/Win10/Documents/MOD4_WAVE50_WINDOWS_4090_20261013/capacity512_own128_expanded_benchmark_v8_20261013');r=s.parent
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
