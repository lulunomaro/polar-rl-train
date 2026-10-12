"""Read installed ray-caster/math implementation only, before judging the reference."""
from scut_wave_schema_io import *

def main():
    w=connect()
    try:
        v=execute(w,r'''import importlib.util,json,time,hashlib
from pathlib import Path
rows=[]
for name in ('isaaclab','isaaclab_physx'):
 spec=importlib.util.find_spec(name)
 if not spec:continue
 roots=list(spec.submodule_search_locations or [])
 for root in roots:
  for p in Path(root).rglob('*ray_caster*.py'):
   raw=p.read_bytes();lines=raw.decode('utf8').splitlines();hits=[i for i,x in enumerate(lines) if any(s in x for s in ('offset.rot','convert_quat','ray_directions','quat_apply'))]
   rows.append(dict(path=str(p),bytes=len(raw),sha256=hashlib.sha256(raw).hexdigest(),matched_source=[dict(line=i+1,context='\n'.join(lines[max(0,i-3):min(len(lines),i+6)])) for i in hits[:25]]))
print(json.dumps(dict(epoch=time.time(),installed_native_sensor_sources=rows,no_app_GPU_or_worker_mutation=True)))
''')
        p=save('NATIVE_SENSOR_QUATERNION_SOURCE_ACTUAL_REVIEW.json',v);print(json.dumps(dict(path=str(p),sources=v['installed_native_sensor_sources'])))
    finally:w.close()

if __name__=='__main__':
    try:main()
    except BaseException:save('SENSOR_SOURCE_READER_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),read_only=True));raise
