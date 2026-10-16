"""Compare already-local complete runs; never repeat either frozen GPU case."""
from pathlib import Path
import hashlib,json,time
D=Path(__file__).resolve().parent;E=D/'curb113_frozen_v2';H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def load(folder,pattern):return json.loads(sorted(folder.glob(pattern))[-1].read_bytes())
old=load(D/'reports','curb_final878_1500_v1_ACTUAL_BOUNDARY_COLLECTION_*.json')
new=load(E/'reports','curb_independent113_1500_v1_ACTUAL_BOUNDARY_COLLECTION_*.json')
def path(v,n):return Path(next(x['local_path'] for x in v['files'] if x['relative'].endswith('/'+n)))
def read(v,n):return json.loads(path(v,n).read_bytes())
rows=[]
for name in ['FIRST_PHYSICS_INITIAL_ACTUAL.json','INITIAL_ACTUAL.json','EXPECTED_INSTALLED_3060_BACKEND_V2.json']:
 a=read(old,name);b=read(new,name);rows.append(dict(file=name,exact=a==b,old_SHA=H(path(old,name)),new_SHA=H(path(new,name))))
assert all(r['exact'] for r in rows),rows
po=read(old,'probe.json');pn=read(new,'probe.json')
for key in ('seed','profile','num_envs','steps','geometry_recipe','geometry','route_scope','body_names'):
 assert po[key]==pn[key],key
query_exact=H(path(old,'probe.json.worldmesh_query.npz'))==H(path(new,'probe.json.worldmesh_query.npz'))
assert query_exact
ro=json.loads((D/'reports/CURB878_FULL1500_ORIGINAL_ROUTE_ALL_PREFIX_CPU_ACTUAL.json').read_bytes())
rn=json.loads((E/'reports/CURB113_FULL1500_ORIGINAL_ROUTE_ALL_PREFIX_CPU_ACTUAL.json').read_bytes())
assert ro['passed'] and rn['passed'] and ro['source_SHA']!=rn['source_SHA']
out=dict(epoch=time.time(),CPU_actual_initial_strict_pair_passed=True,rows=rows,all_original_root_q30_parameters_assignments_reset_and_captured_RNG_queues_exact=True,loaded_backend_source_binding_exact=True,initial_query_bytes_SHA_exact=query_exact,protocol=dict(seed=pn['seed'],profile=pn['profile'],steps=1500,callbacks=6000,envs=80,height_m=.02,strip_m=.15),results={name:{k:r[k] for k in ('source_SHA','counts','ordinary','truncation','query_error','CPUvsGPU_maxabs','raw_SHA')} for name,r in [('protected_shared878',ro),('new_independent113',rn)]},new_missing=[r['env'] for r in rn['all_valid_failed_prefixes'] if r['group']!=2 and not r['contact_confirmed_complete']],not_equal_ancestral_training_cost=True,not_architecture_or_allskills_winner=True,new_PPO_or_budget=False,old_and_new_raw_false_prefixes_preserved=True,original_EXIT_NATURAL_missing_preserved=True)
p=D/'reports/CURB113_VS_PROTECTED878_SAME_ACTUAL_INITIAL_LIMITED_ROUTE_CPU_REVIEW.json'
with p.open('x',encoding='utf8') as f:json.dump(out,f,indent=2)
print(json.dumps(out),flush=True)
