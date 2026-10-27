"""Root-qualified H1 spec + actual W35 CPU fields -> one original72 cohort."""
from pathlib import Path
from W35_mixed72_bound_spec_v1 import bound_W35_spec
from W35_mixed72_protocol_v1 import PYTHON,GENERATION,H,require
from mixed72_next_protocol_v1 import validate_schedule
LOADER='/home/lc01/Zonglin Li/zonglin2/compat/glibc240/ld-linux-x86-64.so.2'
LIBRARY='/home/lc01/Zonglin Li/zonglin2/compat/glibc240:/home/lc01/Zonglin Li/zonglin2/envs/mod4/lib'
REALPY='/home/lc01/Zonglin Li/zonglin2/envs/mod4/bin/python'
OWNER_NAME='mixed72_next_finite_owner_authority72_v1.py'
W35_NODE_NAME='W35_mixed72_finite_node_v1.py'

def no_secret_request(v):
 if isinstance(v,dict):
  assert all(k.lower() not in ('token','password','secret') for k in v)
  for x in v.values():no_secret_request(x)
 elif isinstance(v,(list,tuple)):
  for x in v:no_secret_request(x)
 return True

def bound_cfgs(request,token):
 no_secret_request(request);assert isinstance(token,str) and len(token)>=32
 h=dict(request['h1_spec']);hparent=Path(h['job_root']).parent
 assert h['key']=='h1' and h['run_id']==request['run_id']
 assert Path(request['owner_root'])==hparent/'owner' and Path(request['h1_node_root'])==hparent/'node_h1'
 assert Path(request['h1_node_filename']).name==request['h1_node_filename'] and request['h1_node_filename'].endswith('.py')
 wr=dict(request['w35_request'],run_id=request['run_id'])
 w=bound_W35_spec(wr,token)
 ws={k:v for k,v in w.items() if k not in ('role','token')}
 cfg=dict(role='owner',token=token,run_id=request['run_id'],experts={'h1':h,'w35':ws},deferred_experts=[],scheduling_authority='human_requested_available_experts',authority_generation=GENERATION)
 validate_schedule(cfg)
 return cfg,dict(h,role='node',token=token),w

def logical_argv(root,name):return [PYTHON,'-u','-B',str(Path(root)/name)]

def expected_exec(logical):return dict(exe=LOADER,argv=[LOADER,'--library-path',LIBRARY,REALPY,'-B',*logical[1:]],root='/home/lc01/Zonglin Li/zonglin2')

def validate_owner_sources(owner_root,manifest_SHA):
 import json
 B=Path(owner_root).resolve();owned=Path('/home/lc01/Zonglin Li/zonglin2/tasks')
 assert B.is_relative_to(owned) and B.name=='owner'
 p=B/'MIXED72_OWNER_CONTROLLER_MANIFEST_V1.json';assert H(p)==manifest_SHA
 m=json.loads(p.read_bytes());assert m['schema']=='mod4.mixed72.h1_w35.owner.source.v1' and m['keys']==['h1','w35']
 for r in m['files']:
  f=(B/r['relative']).resolve();assert f.is_relative_to(B) and not f.is_symlink() and f.stat().st_size==r['bytes'] and H(f)==r['SHA']
 return True
