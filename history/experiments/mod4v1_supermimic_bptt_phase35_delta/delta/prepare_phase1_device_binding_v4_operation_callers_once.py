"""Prepare NEW V4 preflight/stage/parent callers only; no operation is run here."""
from pathlib import Path
import ast,json,hashlib,time
R=Path(__file__).resolve().parent;out=R/'reports/PHASE1_DEVICE_BINDING_V4_OPERATION_CALLER_SOURCE_V1.json';assert not out.exists();p=json.loads((R/'PAPER_ALIGNED_REBUILD_20261103/PHASE1_CAPTURE_SOURCE_PAYLOAD_V4.json').read_bytes());assert p['source_files']==350 and p['source_mirror_required_files']==332
prior='''def verify_prior_closed_boundary_device_failure():
 p=json.loads((R/'PHASE1_E3_CAPTURE_RESET_BINDING_V3_LATEST_CLOSED_RESULT_PATH.json').read_bytes());v=json.loads(Path(p['path']).read_bytes());w=v['outer_actual_parent_wait'];e=v['parent_exit_scope'];assert v['status']=='FAIL_CLOSED_CAPTURE_EXECUTION' and w['actual_parent_p_wait_returned'] and w['returncode']==1 and e['all_own_children_waited'] and e['original_single_GPU_private_EX_released'] and e['original_global_finite_EX_released'];assert 'separate original bool term/trunc N80 required' in v['published_metadata']['cases/E3/WORKER_ERROR.json']['error']
 for rel,n in [('reports/PHASE1_WORKER_V4_PARENT_SOURCE_VERIFY_V1.json',44),('reports/PHASE1_COLLECTOR_V4_PARENT_SOURCE_VERIFY_V1.json',51),('reports/PHASE1_MATERIALIZER_V4_PARENT_SOURCE_VERIFY_V1.json',44)]:
  fix=json.loads((R/rel).read_bytes());assert fix['tests_run']==n and fix['failures']==fix['errors']==0
 c=json.loads((R/'reports/PHASE1_BOUNDARY_DEVICE_ACTUAL_CPU_V1.json').read_bytes());q=c['receipt'];assert c['returncode']==0 and q['old_string_device_reproduced'] and q['existing_normalized_device_passed'] and q['negative_cases']==11 and not q['actual_V3_root_cause_confirmed']
 return v['root']
prior_consumed_root=verify_prior_closed_boundary_device_failure()'''
rows=[]
def derive(old,new,changes,guard=False,remote_unchanged=False):
 b=(R/old).read_bytes();t=b.decode();tree=ast.parse(t)
 for a,z,n in changes:
  assert t.count(a)==n,(old,a,t.count(a));t=t.replace(a,z)
 if guard:
  a=t.index('def verify_prior_closed_reset_binding_failure():');end='prior_consumed_root=verify_prior_closed_reset_binding_failure()';z=t.index(end,a)+len(end);t=t[:a]+prior+t[z:]
 ast.parse(t)
 if remote_unchanged:
  f=lambda tr:[x.value for x in ast.walk(tr)if isinstance(x,ast.Constant)and type(x.value)is str and 'subprocess.Popen'in x.value];assert len(f(tree))==1 and f(tree)==f(ast.parse(t))
 dest=R/new;assert not dest.exists()
 with dest.open('x',encoding='utf-8',newline='\n')as s:s.write(t)
 q=dest.read_bytes();rows.append(dict(original=old,original_SHA256=hashlib.sha256(b).hexdigest(),new=new,bytes=len(q),SHA256=hashlib.sha256(q).hexdigest(),native_Popen_wait_controller_literal_unchanged=remote_unchanged))
derive('upload_preflight_phase1_e3_capture_reset_binding_v3_once.py','upload_preflight_phase1_e3_capture_device_binding_v4_once.py',[
 ('PHASE1_CAPTURE_SOURCE_PAYLOAD_V3.json','PHASE1_CAPTURE_SOURCE_PAYLOAD_V4.json',1),
 ('PHASE1_E3_CAPTURE_RESET_BINDING_V3_ACTUAL_PREFLIGHT.json','PHASE1_E3_CAPTURE_DEVICE_BINDING_V4_ACTUAL_PREFLIGHT.json',1),
 ('PHASE1_E3_CAPTURE_RESET_BINDING_V3_PREFLIGHT_STARTED_ONCE.json','PHASE1_E3_CAPTURE_DEVICE_BINDING_V4_PREFLIGHT_STARTED_ONCE.json',1),
 ("==331 and value['source_mirror_required_files']==313","==350 and value['source_mirror_required_files']==332",1),
 ("gid='MOD4V1_PHASE1_E3_PASSIVE_CAPTURE_V1_RESET_BINDING_V3_'","gid='MOD4V1_PHASE1_E3_PASSIVE_CAPTURE_V1_DEVICE_BINDING_V4_'",1),
 ('source_phase1_capture_materializer_v3/stage_phase1_capture_v3.py','source_phase1_capture_materializer_v4/stage_phase1_capture_v4.py',1),
 ('NEW_PHASE1_CAPTURE_ACTUAL_SOURCE_PREFLIGHT_PURPOSE_V3','NEW_PHASE1_CAPTURE_ACTUAL_SOURCE_PREFLIGHT_PURPOSE_V4',1)
 ],guard=True)
derive('stage_phase1_e3_capture_reset_binding_v3_once.py','stage_phase1_e3_capture_device_binding_v4_once.py',[
 ('PHASE1_E3_CAPTURE_RESET_BINDING_V3_ACTUAL_STAGE.json','PHASE1_E3_CAPTURE_DEVICE_BINDING_V4_ACTUAL_STAGE.json',1),
 ('PHASE1_E3_CAPTURE_RESET_BINDING_V3_STAGE_STARTED_ONCE.json','PHASE1_E3_CAPTURE_DEVICE_BINDING_V4_STAGE_STARTED_ONCE.json',1),
 ('PHASE1_E3_CAPTURE_RESET_BINDING_V3_ACTUAL_PREFLIGHT.json','PHASE1_E3_CAPTURE_DEVICE_BINDING_V4_ACTUAL_PREFLIGHT.json',1),
 ('2a4213d95939216f3a91db6c1739a443907aadf33c4f615aa897eace5a915425','f3059d24444c40873f2d55aeb22fd82e32284e761db96250ec985314080c6507',1),
 ('(42437,expected)','(45850,expected)',1),
 ('ACTUAL_PHASE1_CAPTURE_FILE_MATERIALIZATION_NOT_ADMISSION_V3','ACTUAL_PHASE1_CAPTURE_FILE_MATERIALIZATION_NOT_ADMISSION_V4',1)
 ])
derive('dispatch_phase1_e3_capture_reset_binding_v3_original_parent_once.py','dispatch_phase1_e3_capture_device_binding_v4_original_parent_once.py',[
 ('PHASE1_E3_CAPTURE_RESET_BINDING_V3_ORIGINAL_PARENT_DISPATCH_ONCE.json','PHASE1_E3_CAPTURE_DEVICE_BINDING_V4_ORIGINAL_PARENT_DISPATCH_ONCE.json',1),
 ('PHASE1_E3_CAPTURE_RESET_BINDING_V3_PARENT_DISPATCH_STARTED_ONCE.json','PHASE1_E3_CAPTURE_DEVICE_BINDING_V4_PARENT_DISPATCH_STARTED_ONCE.json',1),
 ('PHASE1_E3_CAPTURE_RESET_BINDING_V3_ACTUAL_STAGE.json','PHASE1_E3_CAPTURE_DEVICE_BINDING_V4_ACTUAL_STAGE.json',1),
 ("['source_derivation_version']==3","['source_derivation_version']==4",1),
 ('PHASE1_CAPTURE_SINGLE_ORIGINAL_PARENT_DISPATCH_RESULT_V3','PHASE1_CAPTURE_SINGLE_ORIGINAL_PARENT_DISPATCH_RESULT_V4',1)
 ],guard=True,remote_unchanged=True)
v=dict(kind='NEW_V4_OPERATION_CALLER_SOURCES_NOT_EXECUTED',epoch=time.time(),rows=rows,prior_actual_closed_boundary_failure_required=True,actual_CPU11_contract_required=True,payload_source_files=350,source_mirror_required_files=332,actual_preflight_stage_parent_SDK_operations=0,wire_controller_parent_resource_gates_unchanged=True)
with out.open('x',encoding='utf-8')as s:json.dump(v,s,indent=2)
print(json.dumps(dict(report=str(out),callers=[x['new']for x in rows],executed=False),indent=2))
