from pathlib import Path
from W35_mixed72_bound_spec_v1 import bound_W35_spec
from W35_mixed72_protocol_v1 import PYTHON,JOB
from W35_single72_protocol_v2 import validate_schedule
LOADER='/home/lc01/Zonglin Li/zonglin2/compat/glibc240/ld-linux-x86-64.so.2'
LIBRARY='/home/lc01/Zonglin Li/zonglin2/compat/glibc240:/home/lc01/Zonglin Li/zonglin2/envs/mod4/lib'
REALPY='/home/lc01/Zonglin Li/zonglin2/envs/mod4/bin/python'
OWNER_NAME='W35_single72_finite_owner_authority72_v2.py';NODE_NAME='W35_mixed72_finite_node_v1.py'
def bound_cfgs(request,token):
 assert 'token' not in request and Path(request['owner_root'])==Path(JOB).parent/'owner'
 node=bound_W35_spec(request,token);spec={k:v for k,v in node.items() if k not in ('token','role')}
 cfg=dict(role='owner',token=token,run_id=request['run_id'],experts={'w35':spec},deferred_experts=[],scheduling_authority='human_requested_available_experts',authority_generation=spec['owner_authority_generation'])
 validate_schedule(cfg);return cfg,node
def logical_argv(root,name):return [PYTHON,'-u','-B',str(Path(root)/name)]
def expected_exec(logical):return dict(exe=LOADER,argv=[LOADER,'--library-path',LIBRARY,REALPY,'-B',*logical[1:]],root='/home/lc01/Zonglin Li/zonglin2')
