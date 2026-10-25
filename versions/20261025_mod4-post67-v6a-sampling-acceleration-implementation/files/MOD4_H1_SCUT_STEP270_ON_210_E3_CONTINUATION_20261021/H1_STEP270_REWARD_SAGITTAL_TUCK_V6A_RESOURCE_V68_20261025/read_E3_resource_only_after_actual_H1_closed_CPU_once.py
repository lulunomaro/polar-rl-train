from pathlib import Path
import importlib.util,json,sys,time,traceback
B=Path(__file__).resolve().parent;W=B.parent.parent;R=B/'reports';N=Path(__file__).resolve().parent;B=N.parent/'H1_STEP270_REWARD_PATH_V1_20261022';R=N/'reports'
sys.path.insert(0,str(W/'MOD4_TWO_LINUX_POLICY50_COHORT_52_20261021'));import deploy_two50_reconciled_original_writer_once as d
def put(n,v):
 with (R/n).open('x',encoding='utf8') as f:json.dump(v,f,indent=2)
CODE=r'''
from pathlib import Path
import json,psutil,shutil,subprocess,time
q=v['q'];s=q['specs']['recovery'];base=Path('/home/lc01/Zonglin Li/zonglin2')
compute=subprocess.check_output(['nvidia-smi','--query-compute-apps=gpu_uuid,pid,used_gpu_memory','--format=csv,noheader,nounits'],text=True)
own_gpu_rows=[x for x in compute.splitlines() if s['GPU_UUID'] in x]
line=next(x for x in subprocess.check_output(['nvidia-smi','--query-gpu=uuid,memory.free','--format=csv,noheader,nounits'],text=True).splitlines() if s['GPU_UUID'] in x)
ram=psutil.virtual_memory().available;free=shutil.disk_usage(base).free
print(json.dumps(dict(epoch=time.time(),RAM_available_bytes=ram,RAM8_passed=ram>8*1024**3,durable_free_bytes=free,disk25_passed=free>25*1024**3,expected_GPU_UUID=s['GPU_UUID'],GPU_free_MiB=int(line.split(',')[-1]),GPU7000_passed=int(line.split(',')[-1])>7000,expected_GPU_empty=not own_gpu_rows,allocation_count_on_expected_GPU=len(own_gpu_rows),unknown_peer_identity_not_queried=True,previous_recovery_root_exists=Path(q['roots']['recovery']).exists(),no_mutation_GPU_evaluation_model_or_budget_write=True)))
'''
try:
 proof=json.loads((N.parent/'H1_STEP270_REWARD_AIRBORNE_FEASIBLE_V5_RESOURCE_V67_20261025/reports/PAIR_COMPLETE_MODELS_AND_ORIGINAL_COST_CPU_ACTUAL.json').read_bytes());assert proof['passed'] and proof['original_canonical_cost_settled'] and proof['all_owner_nodes_children_actual_out']
 closure=json.loads((N.parent/'MOD4_MIXED_PRECISION_MISSING_HALF_RSL_V4_AFTER67_20261025/reports/BENCHMARK_TEXT_CANONICAL_AND_ORIGINAL_COST_RETURNED_ACTUAL.json').read_bytes());assert closure['owner_node_workers_all_actual_out'] and closure['original_canonical_cost_settled']
 q=json.loads((N.parent/'H1_STEP270_REWARD_AIRBORNE_FEASIBLE_V5_RESOURCE_V67_20261025/reports/TWO50_LATEST_CLOSED_SOURCES_PAYLOADS_CPU_PREPARED_ACTUAL.json').read_bytes())
 spec=importlib.util.spec_from_file_location('memory',W/'MOD4_BUDGET_ADD100H_EIGHTH_20261021/run_authorized_cohort50_with_existing_hidden_stdin_memory.py');memory=importlib.util.module_from_spec(spec);spec.loader.exec_module(memory);secret=memory.recover();c=d.connect72(secret);secret=None
 try:v=d.code(c,d.PY72,CODE,dict(q=q),timeout=45)
 finally:c.close()
 put('NEXT_E3_BOUNDARY_RESOURCE_COMPONENTS_ACTUAL.json',v);print(json.dumps(v))
except BaseException:
 put('NEXT_E3_BOUNDARY_RESOURCE_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc()));raise
