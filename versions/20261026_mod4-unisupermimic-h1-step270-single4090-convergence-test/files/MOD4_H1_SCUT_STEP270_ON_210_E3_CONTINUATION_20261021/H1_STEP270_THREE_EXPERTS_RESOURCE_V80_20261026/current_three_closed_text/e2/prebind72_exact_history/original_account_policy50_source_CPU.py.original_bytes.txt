
from pathlib import Path
import hashlib,json
H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def load(spec,B):
 B=Path(B);read=lambda p:json.loads(Path(p).read_bytes());assert spec['key']=='e2' and spec['execution_backend']=='target72' and spec['cross_host_qualified_source']
 auth=read(B/'CROSS_HOST_QUALIFIED_SOURCE_AUTH_ACTUAL.json');proof=read(B/'SOURCE_ORIGIN_210_C52/CLOSED_MODELS_COST_CPU_ACTUAL.json');model=proof['models']['e2'];cpu=read(B/'TARGET_TWO50_SOURCE_AND_CONTROLLERS_INSTALLED_CPU_ADMITTED_ACTUAL.json');m=read(B/'THREE_SLOT_COMPLETE_MANIFEST_V1.json');prior=read(B/'QUALIFIED_RUNTIME_BASE_MANIFEST.json')
 assert auth['approved'] and auth['kind']=='human_three_GPU_existing_E2_cross_host_continuation' and auth['source_SHA']==spec['source_SHA']==model['final']['SHA'] and model['Adam']==spec['source_Adamstep']==839920
 assert proof['passed'] and proof['all_owner_nodes_children_actual_out'] and proof['original_canonical_cost_settled'] and proof['all_original_private_shared_locks_free'] and model['actual_cost']['duration_bound_passed']
 assert model['counts']==[175,98] and len(model['all17_changed']['actor_state_dict'])==9 and 'distribution.std_param' in model['all17_changed']['actor_state_dict'] and len(model['all17_changed']['critic_state_dict'])==8
 terminal=read(B/'SOURCE_ORIGIN_210_C52/NODE_TERMINAL_ACTUAL.json')['row'];exit=read(B/'SOURCE_ORIGIN_210_C52/NODE_EXIT_ACTUAL.json');assert terminal['returncode']==0 and not terminal['original_error'] and not terminal['errors'] and terminal['terminal_all_own_children_waited'] and terminal['final']['passed'] and terminal['final']['final']['SHA']==spec['source_SHA'] and exit['actual_all_own_children_waited'] and exit['validation_fcntl_released_if_acquired']
 clock=read(B/'SOURCE_ORIGIN_210_C52/POLICY50_ACTUAL_CLOCK_AND_INHERITANCE.json');assert clock['policy_hz']==spec['policy_hz']==spec['source_policy_hz']==50 and clock['physics_dt_s']==.0025 and clock['decimation']==8
 before={r['relative']:r for r in prior['files']};after={r['relative']:r for r in m['files']}
 protected=lambda rows:{k:v for k,v in rows.items() if k.startswith(('job0/runtime/','job0/assets/','lib/'))}
 a=protected(before);b=protected(after);assert set(a)==set(b)
 for rel,row in a.items():assert b[rel]['bytes']==row['bytes'] and b[rel]['SHA']==row['SHA'],rel
 assert H(B/'native_admission_worker.py')==before['native_admission_worker.py']['SHA'] and H(B/'target_two50_source_sdk_cpu_review.py')==before['target_two50_source_sdk_cpu_review.py']['SHA']
 approved=read(B/'THREE_GPU_CONTROLLER_SOURCE_AUTH_ACTUAL.json')
 for name,row in approved['new_sources'].items():assert H(B/name)==row['SHA']
 assert cpu['passed_CPU_only'] and cpu['source_SHA']==spec['source_SHA'] and cpu['source_schema_counts']==[175,98] and cpu['all17Adam']==839920 and cpu['manifest_SHA']==H(B/'THREE_SLOT_COMPLETE_MANIFEST_V1.json')
 assert cpu['actual_SDK_math']['SHA']==m['expected_actual_SDK_math_SHA'] and len(cpu['actual_RSL_sources'])==2
 v=dict(kind='closed_cross_host_policy50_production',key='e2',passed=True,source_SHA=spec['source_SHA'],GPU_UUID=spec['GPU_UUID'],execution_backend='target72',all_source_model_runtime_finite_CPU=True,old_complete_production_checkpoint_actual_EXIT0=True,explicit_policy_clock_50Hz_admitted=True,explicit_cross_host_source_CPU_admitted=True,same_clock_closed_production=True,source_cost_original_account_ready=True,source_account_reconciliation_receipt_SHA=H(B/'SOURCE_ORIGIN_210_C52/CLOSED_MODELS_COST_CPU_ACTUAL.json'),original_clip6_query_COM_closure_mimic_hardware_savedstop_guards_retained=True,existing_same_source_native_physics_evidence_reused=True,new_target_GPU_PPO_not_claimed=True,not_skill_graduation=True)
 return dict(value=v,SHA=hashlib.sha256(json.dumps(v,indent=2).encode()).hexdigest(),actual_CPU_waited_EXIT0=True)
