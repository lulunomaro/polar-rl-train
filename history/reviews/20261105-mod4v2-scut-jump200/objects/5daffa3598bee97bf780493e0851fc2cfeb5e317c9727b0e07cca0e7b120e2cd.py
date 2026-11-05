"""Read complete logs of a formally returned direct-owner segment once."""
from pathlib import Path
import argparse
import json
import time
from shared_control_access import connection

parser = argparse.ArgumentParser()
parser.add_argument('--root', required=True, type=Path)
args = parser.parse_args()
A = args.root.resolve()
R = A/'reports'
assert (R/'POSTROUND_COMPLETED.json').exists()
assert not (R/'DIRECT_COMPLETE_LOGS.json').exists()
plan = json.loads((A/'PLAN.json').read_bytes())
code = '''from pathlib import Path
import hashlib,json,psutil,time
j=Path(v['root']);release=json.loads((j/'OWNER_EXIT.json').read_bytes())
assert release['all_own_waited']and release['original_leases_released']and not release['error']
identity=json.loads((j/'OWNER_STARTED.json').read_bytes())['identity']
alive=psutil.pid_exists(identity['pid'])and psutil.Process(identity['pid']).create_time()==identity['creation']
assert not alive
logs={}
for name in ['WORKER.log','EVAL.log','OWNER.log']:
 p=j/name;raw=p.read_bytes();logs[name]=dict(path=str(p),bytes=len(raw),SHA=hashlib.sha256(raw).hexdigest(),text=raw.decode('utf8','replace'))
print(json.dumps(dict(epoch=time.time(),logs=logs,exact_owner_alive=alive,release=release,model_reads=0,physics=0,canonical_reads=0,canonical_writes=0)))'''
with (R/'DIRECT_COMPLETE_LOGS_ONCE.json').open('x', encoding='utf8') as f:
    json.dump(dict(epoch=time.time(), root=plan['remote_root'], model_reads=0, physics=0), f, indent=2)
with connection(R, 'FUDAN_DIRECT_FULL_LOGS') as (client, transport):
    result = transport.code(client, transport.PY72, code, dict(root=plan['remote_root']), timeout=45)
with (R/'DIRECT_COMPLETE_LOGS.json').open('x', encoding='utf8') as f:
    json.dump(result, f, indent=2)
print(json.dumps({name:dict(bytes=row['bytes'], SHA=row['SHA']) for name,row in result['logs'].items()}))
