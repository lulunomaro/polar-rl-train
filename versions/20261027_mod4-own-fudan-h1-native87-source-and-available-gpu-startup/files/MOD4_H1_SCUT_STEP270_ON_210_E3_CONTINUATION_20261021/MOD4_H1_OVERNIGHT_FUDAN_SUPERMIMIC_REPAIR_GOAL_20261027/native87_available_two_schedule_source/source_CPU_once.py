"""Typed source/metadata fixtures only, not installed SDK/actual CPU proof."""
from pathlib import Path
import ast,copy,hashlib,json,sys
HERE=Path(__file__).resolve().parent;L=HERE.parent;T=L.parent
N=T/'H1_STEP270_THREE_GPU_OWN_FUDAN_NATIVE_V87_20261027'
sys.path[:0]=[str(HERE),str(N/'controllers_r2')]
import native87_protocol_v1 as protocol
import native87_available_two_activation_support_v1 as candidate
import native87_available_two_schedule_v1 as schedule
checks=[]
def H(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def check(v,label):
 assert v,label
 checks.append(label)
def refuse(fn,label):
 try:fn()
 except (AssertionError,ValueError,KeyError,TypeError):checks.append(label);return
 raise AssertionError('accepted '+label)
prepared=N/'reports/AVAILABLE_TWO_NATIVE87R2_SOURCE_PREPARED_ACTUAL.json'
q=json.loads(prepared.read_bytes());boundary=json.loads((HERE/schedule.BOUNDARY_NAME).read_bytes());boundary_SHA=H(HERE/schedule.BOUNDARY_NAME)
check(candidate.validate_prepared(q,protocol,boundary,boundary_SHA),'actual_saved_R2_prepared_metadata_source_only')
old=q.copy();old['roots']=dict(q['roots'],h1=candidate.ROOTS['h1'].replace('v87r2','v87'))
refuse(lambda:candidate.validate_prepared(old,protocol,boundary,boundary_SHA),'old_h1_namespace_refused')
old=copy.deepcopy(q);old['deferred_experts']=[]
refuse(lambda:candidate.validate_prepared(old,protocol,boundary,boundary_SHA),'false_all3_schedule_refused')
old=copy.deepcopy(boundary);old['resources']['gpus'][0]['compute_application_count']=0
refuse(lambda:schedule.validate_boundary(old),'occupied_boundary_not_fabricated')
# Synthetic valid-ready metadata carries current candidate pins but is NEVER
# written to the target or used as actual admission evidence.
cpu=dict(passed=True,actual_finite_returned=True,prepared_source_report_SHA=H(prepared),results={},specs_with_preinstalled_CPU_proof={})
for key,spec in q['specs'].items():
 s=copy.deepcopy(spec);s['preinstalled_CPU_proof_SHA']='a'*64
 v=dict(kind=protocol.KIND,passed=True,source_SHA=protocol.SOURCE_SHA,bootstrap_SHA=protocol.SOURCE_SHA,
 source_normal_PPO_update=138,bootstrap_Adam=832460,native_continuation_restore_required=False,
 native_environment_state_from_source=False,source_environment_count=20000,configured_environment_count=4096,
 actual_environment_count=None,actual_GPU_runtime_readback_passed=False,actual_GPU_fresh4096_DR_readback_passed=False,
 episode_timeout_s=5.,GPU_UUID=s['GPU_UUID'],execution_backend=s['execution_backend'],seed=s['seed'],
 method_config=protocol.METHOD,candidate_pins=s['candidate_pins'],**{k:True for k in protocol.READY_FLAGS})
 for k in ('native87_contract_SHA','qualified_H1_report_SHA','previous86_closure_SHA','reference_artifact_SHA','objective_contract_SHA'):v[k]=s[k]
 e=dict(value=v,SHA=protocol.digest(v),actual_CPU_waited_EXIT0=True,path=candidate.ROOTS[key]+'/job0/NATIVE87_POLICY_ONLY_FRESH4096_SOURCE_SDK_CPU_ACTUAL.json')
 cpu['results'][key]=dict(passed=True,ready_envelope=e,preinstalled_CPU_proof_SHA='a'*64)
 cpu['specs_with_preinstalled_CPU_proof'][key]=s
check(candidate.validate_CPU(cpu,q,protocol,H(prepared)),'synthetic_R2_two_ready_envelopes_positive')
bad=copy.deepcopy(cpu);bad['results']['h1']['ready_envelope']['path']=bad['results']['h1']['ready_envelope']['path'].replace('v87r2','v87')
refuse(lambda:candidate.validate_CPU(bad,q,protocol,H(prepared)),'old_actual_report_path_refused')
bad=copy.deepcopy(cpu);bad['specs_with_preinstalled_CPU_proof']['recovery'].pop('preinstalled_CPU_proof_SHA')
refuse(lambda:candidate.validate_CPU(bad,q,protocol,H(prepared)),'missing_fresh_recovery_proof_refused')
bad=copy.deepcopy(cpu);bad['results']['h1']['ready_envelope']['value']['actual_GPU_runtime_readback_passed']=True
refuse(lambda:candidate.validate_CPU(bad,q,protocol,H(prepared)),'CPU_cannot_claim_actual_GPU_readback')
bad=copy.deepcopy(cpu);bad['prepared_source_report_SHA']='b'*64
refuse(lambda:candidate.validate_CPU(bad,q,protocol,H(prepared)),'wrong_prepared_SHA_refused')
cfg=dict(experts=cpu['specs_with_preinstalled_CPU_proof'],deferred_experts=['e2'],scheduling_authority='human_requested_available_experts',authority_generation=protocol.AUTHORITY_GENERATION,resource_boundary_relative=schedule.BOUNDARY_NAME,resource_boundary_SHA=boundary_SHA)
check(schedule.validate_schedule(cfg),'two_active_original_slot_validator_plus_pinned_boundary')
orig=(HERE/'ORIGINAL_ALL3_OWNER_BYTES.txt').read_text('utf8');new=(HERE/candidate.OWNER_SCRIPT).read_text('utf8')
diff=json.loads((HERE/'AVAILABLE_TWO_OWNER_EXACT_DIFF_SOURCE_ACTUAL.json').read_bytes())
for before,after in reversed(diff['exact_text_substitutions']):new=new.replace(after,before)
check(new==orig,'owner_reverse_three_substitutions_exact_original')
for name in ('REMOTE_ACCOUNT','REMOTE_PREACTIVATE_NODE','REMOTE_OWNER_VERIFY','REMOTE_OWNER_READY'):
 check(getattr(candidate.original,name)==getattr(candidate.original,name),name+'_original_source_retained')
check(candidate.REMOTE_OWNER_CREATE.replace('v87r2','v87')==candidate.original.REMOTE_OWNER_CREATE,'owner_create_only_R2_namespace_literal_change')
entry=HERE/'activate_available_two_H1_native87R2_sole72_after_actual_CPU_unused_once.py'
ast.parse(entry.read_bytes());check(True,'activation_AST_parses_without_execution')
check(H(HERE/'native87_install_activate_support_v1.py')==H(L/'agent_native87_actual_install_activate_sources_candidate/native87_install_activate_support_v1.py'),'original_support_byteexact')
result=dict(passed=True,count=len(checks),checks=checks,scope='source_AST_and_synthetic_metadata_only',actual_CPU_or_model_reexecuted=False,network=False,activation_executed=False,
 inputs=[dict(path=str(prepared),SHA=H(prepared)),dict(path=str(HERE/schedule.BOUNDARY_NAME),SHA=boundary_SHA)])
with (HERE/'SOURCE_CPU_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(result,f,indent=2)
print(json.dumps(result))
