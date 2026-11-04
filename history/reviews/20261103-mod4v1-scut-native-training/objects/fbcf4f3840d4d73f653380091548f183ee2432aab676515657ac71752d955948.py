"""Read exact failed-owner and target contact API sources; no SDK or model load."""
from pathlib import Path
import importlib.util
import json
import time
import traceback

N=Path(__file__).resolve().parent
A=N/'env20000_scut_stairs_1h_20261104/attempt05'
R=A/'reports'
spec=importlib.util.spec_from_file_location('scut_closed05_reader',N/'run.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);m.R=R
facts=json.loads((R/'FIRST_ACTUAL_RETURNED.json').read_bytes())['files']
assert all(facts['OWNER_EXIT.json'][k]for k in('all_own_waited','original_cost_settled','original_leases_released'))
assert not facts.get('production/FIRST_UPDATED.json')
assert facts['TRAIN_CLOSED.json']['passed_execution'] is False
assert not (R/'CLOSED05_EXACT_SOURCE_READ.json').exists()
code='''from pathlib import Path
import json,time,hashlib
j=Path(v['job']);b=Path('/home/lc01/Zonglin Li/zonglin2')
c=json.loads((b/'state/mod4_single_canonical_authority_20261026/TRAINING_BUDGET_10H.json').read_bytes())
f={}
for name in ['OWNER_STARTED.json','OWNER_EXIT.json','TRAIN_CLOSED.json','GO_PRODUCTION.json','production/ERROR.json','production/APP_CLOSE_INTENT.json']:
 p=j/name; f[name]=json.loads(p.read_bytes()) if p.is_file() else None
assert all(f['OWNER_EXIT.json'][k] for k in ('all_own_waited','original_cost_settled','original_leases_released'))
log=(j/'WORKER.log').read_bytes();text=log.decode('utf8','replace')
base=b/'src/fangzhen_linux/third_party/IsaacLab-3.0.0-beta2.patch1/source'
p=base/'isaaclab_physx/isaaclab_physx/sensors/contact_sensor/contact_sensor.py'
src=p.read_bytes();lines=src.decode().splitlines()
indices=[i for i,line in enumerate(lines) if 'create_rigid_contact_view' in line or 'filter_patterns' in line or 'filter_prim_paths' in line]
selected=sorted(set(k for i in indices for k in range(max(0,i-3),min(len(lines),i+7))))
api=Path('/home/lc01/Zonglin Li/zonglin2/envs/mod4/lib/python3.12/site-packages/isaacsim/extscache/omni.physics.tensors-110.1.13+110.1.2.lx64.r.cp312.u7f4/omni/physics/tensors/api.py')
ar=api.read_bytes();al=ar.decode().splitlines();start=next(i for i,x in enumerate(al) if 'def create_rigid_contact_view' in x)
print(json.dumps(dict(epoch=time.time(),canonical_active=c['active_segment'],remaining=c['remaining_training_seconds'],files=f,worker_log=dict(path=str(j/'WORKER.log'),bytes=len(log),SHA=hashlib.sha256(log).hexdigest(),error_lines=[x for x in text.splitlines()if '[Error]'in x or 'cooking failure'in x or 'foundLost'in x or 'OutOfMemory'in x]),contact_source=dict(path=str(p),bytes=len(src),SHA=hashlib.sha256(src).hexdigest(),excerpt=[dict(line=i+1,text=lines[i])for i in selected]),api_source=dict(path=str(api),bytes=len(ar),SHA=hashlib.sha256(ar).hexdigest(),excerpt=al[start:start+140]),PT_reads=0,SDK_imports=0,physics=0,GPU_scans=0,canonical_writes=0)))'''
try:
    with m.connection('CLOSED05_NAMED_SOURCE_READ')as(client,d):
        value=d.code(client,d.PY72,code,dict(job=json.loads((A/'PLAN.json').read_bytes())['remote_root']),timeout=40)
        m.put('CLOSED05_EXACT_SOURCE_READ.json',value)
    print(json.dumps(dict(canonical_active=value['canonical_active'],remaining=value['remaining'],errors=len(value['worker_log']['error_lines']),contact_source=value['contact_source'],api_excerpt=value['api_source']['excerpt'][:100]),indent=2))
except BaseException:
    m.put('CLOSED05_SOURCE_READ_ERROR_'+str(time.time_ns())+'.json',dict(epoch=time.time(),error=traceback.format_exc(),model_reads=0,physics=0,canonical_writes=0))
    raise
