"""Read the complete first-rollout log once before binding the sole collector."""
from pathlib import Path
import importlib.util
import json
import time
import traceback

N=Path(__file__).resolve().parent
A=N/'env20000_scut_stairs_1h_20261104/attempt07';R=A/'reports'
read=lambda path:json.loads(Path(path).read_bytes())
spec=importlib.util.spec_from_file_location('scut_patch07_first_original',N/'run.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);m.R=R


try:
    first=read(R/'FIRST_ACTUAL_RETURNED.json')['files']
    assert first['production/FIRST_UPDATED.json']['full_save']
    assert first['production/FIRST_UPDATED.json']['actual_onpolicy_samples']==480000
    assert not(R/'FIRST_COMPLETE_LOG_READ_ONCE.json').exists()
    code='''from pathlib import Path
import hashlib,json,time,psutil
j=Path(v['root']);s=json.loads((j/'OWNER_STARTED.json').read_bytes());i=s['identity'];go=json.loads((j/'GO_PRODUCTION.json').read_bytes())
assert i['pid']==v['owner']['pid']and i['creation']==v['owner']['creation']and go==v['GO']
raw=(j/'WORKER.log').read_bytes();text=raw.decode('utf8','replace')
errors=[x for x in text.splitlines()if '[Error]'in x or 'cooking failure'in x or 'foundLostAggregatePairsCapacity'in x or 'OutOfMemoryError'in x]
files={}
for name in ['OWNER_CURRENT.json','OWNER_EXIT.json','TRAIN_CLOSED.json','production/FIRST_UPDATED.json','production/ERROR.json','production/FINAL.json','production/LATEST_PROGRESS.json']:
 p=j/name
 if p.is_file():files[name]=json.loads(p.read_bytes())
same=False
try:
 p=psutil.Process(i['pid']);same=p.create_time()==i['creation']and p.status()!=psutil.STATUS_ZOMBIE
except psutil.Error:pass
print(json.dumps(dict(epoch=time.time(),exact_owner_alive=same,GO=go,files=files,worker_log=dict(path=str(j/'WORKER.log'),bytes=len(raw),SHA=hashlib.sha256(raw).hexdigest(),text=text),actual_error_lines=errors,production_model_reads=0,new_physics=0,canonical_writes=0)))'''
    with m.connection('PATCH07_FIRST_COMPLETE_LOG')as(client,d):
        m.put('FIRST_COMPLETE_LOG_READ_ONCE.json',dict(epoch=time.time(),read_only=True))
        value=d.code(client,d.PY72,code,dict(root=read(A/'PLAN.json')['remote_root'],owner=read(R/'OWNER_LAUNCH.json'),GO=first['GO_PRODUCTION.json']),timeout=40)
        m.put('FIRST_COMPLETE_LOG_ACTUAL.json',value)
    assert not value['actual_error_lines'],'Actual native errors: preserve failed FIRST and use original save boundary'
    assert 'production/ERROR.json'not in value['files']
    assert value['exact_owner_alive']
    latest=value['files']['production/FIRST_UPDATED.json']
    assert latest['gradient']['actor_norm']>0 and latest['gradient']['critic_norm']>0
    spec=importlib.util.spec_from_file_location('scut_patch07_first_bind',N/'repaired_training_control.py')
    controller=importlib.util.module_from_spec(spec);spec.loader.exec_module(controller)
    controller.A=A;controller.R=R;controller.bind()
    m.put('FIRST_NATIVE_VALIDATED_AND_COLLECTOR_BOUND.json',dict(epoch=time.time(),
        first=latest,full_log_source=str(R/'FIRST_COMPLETE_LOG_ACTUAL.json'),
        actual_native_error_lines=0,collector=read(R/'POSTROUND_EXACT_CIM.json'),
        FIRST_not_skill=True,original_save=first['GO_PRODUCTION.json']['save_deadline']))
    print(json.dumps(dict(FIRST_valid=True,full_log_errors=0,collector=read(R/'POSTROUND_EXACT_CIM.json'),GO=first['GO_PRODUCTION.json'])))
except BaseException:
    m.put('FIRST_PATCH_STATUS_ERROR_'+str(time.time_ns())+'.json',dict(epoch=time.time(),error=traceback.format_exc()))
    raise
