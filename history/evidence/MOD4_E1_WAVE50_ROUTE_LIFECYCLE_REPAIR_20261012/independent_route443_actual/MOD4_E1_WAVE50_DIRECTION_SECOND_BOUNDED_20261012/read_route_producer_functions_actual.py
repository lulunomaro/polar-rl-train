from wave_direction_second_io import *

def main():
 n,w=io.connect_both()
 try:
  v=run(n,r'''from pathlib import Path
import json,hashlib,time
D=Path(ROOT_TOKEN);f=json.loads((D/'reports/SOURCE_FREEZE.json').read_bytes())['sha256'];out={}
for name in f:
 if name.endswith('.py') and not '/floor_fix_source_before/' in name:
  p=D/name;raw=p.read_bytes()
  if any(x in raw for x in (b'def rough_route_boundary',b'rough_route_boundary =',b'rough_route_boundary=',b'_rough_route_spawn',b'_e1_spawn_xy')) or name.endswith(('retention_flat_runtime.py','retention_flat_runtime_named_owned.py','wave50_full_checkpoint.py')):
   assert hashlib.sha256(raw).hexdigest()==f[name];out[name]=dict(path=str(p),bytes=len(raw),sha256=f[name],text=raw.decode('utf8'))
print(json.dumps(dict(epoch=time.time(),source_count=len(f),sources=out,no_GPU_or_budget_write=True)))
'''.replace('ROOT_TOKEN',repr(ROOT)))
  p=save('ROUTE_PRODUCER_SOURCE_ACTUAL_'+str(time.time_ns())+'.json',v)
  for name,x in v['sources'].items():
   lines=x['text'].splitlines()
   for i,line in enumerate(lines):
    if 'def rough_route_boundary' in line or 'rough_route_boundary = ' in line or 'rough_route_boundary=' in line:print(name,'\n'.join(lines[max(0,i-2):i+23]))
  print(json.dumps(dict(report=str(p),sources=list(v['sources']))))
 finally:io.cleanup(n,w)
if __name__=='__main__':
 try:main()
 except BaseException:save('ROUTE_PRODUCER_READER_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),no_GPU_replay=True));raise
