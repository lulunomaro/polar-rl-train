"""CPU regression of the actual overwrite and its repair; prepare one missing-only reader."""
from pathlib import Path
import ast,hashlib,json,shutil,tempfile,time
B=Path(__file__).resolve().parent;R=B/'reports';F=B/'future_partial_hour_repair_templates'
H=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
old=B/'controllers/three_real_gpu_resource_v1.py';fixed=F/'three_real_gpu_resource_shared_user_v2.py'
def policy(source):
 tree=ast.parse(source.read_text('utf8'));return next(n.test for n in ast.walk(tree) if isinstance(n,ast.Assert) and 'compute.splitlines' in ast.unparse(n.test))
oldtest=policy(old);newtest=policy(fixed)
compute='GPU-16828f91-2b45-b646-8dc0-9481138e2842, 66633, 8526\n'
cases=[]
for key,flag,occupied,expected in [('h1',True,True,True),('h1',False,True,False),('recovery',True,True,False),('h1',True,False,True)]:
 spec=dict(key=key,GPU_UUID='GPU-16828f91-2b45-b646-8dc0-9481138e2842',human_explicit_GPU_sharing=flag);scope=dict(spec=spec,compute=compute if occupied else '')
 actual=eval(compile(ast.Expression(newtest),'<actual-repaired-admission-assert>','eval'),scope);assert actual==expected;cases.append(dict(key=key,explicit=flag,occupied=occupied,admitted=actual))
assert not eval(compile(ast.Expression(oldtest),'<actual-overwritten-exclusive-assert>','eval'),dict(spec=dict(key='h1',GPU_UUID='GPU-16828f91-2b45-b646-8dc0-9481138e2842',human_explicit_GPU_sharing=True),compute=compute))
with tempfile.TemporaryDirectory(prefix='mod4_h1_inheritance_regression_') as td:
 q=Path(td)/'three_real_gpu_resource_v1.py';shutil.copy2(fixed,q);shutil.copy2(old,q);assert H(q)==H(old);shutil.copy2(fixed,q);assert H(q)==H(fixed)
prep=(F/'prepare_next_three_closed_sources_one_hour_CPU_once.py').read_text('utf8');assert prep.index("for c in C.glob('*.py')")<prep.index("resource=B/'three_real_gpu_resource_shared_user_v2.py'")<prep.index('m=dict(oldm,source_SHA=')
for guard in ("int(line.split(',')[-1])>7000",'available>8*1024**3','free>25*1024**3','LOCK_EX|fcntl.LOCK_NB','previous_failed_preGO_runtime_root'):assert guard in fixed.read_text('utf8')
for name in ('three_slot_finite_owner_v1.py','three_slot_finite_node_v1.py','three_slot_common_v1.py'):assert (B/'controllers'/name).read_bytes()==(B.parent/'MOD4_SCUT_FUDAN_TENTH_HOUR_20261019/controllers'/name).read_bytes()
with (R/'H1_RESOURCE_COPY_ORDER_AND_SHARING_POLICY_REGRESSION_CPU_ACTUAL.json').open('x',encoding='utf8') as stream:json.dump(dict(epoch=time.time(),passed=True,actual_old_assert_reproduced_rejecting_authorized_H1_peer=True,controller_overwrite_reproduced_on_temporary_copy=True,corrected_override_after_controller_copy_before_manifest=True,regression_cases=cases,original_memory_disk_RAM_locks_and_live_controllers_unchanged=True,old_resource_SHA=H(old),prepared_repair_resource_SHA=H(fixed),no_remote_GPU_case_native_or_account_write=True),stream,indent=2)
s=(B/'collect_next_three_actual_learning_metadata_finite_once.py').read_text('utf8')
mapping={
 'THREE_REAL_LEARNING_METADATA_FINITE_COLLECTOR_STARTED_ACTUAL.json':'TWO_HEALTHY_LEARNING_METADATA_V2_COLLECTOR_STARTED_ACTUAL.json',
 'LEARNING_METADATA_OBSERVATIONS_JOURNAL.txt':'TWO_HEALTHY_LEARNING_METADATA_V2_OBSERVATIONS_JOURNAL.txt',
 'THREE_REAL_LEARNING_TARGET72_NATIVE_OR_PRODUCTION_BOUND_METADATA_ACTUAL.json':'TWO_HEALTHY_LEARNING_TARGET72_METADATA_V2_ACTUAL.json',
 'THREE_REAL_LEARNING_SOURCE210_METADATA_ACTUAL.json':'TWO_HEALTHY_LEARNING_SOURCE210_METADATA_V2_ACTUAL.json',
 'THREE_REAL_LEARNING_ONE_ORIGINAL_OWNER_ACTUAL_CURRENT.json':'TWO_HEALTHY_LEARNING_ORIGINAL_OWNER_METADATA_V2_ACTUAL.json',
 'THREE_REAL_GPU_ACTUAL_PPO_LEARNING_METADATA_VERIFIED_OR_PENDING.json':'TWO_HEALTHY_EXPERTS_PPO_AND_H1_PREGO_FAILURE_METADATA_V2_ACTUAL.json',
 'THREE_REAL_LEARNING_FINITE_COLLECTOR_ORIGINAL_ERROR_':'TWO_HEALTHY_LEARNING_METADATA_V2_ORIGINAL_ERROR_'}
for x,y in mapping.items():s=s.replace(x,y)
s=s.replace("for k in ('h1','recovery')","for k in ('recovery',)")
s=s.replace("experts={**target['experts'],**source['experts']};evidence={}","original_h1=json.loads((d.R/'THREE_REAL_LEARNING_TARGET72_NATIVE_OR_PRODUCTION_BOUND_METADATA_ACTUAL.json').read_bytes())['experts']['h1'];experts={**target['experts'],**source['experts'],'h1':original_h1};evidence={}")
s=s.replace('three_actual_PPO_learning_verified=all3,experts=evidence','three_actual_PPO_learning_verified=all3,two_healthy_actual_PPO_learning_verified=all(all(evidence[k][f] for f in (\'actual_GO\',\'actual_production_log_positive\',\'actual_matching_GPU_worker_compute\')) for k in (\'e2\',\'recovery\')),H1_original_preGO_failure_retained_no_replay=True,H1_row_is_retained_original_error_snapshot_not_new_liveness=True,experts=evidence')
s=s.replace("print(json.dumps(dict(all_three_actual_learning=all3,experts=evidence))","print(json.dumps(dict(all_three_actual_learning=all3,two_healthy_actual_learning=all(all(evidence[k][f] for f in ('actual_GO','actual_production_log_positive','actual_matching_GPU_worker_compute')) for k in ('e2','recovery')),H1_preGO_failure_retained=True,experts=evidence))")
ast.parse(s)
with (B/'collect_two_healthy_actual_learning_metadata_V2_missing_only_once.py').open('x',encoding='utf8',newline='\n') as stream:stream.write(s)
print(json.dumps(dict(repair_CPU_regression_passed=True,missing_two_healthy_metadata_reader_prepared=True)))
