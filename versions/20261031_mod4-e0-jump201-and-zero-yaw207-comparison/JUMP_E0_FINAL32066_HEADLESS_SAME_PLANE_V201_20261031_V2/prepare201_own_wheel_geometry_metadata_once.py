"""Read own static wheel collision metadata once; no model/raw trajectory access."""
from pathlib import Path
import hashlib,json,time
B=Path(__file__).resolve().parent;T=B.parent;R=B/'reports'
p=T/'FUDAN_JUMP_PARALLEL_SINGLE_WRITER_HANDOFF_V197_20261031/primary_package/payload/job0/assets/import_contract.json'
with (R/'PURPOSE201_OWN_STATIC_WHEEL_GEOMETRY_SINGLE_READ.json').open('x',encoding='utf8') as f:
    json.dump(dict(epoch=time.time(),source=str(p),maximum_byte_passes=1,scope='Own wheel collision geometry for post-case sampled clearance diagnostics; not a new runtime guard',model_raw_NPZ_reads=0),f,indent=2)
raw=p.read_bytes();c=json.loads(raw);found=[]
def walk(v,path='root'):
    if isinstance(v,dict):
        if v.get('name') in ('left_wheel','right_wheel'):found.append(dict(path=path,value=v))
        for k,x in v.items():
            if k in ('left_wheel','right_wheel'):found.append(dict(path=path+'.'+k,value=x))
            else:walk(x,path+'.'+str(k))
    elif isinstance(v,list):
        for i,x in enumerate(v):walk(x,path+'.'+str(i))
walk(c)
report=dict(epoch=time.time(),source=str(p),source_bytes=len(raw),source_SHA=hashlib.sha256(raw).hexdigest(),static_byte_reads=1,top_keys=list(c),own_wheel_entries=found,not_PhysX_contact_truth=True,model_raw_NPZ_reads=0)
with (R/'ACTUAL201_OWN_STATIC_WHEEL_GEOMETRY_METADATA.json').open('x',encoding='utf8') as f:json.dump(report,f,indent=2)
print(json.dumps(report))
