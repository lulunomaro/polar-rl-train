"""One finite read of the closed original training log, without model or physics calls."""
from pathlib import Path
import argparse, importlib.util, json, os, time
N=Path(__file__).resolve().parent;A=N/'attempt03';R=A/'reports'
spec=importlib.util.spec_from_file_location('v2_full_log_original',N/'control.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
parser=argparse.ArgumentParser();parser.add_argument('--resume-local-refusal',action='store_true')
parser.add_argument('--resume-index',type=int,default=1);parser.add_argument('--wait-local',action='store_true');args=parser.parse_args()
if args.resume_local_refusal:
    assert (R/'MOD4V2_FINAL60_COMPLETE_LOG_LOCAL_CIM.json').exists()
    assert not (R/'FINAL60_COMPLETE_LOG_ONCE.json').exists()
    R=R/('complete_log_local_resume'+str(args.resume_index).zfill(2));R.mkdir(exist_ok=False)
m.REPORTS=R
assert not(R/'FINAL60_COMPLETE_LOG_ACTUAL.json').exists()
plan=json.loads((A/'PLAN.json').read_bytes())
local=m.local()
if args.wait_local:
    started=time.time()
    while any(row['ProcessId']!=os.getpid()for row in local.local_rows()):
        assert time.time()-started<10800,'Local controller remains active; no network/once consumption'
        time.sleep(10)
with local.connection('MOD4V2_FINAL60_COMPLETE_LOG')as(client,d):
    m.put('FINAL60_COMPLETE_LOG_ONCE.json',dict(epoch=time.time(),model_reads=0,physics=0,canonical_writes=0))
    code='''from pathlib import Path
import hashlib,json,psutil,time
j=Path(v['root']);release=json.loads((j/'OWNER_EXIT.json').read_bytes())
assert release['all_own_waited']and release['original_cost_settled']and release['original_leases_released']
identity=json.loads((j/'OWNER_STARTED.json').read_bytes())['identity']
alive=psutil.pid_exists(identity['pid'])and psutil.Process(identity['pid']).create_time()==identity['creation']
assert not alive
logs={}
for name in ['WORKER.log','EVAL.log','OWNER.log']:
 p=j/name;raw=p.read_bytes();logs[name]=dict(path=str(p),bytes=len(raw),SHA=hashlib.sha256(raw).hexdigest(),text=raw.decode('utf8','replace'))
print(json.dumps(dict(epoch=time.time(),logs=logs,exact_owner_alive=alive,release=release,model_reads=0,physics=0,canonical_writes=0)))'''
    value=d.code(client,d.PY72,code,dict(root=plan['remote_root']),timeout=45)
    m.put('FINAL60_COMPLETE_LOG_ACTUAL.json',value)
    print(json.dumps(dict(exact_owner_alive=value['exact_owner_alive'],logs={name:dict(bytes=row['bytes'],SHA=row['SHA'])for name,row in value['logs'].items()})))
