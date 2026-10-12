from scut_wave_schema_io import *

def main():
    w=connect()
    try:
        v=execute(w,r'''from pathlib import Path
import json,time,hashlib,importlib.util
rows=[]
for name in ('isaaclab','isaaclab_physx'):
 s=importlib.util.find_spec(name)
 for root in list(s.submodule_search_locations or []) if s else []:
  for p in (Path(root)/'sensors').rglob('*.py'):
   raw=p.read_bytes();text=raw.decode('utf8');lines=text.splitlines();ids=[i for i,x in enumerate(lines) if 'self.cfg.offset.rot' in x or 'def _create_offset_buffers' in x]
   if ids:rows.append(dict(path=str(p),bytes=len(raw),sha256=hashlib.sha256(raw).hexdigest(),offset_source=[dict(line=i+1,text='\n'.join(lines[max(0,i-5):min(len(lines),i+28)])) for i in ids]))
P=Path(INPUT_ROOT_TOKEN);src=(P/'original/source/agent_tasks/agent_tasks/direct/wheelbipe/wheelbipe25_v3/env.py').read_text();lines=src.splitlines();ids=[i for i,x in enumerate(lines) if 'def _use_raycast_height' in x or 'def _get_raycast_height' in x]
print(json.dumps(dict(epoch=time.time(),native_offset_buffer_sources=rows,original_SCUT_height_path=[dict(line=i+1,text='\n'.join(lines[i:i+45])) for i in ids],no_GPU_or_worker_mutation=True)))
'''.replace('INPUT_ROOT_TOKEN',repr('D:/MOD4_async_eval/scut_wave50_gate_compare_detached_reviewed_20261012')))
        p=save('EXACT_SENSOR_OFFSET_NATIVE_SEMANTICS_ACTUAL_REVIEW.json',v);print(json.dumps(dict(path=str(p),native=v['native_offset_buffer_sources'],original_height=v['original_SCUT_height_path'])))
    finally:w.close()

if __name__=='__main__':
    try:main()
    except BaseException:save('EXACT_SENSOR_SOURCE_READER_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),read_only=True));raise
