from pathlib import Path
import ast,hashlib,json,time
N=Path(__file__).resolve().parent;T=N.parent;S=N/'source';R=N/'reports';S.mkdir(exist_ok=False);R.mkdir(exist_ok=False)
def put(p,x):
 with p.open('x',encoding='utf8')as f:json.dump(x,f,indent=2,allow_nan=False)
D=T/'FUDAN_TERRAIN80_CURRENT_DEPTH_PACKET_V272_20261101';j=json.loads((D/'reports/ROOT272_NEW240_MEAN_REGRESSION_PARENT_OR_ORIGINAL_ERROR_RETURNED_ACTUAL.json').read_bytes());assert j['passed_execution'];r=j['original_parent']['result'];assert r['passed']and r['controls']==64 and r['own_transitions']==5120 and r['complete_current_depth_packet_recorded']and r['actual_anchor_packets_validated']>0
binding=next(x for x in j['full_UTF8']if x['path'].endswith('/ACTUAL272_FULL_MEASURED_SCHEMA_BINDING.json'));b=json.loads(binding['UTF8']);admission=next(x for x in j['full_UTF8']if x['path'].endswith('/ACTUAL272_CURRENT_AUTHORITY_AND_N1_RESOURCE_ADMISSION.json'));source_task=next(json.loads(x['UTF8'])for x in j['full_UTF8']if x['path'].endswith('/TASK272_ADMITTED_ACTUAL.json'))
log=next(x['UTF8']for x in j['full_UTF8']if x['path'].endswith('/ACTUAL272_STDOUT_STDERR.log'));assert not('PxPhysics::createMaterial'in log and'64K'in log)
C=T/'DEPTH_WM224_FUTURE_SAFE_H32_WARM_SOURCE_V273V2_20261101';refs=json.loads((C/'SOURCE273_PINNED_BINDINGS_AND_ABI.json').read_bytes())['references'];files=[]
for row in refs:
 p=Path(row['path'])
 if p.suffix!='.py':continue
 data=p.read_bytes();assert len(data)==row['bytes']and hashlib.sha256(data).hexdigest()==row['SHA']
 relative=Path('kernel/supermimic_wheel_leg_v3')/p.name if p.parent.name=='supermimic_wheel_leg_v3'else Path('code')/p.name
 q=S/relative;q.parent.mkdir(parents=True,exist_ok=True);q.write_bytes(data);files.append(q)
q=S/'code/future_safe_wm_warm273.py';q.write_bytes((C/'future_safe_wm_warm273.py').read_bytes());files.append(q)
q=S/'worker274_new272_H32_CUDA_no_optimizer_once.py';q.write_bytes((N/q.name).read_bytes());files.append(q)
receipt=T/'MODEL2050_LITERAL_JUMP_400N50_ADAPT_V240_20261101/reports/ROOT240V2_NEW_FORMAL_INITIAL_WHOLE_CPU_RETURNED_ACTUAL.json'
task=dict(kind='ACTUAL_NEW272_H32_WM_CUDA_ADMISSION_NO_OPTIMIZER',GPU_UUID='GPU-16828f91-2b45-b646-8dc0-9481138e2842',dataset=r['producer'],actual_binding=b,binding_witness_SHA=binding['SHA'],source_actual_resource_admission_SHA=admission['SHA'],source_run_id=source_task['run_id'],source_generation=source_task['generation'],teacher_SHA=r['model_SHA'],teacher_whole_CPU_receipt_SHA=hashlib.sha256(receipt.read_bytes()).hexdigest(),private_shared_EX_and_current_authority_admitted=False,raw_byte_open_max=1,old_datasets_models_PT_reads=0,optimizer_steps_allowed=0)
put(N/'TASK274_LOCAL_FROZEN.json',task)
files +=[N/'TASK274_LOCAL_FROZEN.json',Path(__file__).resolve(),N/'run_ROOT274_new272_CUDA_admission_once.py',N/'parent274_new272_model_only_once.py',N/'worker274_new272_H32_CUDA_no_optimizer_once.py']
files.append(N/'BEFORE_USE274V2_ONLY_LOCK_PATH_AND_NEW_NAMESPACE.json')
for p in files:
 if p.suffix=='.py':ast.parse(p.read_text('utf8'),filename=str(p))
report=R/'ROOT274_NEW_MEASURED_DATA_CUDA_PURPOSE_SOURCE_CPU_RETURNED.json';put(report,dict(passed=True,epoch=time.time(),source_AST=sum(p.suffix=='.py'for p in files),new272_measured_data_only=True,first_anchor_H32=True,source_checkpoint_metadata_only=True,checkpoint_read_max=0,WM_scratch_normalizer_fits_then_exact_restore=True,optimizer_step_max=0,actual_GPU_admission_pending=True,source272_64Kerrors=0))
idx=N/'INDEX274_NEW272_CUDA_ADMISSION_SOURCE_FROZEN.json';put(idx,dict(kind='FROZEN_NEW272_FIRST_RAW_WM_CUDA_NO_OPTIMIZER_PURPOSE',epoch=time.time(),files=[dict(path=str(p),bytes=p.stat().st_size,SHA=hashlib.sha256(p.read_bytes()).hexdigest())for p in files+[report]]))
print(json.dumps(dict(passed=True,index_SHA=hashlib.sha256(idx.read_bytes()).hexdigest(),source_files=len(files))))
