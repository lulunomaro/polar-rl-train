from pathlib import Path
import ast,hashlib,json,time
N=Path(__file__).resolve().parent;T=N.parent
s=(T/'MOD4_H1_FLAT20_NATIVE_RESOURCE_V100_20261028/collect_actual100_original_early_failure_cost_allout_fulltexts_once.py').read_text('utf8')
s=s.replace('TWO100_TARGET20_TWO_NATIVE_ORIGINAL_OWNER_SOURCE_V1','TWO106_FUDAN270_20S_ACTUAL_CPU_BOUND_ORIGINAL_OWNER_SOURCE_V1').replace('TWO100_TWO_NATIVE20_FIRST_POLICY_OBSERVER_SOURCE_V1','TWO106_FUDAN270_20S_FIRST_CLOSING_INITIAL_CPU_SOURCE_V1').replace('TWO100','TWO106').replace('ACTUAL100','ACTUAL106').replace('original100','original106')
ast.parse(s);p=N/'collect_actual106_original_early_failure_cost_allout_fulltexts_UNUSED_once.py'
with p.open('x',encoding='utf8') as f:f.write(s)
with (N/'reports/FROZEN_UNUSED_ACTUAL106_EARLY_FAILURE_READER_INDEX.json').open('x',encoding='utf8') as f:json.dump(dict(epoch=time.time(),frozen=True,unused=True,path=str(p),SHA=hashlib.sha256(p.read_bytes()).hexdigest(),original850_1140_bounds=True,both_original_error_firstreader_and_original_natural_exit_required=True,no_normal900_guard_relaxation=True),f,indent=2)
