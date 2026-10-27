"""Compile remote source and check synthetic proof metadata. Never contacts a host."""
from pathlib import Path
import ast,json,copy,sys,traceback,hashlib,datetime
D=Path(__file__).resolve().parent;L=D.parent;T=L.parent
sys.path.append(str(L/'agent_native87_worker_and_target_CPU_entry_candidate'))
import native87_protocol_v1 as p
import native87_install_activate_support_v1 as s
from native87_closed_source_CPU_v1 import validate_proof_data
rows=[]
def case(name,fn):
 try:detail=fn();rows.append(dict(name=name,passed=True,detail=detail))
 except Exception:rows.append(dict(name=name,passed=False,error=traceback.format_exc()))
def yes(v):assert bool(v)
def rejects(fn):
 try:fn()
 except (AssertionError,ValueError,KeyError):return True
 raise AssertionError('expected rejection')
spec=dict(key='h1',native87_policy_only=True,new_native_architecture_fresh=True,finite_method_test=True,closed_production_continuation=False,native_continuation=False,
    bootstrap_source_kind='closed_production_policy_only',source_SHA=p.SOURCE_SHA,bootstrap_source_SHA=p.SOURCE_SHA,source_Adamstep=832460,source_normal_PPO_update=138,
    seed=27,method_config=p.METHOD,GPU_UUID=p.GPUS['h1'],execution_backend='source210',policy_hz=100,max_parent_seconds=3900,exit_headroom_seconds=300,
    owner_authority_generation=p.AUTHORITY_GENERATION,fresh_environment_resume_scope='policy_only_no_source_environment_state',manifest_SHA='a'*64,
    native87_contract_SHA='b'*64,qualified_H1_report_SHA='c'*64,previous86_closure_SHA='d'*64,reference_artifact_SHA='e'*64,objective_contract_SHA='f'*64,
    candidate_pins={'target_fixture.py':'1'*64},closed_source_CPU_script='target_fixture.py')
value=dict(passed=True,kind=p.KIND,source_SHA=p.SOURCE_SHA,bootstrap_SHA=p.SOURCE_SHA,source_normal_PPO_update=138,bootstrap_Adam=832460,
    native_continuation_restore_required=False,native_environment_state_from_source=False,source_environment_count=20000,configured_environment_count=4096,
    actual_environment_count=None,actual_GPU_runtime_readback_passed=False,actual_GPU_fresh4096_DR_readback_passed=False,episode_timeout_s=5.,
    GPU_UUID=spec['GPU_UUID'],execution_backend=spec['execution_backend'],seed=27,method_config=p.METHOD,candidate_pins=spec['candidate_pins'],
    **{k:spec[k] for k in ('native87_contract_SHA','qualified_H1_report_SHA','previous86_closure_SHA','reference_artifact_SHA','objective_contract_SHA')},
    **{k:True for k in p.READY_FLAGS})
report_SHA=p.digest(value);argv=['/fixture-only/python','/fixture-only/target.py']
proof=dict(schema='mod4.native87.actual_waited_preinstalled_CPU.v1',not_synthetic=True,actual_CPU_waited_EXIT0=True,returncode=0,
    manifest_SHA=spec['manifest_SHA'],script_relative='target_fixture.py',script_SHA='1'*64,source_SHA=p.SOURCE_SHA,
    report_relative='job0/NATIVE87_POLICY_ONLY_FRESH4096_SOURCE_SDK_CPU_ACTUAL.json',report_SHA=report_SHA,
    started_receipt_SHA='2'*64,waited_receipt_SHA='3'*64,actual_identity=dict(pid=123,creation=100.,argv=argv,exe='/fixture-only/python'),
    started_epoch=101.,waited_epoch=102.,ready_envelope=dict(value=value,SHA=report_SHA,actual_CPU_waited_EXIT0=True))
kwargs=dict(manifest_SHA=spec['manifest_SHA'],script_SHA='1'*64,report_SHA=report_SHA,started_SHA='2'*64,waited_SHA='3'*64,expected_argv=argv,expected_exe='/fixture-only/python')
case('proof_validator_positive_SYNTHETIC_ONLY_not_actual_admission',lambda:bool(validate_proof_data(proof,spec,**kwargs)))
for field,bad in [('not_synthetic',False),('returncode',1),('manifest_SHA','9'*64),('source_SHA','9'*64),('script_SHA','9'*64),('report_SHA','9'*64),('started_receipt_SHA','9'*64),('waited_receipt_SHA','9'*64)]:
 def wrong(field=field,bad=bad):v=copy.deepcopy(proof);v[field]=bad;return rejects(lambda:validate_proof_data(v,spec,**kwargs))
 case('reject_wrong_'+field,wrong)
def identity_wrong():
 v=copy.deepcopy(proof);v['actual_identity']['argv']=['wrong'];return rejects(lambda:validate_proof_data(v,spec,**kwargs))
case('reject_wrong_actual_identity_argv',identity_wrong)
for name,value in vars(s).items():
 if name.startswith('REMOTE_'):case('compile_'+name,lambda name=name,value=value:compile(value,name,'exec') is not None)
for file in D.glob('*.py'):case('parse_'+file.name,lambda file=file:ast.parse(file.read_text('utf8')) is not None)
def cache_source():
 text=(D/'native87_closed_source_CPU_v1.py').read_text();tree=ast.parse(text)
 assert len([n for n in ast.walk(tree) if isinstance(n,ast.Call) and isinstance(n.func,ast.Attribute) and n.func.attr=='Popen'])==1
 assert "if spec.get('preinstalled_CPU_proof_SHA'):" in text and "with proof_path.open('x'" in text
 assert 'torch.load' not in text
 assert 'p.wait()' in text and "identity['exe']" in text and "identity['argv']==args" in text
 assert 'native87_closed_source_CPU_v1 import load' in s.REMOTE_CPU
 assert 'runpy' not in s.REMOTE_CPU
 return dict(one_actual_CPU_execution_branch=True,no_model_load_in_cache_dispatcher=True,external_proof_pin_required=True)
case('CPU_once_and_node_cache_AST',cache_source)
def activation_source():
 text=(D/'activate_three_H1_native87_sole72_after_actual_CPU_unused_once.py').read_text()
 assert 'validate_CPU(cpu,q,protocol)' in text and "specs=cpu['specs_with_preinstalled_CPU_proof']" in text
 assert "preinstalled_CPU_proof_SHA" in text and 'native87_protocol_v1.py' in s.OWNER_FILES and 'native87_closed_source_CPU_v1.py' in s.OWNER_FILES
 assert '577055.9868602753' in s.REMOTE_ACCOUNT and '86412.86069250107' in s.REMOTE_ACCOUNT
 assert '32*1024**3' in s.REMOTE_PREACTIVATE_NODE and '>15669' in s.REMOTE_PREACTIVATE_NODE
 assert 'EF3105C85DD986BD' in s.REMOTE_PREACTIVATE_NODE
 assert "owner_identity=identity['owner_identity']" in text and "owner_root=q['owner_root']" in text
 return dict(sole72_and_all3_actual_CPU_proof_required=True,independent_owner_root_not_cwd=True)
case('activation_source_gates_AST',activation_source)
report=dict(UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),passed=all(r['passed'] for r in rows),passed_count=sum(r['passed'] for r in rows),total=len(rows),tests=rows,
    synthetic_proof_metadata_only=True,no_actual_proof_or_ready_generated=True,no_network_model_Task_GO_fee_or_Git=True)
with (D/'INSTALL_ACTIVATE_CPU_PROOF_SOURCE_REVIEW_V1_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(report,f,indent=2)
print(json.dumps(dict(passed=report['passed'],passed_count=report['passed_count'],total=report['total'])))
if not report['passed']:raise SystemExit(1)
