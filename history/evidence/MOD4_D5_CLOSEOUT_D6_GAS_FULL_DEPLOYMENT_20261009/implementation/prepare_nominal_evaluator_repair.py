"""New evaluator authority excludes only six reviewed incompatible nominal jobs."""
from pathlib import Path
import json,ast
D=Path(__file__).resolve().parent;P=D.parent/'MOD4_D6_DAMPING_SOURCE_PREPARE_20261008'
retired=tuple('clk2500-closure-episode-d3-95-d5-retention-'+str(seed)+'-nominal-'+kind for seed in (20261002,20261003) for kind in ('flat','spin','world'))
t=(P/'eval_worker_gas_damping_review.py').read_text();t=t.replace('GAS_DAMPING_REVIEW','NOMINAL_SCOPE_REVIEW')
t=t.replace("\ndef main():","\nRETIRED=RETIRED+"+repr(retired)+"\n\ndef main():")
ast.parse(t);(D/'eval_worker_nominal_scope_review.py').write_text(t,encoding='utf8')
t=(P/'admit_gas_damping_review_once.py').read_text()
start=t.index("    assert hashlib.sha256((D/'eval_worker_closure2500.py')")
end=t.index('    actual=ps(',start)
t=t[:start]+"    assert hashlib.sha256((D/'eval_worker_closure2500.py').read_bytes()).hexdigest()=='0b7e7a700a952dda0a08edc7587406f39880d10843ee4ef49132fe979e6268f1'\n    fault=read(D/'GAS_DAMPING_REVIEW_WORKER_ATTENTION.json');assert 'Frozen evaluation failed' in fault['error']\n    failed=read(D/'jobs/clk2500-closure-episode-d3-95-d5-retention-20261002-nominal-flat/result.json');assert failed['phase']=='retained_failed'\n    log=(D/'jobs/clk2500-closure-episode-d3-95-d5-retention-20261002-nominal-flat/probe.log').read_text(encoding='utf8',errors='replace');assert '_mild_dr' in log\n"+t[end:]
t=t.replace('admit_gas_damping_review_once.py','admit_nominal_scope_review_once.py')
t=t.replace("old='MOD4_AsyncFrozenEvaluation_v15_atomic_retry_review'","old='MOD4_AsyncFrozenEvaluation_v15_gas_damping_review'")
t=t.replace('GAS_DAMPING_REVIEW','NOMINAL_SCOPE_REVIEW')
t=t.replace("fault=read(D/'NOMINAL_SCOPE_REVIEW_WORKER_ATTENTION.json')","fault=read(D/'GAS_DAMPING_REVIEW_WORKER_ATTENTION.json')")
t=t.replace('MOD4_AsyncFrozenEvaluation_v15_gas_damping_review','MOD4_AsyncFrozenEvaluation_v15_nominal_scope_review')
t=t.replace("old='MOD4_AsyncFrozenEvaluation_v15_nominal_scope_review'","old='MOD4_AsyncFrozenEvaluation_v15_gas_damping_review'")
t=t.replace('eval_worker_gas_damping_review.py','eval_worker_nominal_scope_review.py')
t=t.replace('reviewed_only_PhysX_CPU_tensor_index_reader=True','reviewed_only_nominal_D0_interface_dependency=True').replace('old80_on_never_ran_not_passed=True','invalid_nominal_jobs_retained_not_passed=True')
ast.parse(t);(D/'admit_nominal_scope_review_once.py').write_text(t,encoding='utf8')
t=(P/'deploy_gas_damping_review_once.py').read_text().replace('GAS_DAMPING_REVIEW','NOMINAL_SCOPE_REVIEW').replace('eval_worker_gas_damping_review.py','eval_worker_nominal_scope_review.py').replace('admit_gas_damping_review_once.py','admit_nominal_scope_review_once.py')
ast.parse(t);(D/'deploy_nominal_scope_review_once.py').write_text(t,encoding='utf8')
print(json.dumps(dict(prepared=True,retired_invalid_nominal_jobs=retired,no_GPU=True)))
