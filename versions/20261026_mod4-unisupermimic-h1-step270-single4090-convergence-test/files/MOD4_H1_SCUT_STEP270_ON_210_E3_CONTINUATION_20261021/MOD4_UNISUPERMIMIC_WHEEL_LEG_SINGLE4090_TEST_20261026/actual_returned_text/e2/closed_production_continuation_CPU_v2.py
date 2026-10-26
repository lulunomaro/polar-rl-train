"""Actual installed CPU admission for the explicitly new finite method, not E2 production."""
from pathlib import Path
import hashlib,json,os,subprocess
def load(spec,B):
 B=Path(B);assert spec['finite_method_test'] and spec['key']=='e2' and spec['GPU_UUID']=='GPU-16828f91-2b45-b646-8dc0-9481138e2842'
 source=json.loads((B/'reports/ACTUAL_MOD4_OFFLINE_TRANSITION_TEST_INPUT_PRODUCER_INDEX.json').read_bytes());assert spec['source_SHA']==source['SHA']
 proof=json.loads((B/'CURRENT_CLOSED80_ORIGINAL_MODELS_AND_COST_CPU_ACTUAL.json').read_bytes());assert proof['passed'] and proof['original_canonical_cost_settled'] and proof['all_owner_nodes_children_actual_out'] and all(v['actual_cost']['duration_bound_passed'] for v in proof['models'].values())
 env=dict(os.environ,CUDA_VISIBLE_DEVICES='',PYTHONDONTWRITEBYTECODE='1');p=subprocess.run([spec['python'],'-B','-X','utf8',str(B/'test_mod4_supermimic_native30_action6_CPU_v2.py'),'--installed'],cwd=B,env=env,capture_output=True,text=True,timeout=90)
 (B/'reports/ACTUAL_INSTALLED_CPU_STDOUT.txt').write_text(p.stdout,'utf8');(B/'reports/ACTUAL_INSTALLED_CPU_STDERR.txt').write_text(p.stderr,'utf8');assert p.returncode==0
 cpu=json.loads((B/'reports/ACTUAL_INSTALLED_NATIVE30_ACTION6_CPU_ADMITTED.json').read_bytes());assert cpu['passed'] and not cpu['CUDA_initialized'] and cpu['source_SHA']==spec['source_SHA']
 v=dict(passed=True,kind='UNISUPERMIMIC_MOD4_NATIVE30_ACTION6_FINITE_METHOD_TEST',source_SHA=spec['source_SHA'],GPU_UUID=spec['GPU_UUID'],upstream_revision='faf7818e8abac3ec6abb8f00e6e904d3577f800b',actual_installed_CPU_passed=True,native_joint_states=30,actions=6,source80_actual_cost_models_allout_passed=True,not_production_E2_source_or_skill_qualification=True)
 return dict(value=v,SHA=hashlib.sha256(json.dumps(v,indent=2).encode()).hexdigest(),actual_CPU_waited_EXIT0=True)
