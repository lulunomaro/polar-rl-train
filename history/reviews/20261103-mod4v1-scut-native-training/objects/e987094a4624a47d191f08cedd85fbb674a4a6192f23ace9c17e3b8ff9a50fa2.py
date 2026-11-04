"""Request the owned full-save boundary after actual PhysX dropped-pair error."""
from pathlib import Path
import importlib.util
import argparse
import json
import time

N=Path(__file__).resolve().parent
A=N/'env20000_scut_stairs_1h_20261104'
p=argparse.ArgumentParser();p.add_argument('--root',type=Path);args=p.parse_args()
if args.root:A=args.root.resolve()
R=A/'reports'
f=json.loads((R/'FIRST_ACTUAL_RETURNED.json').read_bytes())['files']
if A.name=='attempt03':
    assert(R/'ACTUAL_MESH_COOKING_FAILURE.json').exists()
else:
    assert 'foundLostAggregatePairsCapacity'in f['WORKER.log']and 'simulation will miss interactions'in f['WORKER.log']
assert f['production/FIRST_UPDATED.json']['full_save']
s=importlib.util.spec_from_file_location('scut_stair_owned_stop_transport',N/'run.py')
m=importlib.util.module_from_spec(s);s.loader.exec_module(m);m.R=R
plan=json.loads((A/'PLAN.json').read_bytes())
with m.connection('CAPACITY_ERROR_OWNED_FULLSAVE_STOP03' if A.name=='attempt03'else'CAPACITY_ERROR_OWNED_FULLSAVE_STOP02')as(client,d):
    code='''from pathlib import Path
import json,psutil,time
j=Path(v['root']);started=json.loads((j/'OWNER_STARTED.json').read_bytes())
assert started['identity']['pid']==v['owner'] and started['identity']['creation']==v['creation']
go=json.loads((j/'GO_PRODUCTION.json').read_bytes());assert go==v['GO']
pid=started['identity']['pid'];process=psutil.Process(pid);assert process.create_time()==v['creation']
p=j/'STOP_AFTER_SAVE.json';old=json.loads(p.read_bytes())if p.exists()else None
if old is None:
 with p.open('x')as stream:json.dump(dict(epoch=time.time(),reason=v['reason'],fullsave_required=True),stream)
print(json.dumps(dict(epoch=time.time(),STOP_AFTER_SAVE=json.loads(p.read_bytes()),owner_exact=True,GO=go,no_signal_or_kill=True,canonical_writes=0)))'''
    identity=json.loads((R/'OWNER_LAUNCH.json').read_bytes())
    out=d.code(client,d.PY72,code,dict(root=plan['remote_root'],owner=identity['pid'],creation=identity['creation'],
        GO=f['GO_PRODUCTION.json'],reason='Actual PhysX collision resource or mesh cooking failed; fullsave then exit, no kill or budget refund'),timeout=40)
    m.put('CAPACITY_ERROR_STOP_AFTER_SAVE_ACTUAL.json',out)
print(json.dumps(out))
