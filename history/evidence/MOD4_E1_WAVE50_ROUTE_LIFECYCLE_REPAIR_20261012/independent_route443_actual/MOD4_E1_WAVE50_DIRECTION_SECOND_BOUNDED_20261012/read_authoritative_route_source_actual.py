"""Only inspect frozen source and live idle boundary, never execute a controller."""
from wave_direction_second_io import *

def main():
    n,w=io.connect_both()
    try:
        v=run(n,r'''from pathlib import Path
import json,hashlib,time,shutil
D=Path(ROOT_TOKEN);h=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();f=json.loads((D/'reports/SOURCE_FREEZE.json').read_bytes())['sha256'];sources={}
for name in f:
 if name.endswith(('mod4_task.py','e1_terrain_training_health.py','route_isaac.py','wave50_geometry_runtime.py','wave50_full_checkpoint.py','wave50_entry_full_checkpoint_v2.py','wave50_entry_runtime_v2.py','wave50_direction_state.py')):
  p=D/name;assert h(p)==f[name];sources[name]=dict(path=str(p),bytes=p.stat().st_size,sha256=h(p),text=p.read_text())
state=json.loads((D/'reports/E1_STATE.json').read_bytes());assert state['phase']=='E1_WAVE50_direction_second_bounded_saved_review_ready' and state['child'] is None
print(json.dumps(dict(epoch=time.time(),source_count=len(f),sources=sources,state=state,durable_free_bytes=shutil.disk_usage(D).free,no_GPU_or_budget_write=True)))
'''.replace('ROOT_TOKEN',repr(ROOT)))
        save('AUTHORITATIVE_ROUTE_SOURCE_ACTUAL_COLLECTION_'+str(time.time_ns())+'.json',v)
        for name,x in v['sources'].items():
            if name.endswith(('mod4_task.py','e1_terrain_training_health.py','route_isaac.py')):
                s=x['text'];lines=s.splitlines()
                for i,line in enumerate(lines):
                    if 'def route_finished' in line or ('route_finished' in line and '=' in line) or '2.0' in line and ('distance' in line or 'route' in line):print(name, '\n'.join(lines[max(0,i-2):i+18]))
        print(json.dumps(dict(source_count=v['source_count'],durable_free_bytes=v['durable_free_bytes'],phase=v['state']['phase'])))
    finally:io.cleanup(n,w)

if __name__=='__main__':
    try:main()
    except BaseException:save('AUTHORITATIVE_ROUTE_READER_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),no_GPU_replay=True));raise
