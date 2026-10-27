"""One tiny pure structural dispatch+original charge algebra fixture. No owner run."""
from pathlib import Path
import ast,json,hashlib,hmac,sys,types
P=Path(__file__).resolve().parent;sys.path.insert(0,str(P))
# Only original pure functions are compiled; common's filesystem/owner code is not run.
source=(P/'three_slot_common_v1.py').read_text();nodes=[n for n in ast.parse(source).body if isinstance(n,ast.FunctionDef) and n.name in ['terminal','charge_values','authenticated_row']]
ns=dict(json=json,hashlib=hashlib,hmac=hmac);exec(compile(ast.Module(body=nodes,type_ignores=[]),'<original charge/source structure only>','exec'),ns)
remaining=554499.7579419613;c=dict(charged_training_seconds=2268000-remaining,remaining_training_seconds=remaining);a=dict(experts={},charged_expert_seconds=0)
go={'h1':dict(learning_started_epoch=10.,max_parent_seconds=3900),'w35':dict(learning_started_epoch=11.,max_parent_seconds=3900)}
ns['charge_values'](c,a,go,{},15.);assert a['charged_expert_seconds']==9.
rows={'h1':dict(terminal_all_own_children_waited=True,returncode=0,owner_received_terminal_epoch=16.)}
ns['charge_values'](c,a,go,rows,20.);assert a['charged_expert_seconds']==15.
ns['charge_values'](c,a,go,rows,20.);assert a['charged_expert_seconds']==15.
rows['w35']=dict(terminal_all_own_children_waited=True,returncode=0,owner_received_terminal_epoch=22.)
ns['charge_values'](c,a,go,rows,22.);assert a['charged_expert_seconds']==17. and a['experts']['h1']['charged_seconds']==6. and a['experts']['w35']['charged_seconds']==11.
# H1 source is pending: this import-only stub tests ROUTING/registration, never qualifies H1.
h=types.ModuleType('h1_next72_protocol')
def hvalidate(s):assert s['key']=='h1';return True
h.validate_spec=hvalidate;h.nativeflat_valid_ready=lambda row,spec:bool(row.get('SOURCE_STRUCTURAL_STUB_ONLY'));h.flat_go_fields=lambda spec:{'SOURCE_STRUCTURAL_STUB_ONLY':True}
sys.modules['h1_next72_protocol']=h
import mixed72_next_protocol_v1 as m
from W35_mixed72_bound_spec_v1 import bound_W35_spec
import W35_mixed72_protocol_v1 as w
request=dict(node_root=str(Path(w.JOB).parent/'node_w35'),source_CPU_SHA='d022ee93254dbf268c9b743ca0624951680b3f17e9ac791b317a95e2794f35cc',CPU_waited_proof_SHA='d932530973730ac7220274b61b62a006a2198a2693ac06680d372ef71a09941a',manifest_SHA='c844c322b1e447334bf8efd16c8f0292e9d5e5f264c7647601e7eb410fce9b44',run_id='SOURCE_STRUCTURAL_ONLY')
ws=bound_W35_spec(request,'SOURCE_FIXTURE_NOT_LIVE_TOKEN_'+'x'*32)
hs=dict(key='h1',GPU_UUID=m.H1_GPU,execution_backend='target72',run_id=request['run_id'],max_parent_seconds=3900,exit_headroom_seconds=300)
cfg=dict(experts={'h1':hs,'w35':ws},deferred_experts=[],authority_generation=w.GENERATION,scheduling_authority='human_requested_available_experts',run_id=request['run_id'])
assert m.validate_schedule(cfg)
missing=dict(cfg,experts={'h1':hs})
try:m.validate_schedule(missing);raise RuntimeError('missing genuine W35 incorrectly accepted')
except AssertionError:pass
assert m.nativeflat_valid_ready(dict(SOURCE_STRUCTURAL_STUB_ONLY=True),hs)
assert not m.nativeflat_valid_ready(dict(key='w35',phase='ready',actual_validation_fcntl_held=False),ws)
assert m.flat_go_fields(ws)['GPU_UUID']==w.GPU and m.flat_go_fields(hs)['SOURCE_STRUCTURAL_STUB_ONLY']
result=dict(passed=True,scope='pure original charge algebra and dispatch slot-set/source structure only',H1_stub_not_actual_H1_CPU_or_qualification=True,real_owner_LEDGER_GPU_model_GO_not_run=True,two_genuine_slot_registration_required=True,missing_W35_rejected=True,unlocked_W35_not_ready=True,independent_actual_duration_algebra=dict(h1=6.,w35=11.,sum=17.,repeated_update_no_double_charge=True))
with (P/'reports/MIXED72_PURE_STRUCTURAL_DISPATCH_CHARGE_CPU_ACTUAL_V1.json').open('x') as f:json.dump(result,f,indent=2)
print(json.dumps(result))
