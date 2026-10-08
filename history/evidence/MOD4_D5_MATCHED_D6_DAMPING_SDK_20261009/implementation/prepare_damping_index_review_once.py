"""Separate proof reader for PhysX CPU tensors; preserve failed immutable80 jobs."""
from pathlib import Path
import hashlib,json
D=Path(__file__).resolve().parent;R=D/'reports'
assert not (R/'D6_INDEX_REVIEW_PREPARED.json').exists()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
proof=(D/'gas_damping_actual_sdk_proof.py').read_text(encoding='utf8')
old="actual[other],self.before['damping'][other]";assert proof.count(old)==1
proof=proof.replace(old,"actual[other.cpu()],self.before['damping'][other.cpu()]")
dest=D/'gas_damping_sdk_index_review.py';assert not dest.exists();dest.write_text(proof,encoding='utf8')
worker=(D/'eval_worker_atomic_retry_review.py').read_text(encoding='utf8')
worker=worker.replace('ATOMIC_RETRY','GAS_DAMPING_REVIEW')
needle="RETIRED=(";assert worker.count(needle)==1
worker=worker.replace(needle,"RETIRED=('clk2500-closure-episode-d3-80-d6-gas-sdk-off','clk2500-closure-episode-d3-80-d6-gas-sdk-on',")
dest=D/'eval_worker_gas_damping_review.py';assert not dest.exists();dest.write_text(worker,encoding='utf8')
admit=(D/'admit_atomic_retry_worker_once.py').read_text(encoding='utf8')
admit=admit.replace('ATOMIC_RETRY','GAS_DAMPING_REVIEW').replace('admit_atomic_retry_worker_once.py','admit_gas_damping_review_once.py')
admit=admit.replace('eval_worker_spring_audit_review.py','eval_worker_atomic_retry_review.py')
admit=admit.replace('ae2ce15e9853bac91662f4795dbb55d39abfdbbde59725ba21f0df62caea6aaf',sha(D/'eval_worker_atomic_retry_review.py'))
old="fault=read(D/'SPRING_AUDIT_WORKER_ATTENTION.json');assert 'PermissionError: [WinError 5]' in fault['error'] and 'SPRING_AUDIT_WORKER_STATE.json.partial' in fault['error']"
assert admit.count(old)==1;admit=admit.replace(old,"fault=read(D/'ATOMIC_RETRY_WORKER_ATTENTION.json');assert 'Frozen evaluation failed' in fault['error']\n    failed=read(D/'jobs/clk2500-closure-episode-d3-80-d6-gas-sdk-off/result.json');assert failed['phase']=='retained_failed'\n    log=(D/'jobs/clk2500-closure-episode-d3-80-d6-gas-sdk-off/probe.log').read_text(encoding='utf8',errors='replace');assert 'indices should be either on cpu' in log")
admit=admit.replace("old='MOD4_AsyncFrozenEvaluation_v15_spring_audit_review'","old='MOD4_AsyncFrozenEvaluation_v15_atomic_retry_review'")
admit=admit.replace("$name='MOD4_AsyncFrozenEvaluation_v15_atomic_retry_review'","$name='MOD4_AsyncFrozenEvaluation_v15_gas_damping_review'")
admit=admit.replace('\\eval_worker_atomic_retry_review.py','\\eval_worker_gas_damping_review.py')
admit=admit.replace('transient_windows_share_conflicts_bounded_retry=True','transient_windows_share_conflicts_bounded_retry=True,reviewed_only_PhysX_CPU_tensor_index_reader=True,old80_on_never_ran_not_passed=True')
dest=D/'admit_gas_damping_review_once.py';assert not dest.exists();dest.write_text(admit,encoding='utf8')
publisher=(D/'publish_actual_damping_sdk_once.py').read_text(encoding='utf8')
publisher=publisher.replace('D6_ACTUAL_DAMPING_SDK_PUBLISHED','D6_INDEX_REVIEW_SDK_PUBLISHED')
publisher=publisher.replace('gas_damping_actual_sdk_proof.py','gas_damping_sdk_index_review.py').replace('from gas_damping_actual_sdk_proof import','from gas_damping_sdk_index_review import')
publisher=publisher.replace('80-d6-gas-sdk','81-d6-gas-sdk-index').replace('d6-gas-damping-actual-sdk-','d6-gas-damping-index-reviewed-sdk-')
dest=D/'publish_damping_index_review_once.py';assert not dest.exists();dest.write_text(publisher,encoding='utf8')
deploy=(D/'deploy_atomic_retry_worker_once.py').read_text(encoding='utf8')
deploy=deploy.replace('ATOMIC_RETRY','GAS_DAMPING_REVIEW').replace("('resilient_json_atomic.py','test_atomic_sharing_retry.py','eval_worker_atomic_retry_review.py','admit_atomic_retry_worker_once.py')","('eval_worker_gas_damping_review.py','admit_gas_damping_review_once.py')")
deploy=deploy.replace("('test_atomic_sharing_retry.py','admit_atomic_retry_worker_once.py')","('admit_gas_damping_review_once.py',)")
dest=D/'deploy_gas_damping_review_once.py';assert not dest.exists();dest.write_text(deploy,encoding='utf8')
names=('gas_damping_sdk_index_review.py','eval_worker_gas_damping_review.py','admit_gas_damping_review_once.py','publish_damping_index_review_once.py','deploy_gas_damping_review_once.py')
for name in names:compile((D/name).read_text(encoding='utf8'),name,'exec')
(R/'D6_INDEX_REVIEW_PREPARED.json').write_text(json.dumps(dict(failed80_off_preserved=True,old80_on_not_started=True,adapter_and_D5_production_unchanged=True,files={n:sha(D/n) for n in names}),indent=2),encoding='utf8')
print(json.dumps(dict(new_files=list(names),only_SDK_CPU_PhysX_index_reader_repair=True)))
