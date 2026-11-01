from pathlib import Path
import ast,hashlib,json,time
N=Path(__file__).resolve().parent;T=N.parent;S=N/'source';R=N/'reports';S.mkdir(exist_ok=False);R.mkdir(exist_ok=False)
def put(p,x):
 with p.open('x',encoding='utf8')as f:json.dump(x,f,indent=2,allow_nan=False)
P=T/'OWN_MOD4_FULLSTATE_DEPTH_COLLECTOR_V267_20261101';result=json.loads((P/'reports/ROOT267_NEW240_MEAN_REGRESSION_PARENT_OR_ORIGINAL_ERROR_RETURNED_ACTUAL.json').read_bytes());assert result['passed_execution'];actual=result['original_parent']['result'];assert actual['controls']==64 and actual['terminated']==actual['truncated']==0 and actual['actor_frozen_exact']
b=next(x for x in result['full_UTF8']if x['path'].endswith('/ACTUAL267_FULL_MEASURED_SCHEMA_BINDING.json'));binding=json.loads(b['UTF8']);assert binding['passed']and binding['state224_LAYOUT']['BODY_contact31x3_div400']==[131,224]
task=dict(kind='NEW269_NECESSARY_FIRST_NEW267_MEASURED224_LITERAL_ABI_CPU',purpose='Validate actual224->originalFudan measured frame and64 reward/memory rows before realWM use; no statistics/Git reread purpose.',producer=actual['producer'],actual_binding=binding,binding_witness_SHA=b['SHA'],models_legacy_raw_reads=0)
put(N/'TASK269_LOCAL_FROZEN.json',task)
C=T/'DEPTH_SUPERMIMIC_MEASURED224_WM50_SOURCE_FROM255_V268_20261101';F=T/'MODEL2050_LITERAL_JUMP_400N50_ADAPT_V240_20261101/package';K=T/'MOD4_H1_MATLAB_REFERENCE_IMAGINATION_TRACKING_RESOURCE_V165_20261030/payloads_v2/seed27/source/supermimic_wheel_leg_v3'
for p,relative in[(C/'measured_state224_v268.py','code/measured_state224_v268.py'),(C/'predicted_literal_frame268.py','code/predicted_literal_frame268.py')]+[(F/f,'code/'+f)for f in('jump194_boundary.py','literal_original_methods.py','literal_original_config.py')]+[(K/f,'native/'+f)for f in('geometry.py','networks.py','augmented_wheel_leg_world_model_v1.py')]:
 q=S/relative;q.parent.mkdir(exist_ok=True);q.write_bytes(p.read_bytes())
(S/'review269_NEW267_state_and_literal_frame_CPU_once.py').write_bytes((N/'review269_NEW267_state_and_literal_frame_CPU_once.py').read_bytes())
files=sorted(S.rglob('*.py'))+[N/'TASK269_LOCAL_FROZEN.json',N/'run_ROOT269_new267_measured_CPU_once.py',Path(__file__).resolve(),N/'review269_NEW267_state_and_literal_frame_CPU_once.py']
for p in files:
 if p.suffix=='.py':ast.parse(p.read_text('utf8'),filename=str(p))
report=R/'ROOT269_SOURCE_AND_NEW_ACTUAL_PURPOSE_FROZEN.json';put(report,dict(passed=True,epoch=time.time(),source_AST=sum(p.suffix=='.py'for p in files),source_kind='New ABI integration, no prior fixture or raw read',source_pair_count=64,first_new267_NPZ_byte_open_max=1,np_load_max=1,each_member_max1=True,source_component_PT_read_max=0,models_GPU_App_optimizer_account=0,actual_body_motor_binding_SHA=b['SHA'],actual_CPU_pending=True))
idx=N/'INDEX269_DATASET_CPU_SOURCE_FROZEN.json';put(idx,dict(kind='FROZEN_NEW267_FIRST_NECESSARY_RAW_ABI_CPU_PURPOSE',epoch=time.time(),files=[dict(path=str(p),bytes=p.stat().st_size,SHA=hashlib.sha256(p.read_bytes()).hexdigest())for p in files+[report]]))
print(json.dumps(dict(passed=True,index_SHA=hashlib.sha256(idx.read_bytes()).hexdigest())))
