"""NEW Admission2 static-only caller preparation; no native dispatch generated."""
from pathlib import Path
import ast,json,hashlib,time
R=Path(__file__).resolve().parent;out=R/'reports/PHASE1_V4_ADMISSION2_STATIC_CALLER_SOURCE_V1.json';assert not out.exists()
guard='''def verify_prior_zero_admission_closed():
 v=json.loads((R/'reports/PHASE1_V4_ZERO_ADMISSION_CLOSED_TRUTH_V1.json').read_bytes());e=v['parent_exit_scope'];w=v['outer_actual_wait'];assert v['actual_group_admission']is None and v['actual_children']is None and v['actual_GO']is None and not v['SDK_selected_model_opened']and e['all_own_children_waited']and e['child_waits']==[]and e['original_single_GPU_private_EX_released']and e['original_global_finite_EX_released']and w['actual_parent_p_wait_returned']and w['returncode']==1 and w['controller_errors']==[]
 for rel,n in [('reports/PHASE1_WORKER_V4_PARENT_SOURCE_VERIFY_V1.json',44),('reports/PHASE1_COLLECTOR_V4_PARENT_SOURCE_VERIFY_V1.json',51),('reports/PHASE1_MATERIALIZER_V4_PARENT_SOURCE_VERIFY_V1.json',44)]:
  f=json.loads((R/rel).read_bytes());assert f['tests_run']==n and f['failures']==f['errors']==0
 return v['root']
prior_consumed_root=verify_prior_zero_admission_closed()'''
rows=[]
def derive(old,new,changes,prior=False):
 b=(R/old).read_bytes();t=b.decode()
 for a,z,n in changes:
  assert t.count(a)==n,(old,a,t.count(a));t=t.replace(a,z)
 if prior:
  a=t.index('def verify_prior_closed_boundary_device_failure():');end='prior_consumed_root=verify_prior_closed_boundary_device_failure()';z=t.index(end,a)+len(end);t=t[:a]+guard+t[z:]
 ast.parse(t);dest=R/new;assert not dest.exists()
 with dest.open('x',encoding='utf-8',newline='\n')as f:f.write(t)
 q=dest.read_bytes();rows.append(dict(original=old,original_SHA256=hashlib.sha256(b).hexdigest(),new=new,bytes=len(q),SHA256=hashlib.sha256(q).hexdigest()))
derive('upload_preflight_phase1_e3_capture_device_binding_v4_once.py','upload_preflight_phase1_e3_capture_v4_admission2_once.py',[
 ('PHASE1_E3_CAPTURE_DEVICE_BINDING_V4_ACTUAL_PREFLIGHT.json','PHASE1_E3_CAPTURE_V4_ADMISSION2_ACTUAL_PREFLIGHT.json',1),
 ('PHASE1_E3_CAPTURE_DEVICE_BINDING_V4_PREFLIGHT_STARTED_ONCE.json','PHASE1_E3_CAPTURE_V4_ADMISSION2_PREFLIGHT_STARTED_ONCE.json',1),
 ("gid='MOD4V1_PHASE1_E3_PASSIVE_CAPTURE_V1_DEVICE_BINDING_V4_'","gid='MOD4V1_PHASE1_E3_PASSIVE_CAPTURE_V1_DEVICE_BINDING_V4_ADMISSION2_'",1),
 ('NEW_PHASE1_CAPTURE_ACTUAL_SOURCE_PREFLIGHT_PURPOSE_V4','NEW_PHASE1_V4_ADMISSION2_STATIC_PREFLIGHT_PURPOSE',1)
 ],prior=True)
derive('stage_phase1_e3_capture_device_binding_v4_once.py','stage_phase1_e3_capture_v4_admission2_once.py',[
 ('PHASE1_E3_CAPTURE_DEVICE_BINDING_V4_ACTUAL_STAGE.json','PHASE1_E3_CAPTURE_V4_ADMISSION2_ACTUAL_STAGE.json',1),
 ('PHASE1_E3_CAPTURE_DEVICE_BINDING_V4_STAGE_STARTED_ONCE.json','PHASE1_E3_CAPTURE_V4_ADMISSION2_STAGE_STARTED_ONCE.json',1),
 ('PHASE1_E3_CAPTURE_DEVICE_BINDING_V4_ACTUAL_PREFLIGHT.json','PHASE1_E3_CAPTURE_V4_ADMISSION2_ACTUAL_PREFLIGHT.json',1),
 ('ACTUAL_PHASE1_CAPTURE_FILE_MATERIALIZATION_NOT_ADMISSION_V4','ACTUAL_PHASE1_CAPTURE_FILE_MATERIALIZATION_NOT_ADMISSION_V4_ADMISSION2',1)
 ])
v=dict(kind='NEW_ADMISSION2_STATIC_SOURCE_ONLY_CALLERS_AFTER_CLOSED_ZERO_GO',epoch=time.time(),rows=rows,unchanged_source_payload_and_materializer=True,new_root_required=True,actual_preflight_stage_native_parent_SDK_operations=0,no_dispatcher_created=True,requires_future_original_resources_and_actual_release_witness_before_dispatch=True)
with out.open('x',encoding='utf-8')as f:json.dump(v,f,indent=2)
print(json.dumps(dict(report=str(out),callers=[x['new']for x in rows],native_parent_created=False),indent=2))
