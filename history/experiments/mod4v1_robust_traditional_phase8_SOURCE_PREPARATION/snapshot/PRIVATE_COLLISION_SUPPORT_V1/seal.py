from pathlib import Path
import hashlib,json
D=Path(__file__).resolve().parent
result=json.loads((D/'validation001/RESULT.json').read_text(encoding='utf-8'))
plan=json.loads((D/'PLAN.json').read_text(encoding='utf-8'))
assert result['failures']==0 and result['checks']>0
assert result['counters']=={'model_compiles':1,'explicit_mj_forward':5,'integrator_entries':0}
assert result['max_support_oracle_error_m']<=plan['absolute_oracle_budget_m']
assert result['R62_scores_changed'] is False and result['old_raw_reads']==0
names=['PLAN.json','support.py','validate_once.py','README.md','seal.py','VALIDATION_001.log',
       'validation001/SOURCE_PREEXEC.json','validation001/RESULT.json',
       'validation001/REAL_GEOMETRIC_SNAPSHOTS.json']
rows=[]
for name in names:
 p=D/name
 assert p.is_file()
 rows.append({'path':name,'bytes':p.stat().st_size,'SHA':hashlib.sha256(p.read_bytes()).hexdigest()})
obj={'status':'VALIDATED_PRIVATE_GEOMETRY_KERNEL_NOT_RUNTIME_INTEGRATED','files':rows,
     'external_source_evidence_from_validation_not_rehashed':result['sources_before_after'][3:],
     'controller_inputs_or_old_scores_changed':False,'new_episodes':0,'PH8pending':True}
with (D/'INDEX.json').open('x',encoding='utf-8') as f:json.dump(obj,f,indent=2,allow_nan=False)
receipt={'status':obj['status'],'INDEX_SHA':hashlib.sha256((D/'INDEX.json').read_bytes()).hexdigest(),
         'small_indexed_files':len(rows),'checks':result['checks'],'failures':0,
         'explicit_new_model_and_forward_counts':result['counters'],
         'new_runtime_writer_or_physics_validation':False,'R62_scores_changed':False,'PH8pending':True}
with (D/'RECEIPT.json').open('x',encoding='utf-8') as f:json.dump(receipt,f,indent=2,allow_nan=False)
print(json.dumps(receipt))
