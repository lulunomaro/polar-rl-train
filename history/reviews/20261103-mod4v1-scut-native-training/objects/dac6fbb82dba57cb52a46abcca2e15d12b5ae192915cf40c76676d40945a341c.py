"""Return the completed original owner's complete logs; never launch production."""
from pathlib import Path
import importlib.util
import json
import time
import traceback

N = Path(__file__).resolve().parent
A = N / 'env20000_scut_stairs_1h_20261104/attempt07'
R = A / 'reports'
read = lambda path: json.loads(Path(path).read_bytes())
spec = importlib.util.spec_from_file_location('scut_closed07_original_transport', N / 'run.py')
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
m.R = R

code = '''from pathlib import Path
import hashlib,json,time,psutil
j=Path(v['root']);identity=json.loads((j/'OWNER_STARTED.json').read_bytes())['identity']
assert identity['pid']==v['owner']['pid'] and identity['creation']==v['owner']['creation']
assert identity['exe']==v['owner']['exe'] and identity['argv']==v['owner']['argv']
go=json.loads((j/'GO_PRODUCTION.json').read_bytes());assert go==v['GO']
exit=json.loads((j/'OWNER_EXIT.json').read_bytes())
assert exit['all_own_waited'] and exit['original_cost_settled'] and exit['original_leases_released'] and exit['error'] is None
files={}
for name in ['OWNER_STARTED.json','GO_PRODUCTION.json','OWNER_EXIT.json','TRAIN_CLOSED.json','production/FINAL.json','production/LATEST_PROGRESS.json','production/ERROR.json','evaluation/RESULT.json','evaluation/ERROR.json']:
 p=j/name
 if p.is_file():files[name]=json.loads(p.read_bytes())
logs={};errors={}
for name in ['WORKER.log','EVAL.log']:
 p=j/name
 if not p.is_file():continue
 raw=p.read_bytes();text=raw.decode('utf8','replace')
 logs[name]=dict(path=str(p),bytes=len(raw),SHA=hashlib.sha256(raw).hexdigest(),text=text)
 errors[name]=[line for line in text.splitlines() if any(term in line.lower() for term in ['[error]','traceback (most recent call last)','cooking failure','failed to cook','foundlostaggregatepairscapacity','patch buffer overflow','outofmemoryerror','dropped pair'])]
alive=False
try:
 p=psutil.Process(identity['pid']);alive=p.create_time()==identity['creation'] and p.status()!=psutil.STATUS_ZOMBIE
except psutil.Error:pass
print(json.dumps(dict(epoch=time.time(),original_identity=identity,exact_owner_alive=alive,files=files,logs=logs,actual_error_lines=errors,PT_reads=0,new_physics=0,GPU_probes=0,canonical_writes=0,remote_process_launches=0)))'''

try:
    assert (R / 'POSTROUND_COMPLETED.json').exists()
    returned = read(R / 'POSTROUND_FULL_RETURNED.json')['files']
    expected_owner = returned['OWNER_STARTED.json']['identity']
    launch = read(R / 'OWNER_LAUNCH.json')
    assert expected_owner['pid'] == launch['pid'] and expected_owner['creation'] == launch['creation']
    assert not (R / 'FINAL_COMPLETE_LOG_ACTUAL.json').exists()
    recovering = (R / 'FINAL_COMPLETE_LOG_READ_ONCE.json').exists()
    once = 'FINAL_COMPLETE_LOG_IDENTITY_READER_RECOVERY_ONCE.json' if recovering else 'FINAL_COMPLETE_LOG_READ_ONCE.json'
    assert not (R / once).exists()
    label = 'PATCH07_FINAL_COMPLETE_LOG_IDENTITY_RECOVERY' if recovering else 'PATCH07_FINAL_COMPLETE_LOG'
    with m.connection(label) as (client, d):
        m.put(once, dict(epoch=time.time(), read_only=True,
            expected_identity_source='POSTROUND_FULL_RETURNED/OWNER_STARTED.json; launcher bash execs original Python',
            remote_process_launches=0, new_physics=0))
        value = d.code(client, d.PY72, code, dict(
            root=read(A / 'PLAN.json')['remote_root'],
            owner=expected_owner,
            GO=read(R / 'FIRST_ACTUAL_RETURNED.json')['files']['GO_PRODUCTION.json']), timeout=45)
        m.put('FINAL_COMPLETE_LOG_ACTUAL.json', value)
    print(json.dumps(dict(exact_owner_alive=value['exact_owner_alive'],
        logs={key: {field: row[field] for field in ['path', 'bytes', 'SHA']}
              for key, row in value['logs'].items()},
        actual_error_lines=value['actual_error_lines'],
        final=value['files']['production/FINAL.json'],
        release=value['files']['OWNER_EXIT.json'], PT_reads=0, new_physics=0)))
except BaseException:
    m.put('FINAL_LOG_READER_ERROR_' + str(time.time_ns()) + '.json',
          dict(epoch=time.time(), error=traceback.format_exc()))
    raise
