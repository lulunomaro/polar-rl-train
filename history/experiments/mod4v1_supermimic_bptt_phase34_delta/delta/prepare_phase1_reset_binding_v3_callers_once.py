"""Derive NEW V3 own-purpose callers; never execute old or new callers here."""
from pathlib import Path
import ast,json,hashlib,time
R=Path(__file__).resolve().parent;out=R/'reports/PHASE1_RESET_BINDING_V3_PARENT_CALLER_SOURCE_V1.json';assert not out.exists();payload=json.loads((R/'PAPER_ALIGNED_REBUILD_20261103/PHASE1_CAPTURE_SOURCE_PAYLOAD_V3.json').read_bytes());assert payload['source_files']==331 and payload['source_mirror_required_files']==313
prior='''def verify_prior_closed_reset_binding_failure():
 p=json.loads((R/'PHASE1_E3_CAPTURE_BOOTSTRAP_V2_LATEST_CLOSED_RESULT_PATH.json').read_bytes());v=json.loads(Path(p['path']).read_bytes());w=v['outer_actual_parent_wait'];e=v['parent_exit_scope'];assert v['status']=='FAIL_CLOSED_CAPTURE_EXECUTION' and w['actual_parent_p_wait_returned'] and w['returncode']==1 and e['all_own_children_waited'] and e['original_single_GPU_private_EX_released'] and e['original_global_finite_EX_released'];assert 'Function identity mismatch: RecoveryEnv._reset_idx' in v['published_metadata']['cases/E3/WORKER_ERROR.json']['error']
 for rel,n in [('reports/PHASE1_B2_PARENT_SOURCE_VERIFY_V1.json',28),('reports/PHASE1_WORKER_V3_PARENT_SOURCE_VERIFY_V1.json',44),('reports/PHASE1_COLLECTOR_V3_PARENT_SOURCE_VERIFY_V1.json',43),('reports/PHASE1_MATERIALIZER_V3_PARENT_SOURCE_VERIFY_V1.json',42)]:
  fix=json.loads((R/rel).read_bytes());assert fix['tests_run']==n and fix['failures']==fix['errors']==0
 return v['root']
prior_consumed_root=verify_prior_closed_reset_binding_failure()'''
rows=[]
def derive(old,new,changes,guard=False,remote_unchanged=False):
 raw=(R/old).read_bytes();text=raw.decode();oldtree=ast.parse(text)
 for a,b,n in changes:
  assert text.count(a)==n,(old,a,text.count(a));text=text.replace(a,b)
 if guard:
  a=text.index('def verify_prior_closed_import_failure():');end='prior_consumed_root=verify_prior_closed_import_failure()';z=text.index(end,a)+len(end);text=text[:a]+prior+text[z:]
 ast.parse(text)
 if remote_unchanged:
  strings=lambda tree:[x.value for x in ast.walk(tree)if isinstance(x,ast.Constant)and type(x.value)is str and 'subprocess.Popen' in x.value]
  assert strings(oldtree)==strings(ast.parse(text)) and len(strings(oldtree))==1
 dest=R/new;assert not dest.exists()
 with dest.open('x',encoding='utf-8',newline='\n')as f:f.write(text)
 b=dest.read_bytes();rows.append(dict(original=old,original_SHA256=hashlib.sha256(raw).hexdigest(),new=new,bytes=len(b),SHA256=hashlib.sha256(b).hexdigest(),native_controller_dispatch_literal_unchanged=remote_unchanged))
derive('upload_preflight_phase1_e3_capture_bootstrap_v2_once.py','upload_preflight_phase1_e3_capture_reset_binding_v3_once.py',[
 ('PHASE1_CAPTURE_SOURCE_PAYLOAD_V2.json','PHASE1_CAPTURE_SOURCE_PAYLOAD_V3.json',1),
 ('PHASE1_E3_CAPTURE_BOOTSTRAP_V2_ACTUAL_PREFLIGHT.json','PHASE1_E3_CAPTURE_RESET_BINDING_V3_ACTUAL_PREFLIGHT.json',1),
 ('PHASE1_E3_CAPTURE_BOOTSTRAP_V2_PREFLIGHT_STARTED_ONCE.json','PHASE1_E3_CAPTURE_RESET_BINDING_V3_PREFLIGHT_STARTED_ONCE.json',1),
 ("==280 and value['source_mirror_required_files']==263","==331 and value['source_mirror_required_files']==313",1),
 ("gid='MOD4V1_PHASE1_E3_PASSIVE_CAPTURE_V1_BOOTSTRAP_FIX_V2_'","gid='MOD4V1_PHASE1_E3_PASSIVE_CAPTURE_V1_RESET_BINDING_V3_'",1),
 ('source_phase1_capture_materializer_v2/stage_phase1_capture_v2.py','source_phase1_capture_materializer_v3/stage_phase1_capture_v3.py',1),
 ('NEW_PHASE1_CAPTURE_ACTUAL_SOURCE_PREFLIGHT_PURPOSE_V2','NEW_PHASE1_CAPTURE_ACTUAL_SOURCE_PREFLIGHT_PURPOSE_V3',1)
 ],guard=True)
derive('stage_phase1_e3_capture_bootstrap_v2_once.py','stage_phase1_e3_capture_reset_binding_v3_once.py',[
 ('PHASE1_E3_CAPTURE_BOOTSTRAP_V2_ACTUAL_STAGE.json','PHASE1_E3_CAPTURE_RESET_BINDING_V3_ACTUAL_STAGE.json',1),
 ('PHASE1_E3_CAPTURE_BOOTSTRAP_V2_STAGE_STARTED_ONCE.json','PHASE1_E3_CAPTURE_RESET_BINDING_V3_STAGE_STARTED_ONCE.json',1),
 ('PHASE1_E3_CAPTURE_BOOTSTRAP_V2_ACTUAL_PREFLIGHT.json','PHASE1_E3_CAPTURE_RESET_BINDING_V3_ACTUAL_PREFLIGHT.json',1),
 ('e39fc8936136f89e708df6a9a26911135d0c1616c641564cf155235ff0d06f6d','2a4213d95939216f3a91db6c1739a443907aadf33c4f615aa897eace5a915425',1),
 ('(34834,expected)','(42437,expected)',1),
 ('ACTUAL_PHASE1_CAPTURE_FILE_MATERIALIZATION_NOT_ADMISSION_V2','ACTUAL_PHASE1_CAPTURE_FILE_MATERIALIZATION_NOT_ADMISSION_V3',1)
 ])
derive('dispatch_phase1_e3_capture_bootstrap_v2_original_parent_once.py','dispatch_phase1_e3_capture_reset_binding_v3_original_parent_once.py',[
 ('PHASE1_E3_CAPTURE_BOOTSTRAP_V2_ORIGINAL_PARENT_DISPATCH_ONCE.json','PHASE1_E3_CAPTURE_RESET_BINDING_V3_ORIGINAL_PARENT_DISPATCH_ONCE.json',1),
 ('PHASE1_E3_CAPTURE_BOOTSTRAP_V2_PARENT_DISPATCH_STARTED_ONCE.json','PHASE1_E3_CAPTURE_RESET_BINDING_V3_PARENT_DISPATCH_STARTED_ONCE.json',1),
 ('PHASE1_E3_CAPTURE_BOOTSTRAP_V2_ACTUAL_STAGE.json','PHASE1_E3_CAPTURE_RESET_BINDING_V3_ACTUAL_STAGE.json',1),
 ("['source_derivation_version']==2","['source_derivation_version']==3",1),
 ('PHASE1_CAPTURE_SINGLE_ORIGINAL_PARENT_DISPATCH_RESULT_V2','PHASE1_CAPTURE_SINGLE_ORIGINAL_PARENT_DISPATCH_RESULT_V3',1)
 ],guard=True,remote_unchanged=True)
derive('collect_phase1_capture_bootstrap_v2_closed_metadata_once.py','collect_phase1_capture_reset_binding_v3_closed_metadata_once.py',[
 ('source_phase1_capture_result_collector_v2','source_phase1_capture_result_collector_v3',1),
 ('PHASE1_CAPTURE_BOOTSTRAP_V2_CLOSED_METADATA_COLLECTION_STARTED_ONCE.json','PHASE1_CAPTURE_RESET_BINDING_V3_CLOSED_METADATA_COLLECTION_STARTED_ONCE.json',1),
 ('PHASE1_E3_CAPTURE_BOOTSTRAP_V2_LATEST_CLOSED_RESULT_PATH.json','PHASE1_E3_CAPTURE_RESET_BINDING_V3_LATEST_CLOSED_RESULT_PATH.json',1),
 ('8a0dfd808483687f3a718d327c6dddf77d6989ed140eddc4de6dc262b832c29c','2f6188fe03958bfd237efab6c22ea6f63ffa61c54608144607db5d8bc9ff577f',1),
 ('f810645b940445863ea4375f5b27b5fea15e5b2b0eaff53aacf88ffb08ffb1dd','71e4df44944aa9c4b81702bd673259107570ddd49bd692993b9fe81d1e7a303d',1),
 ('PHASE1_E3_CAPTURE_BOOTSTRAP_V2_ACTUAL_CLOSED_','PHASE1_E3_CAPTURE_RESET_BINDING_V3_ACTUAL_CLOSED_',1),
 ('PHASE1_E3_CAPTURE_BOOTSTRAP_V2_ORIGINAL_PARENT_DISPATCH_ONCE.json','PHASE1_E3_CAPTURE_RESET_BINDING_V3_ORIGINAL_PARENT_DISPATCH_ONCE.json',1)
 ])
v=dict(kind='NEW_V3_ONLY_PARENT_CALLER_SOURCE_DERIVATIONS_NOT_EXECUTED',epoch=time.time(),rows=rows,prior_actual_closed_reset_binding_failure_required=True,payload_source_files=331,source_mirror_required_files=313,actual_preflight_stage_parent_SDK_collect_operations=0,wire_controller_parent_resource_gates_unchanged=True)
with out.open('x',encoding='utf-8')as f:json.dump(v,f,indent=2)
print(json.dumps(dict(report=str(out),callers=[x['new']for x in rows],executed=False),indent=2))
