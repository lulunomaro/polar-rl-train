"""Derive NEW V2 once callers. No old caller is executed or changed."""
from pathlib import Path
import ast,json,hashlib,time
R=Path(__file__).resolve().parent;out=R/'reports/PHASE1_BOOTSTRAP_V2_PARENT_CALLER_SOURCE_V1.json';assert not out.exists()
payload=json.loads((R/'PAPER_ALIGNED_REBUILD_20261103/PHASE1_CAPTURE_SOURCE_PAYLOAD_V2.json').read_bytes());assert payload['source_files']==280 and payload['source_mirror_required_files']==263
prior_guard="""
def verify_prior_closed_import_failure():
 p=json.loads((R/'PHASE1_E3_CAPTURE_V1_LATEST_CLOSED_RESULT_PATH.json').read_bytes());v=json.loads(Path(p['path']).read_bytes());w=v['outer_actual_parent_wait'];e=v['parent_exit_scope'];assert v['status']=='FAIL_CLOSED_CAPTURE_EXECUTION' and w['actual_parent_p_wait_returned'] and w['returncode']==1 and e['all_own_children_waited'] and e['original_single_GPU_private_EX_released'] and e['original_global_finite_EX_released'];assert \"No module named 'launch_storage_contract'\" in v['published_metadata']['cases/E3/WORKER_ERROR.json']['error']
 fix=json.loads((R/'reports/PHASE1_WORKER_V2_PARENT_SOURCE_VERIFY_V1.json').read_bytes());assert fix['tests_run']==96 and fix['failures']==fix['errors']==0 and fix['source13_unchanged_after_test'];return v['root']
prior_consumed_root=verify_prior_closed_import_failure()
"""
rows=[]
def derive(old,new,changes,guard_anchor=None):
 p=R/old;b=p.read_bytes();text=b.decode()
 for before,after,count in changes:
  assert text.count(before)==count,(old,before,text.count(before));text=text.replace(before,after)
 if guard_anchor:
  assert text.count(guard_anchor)==1;text=text.replace(guard_anchor,prior_guard+'\n'+guard_anchor)
 ast.parse(text);dest=R/new;assert not dest.exists()
 with dest.open('x',encoding='utf-8',newline='\n')as f:f.write(text)
 nb=dest.read_bytes();rows.append(dict(original=old,original_SHA256=hashlib.sha256(b).hexdigest(),new=new,bytes=len(nb),SHA256=hashlib.sha256(nb).hexdigest()))
derive('upload_preflight_phase1_e3_capture_v1_once.py','upload_preflight_phase1_e3_capture_bootstrap_v2_once.py',[
 ('PHASE1_CAPTURE_SOURCE_PAYLOAD_V1.json','PHASE1_CAPTURE_SOURCE_PAYLOAD_V2.json',1),
 ('PHASE1_E3_CAPTURE_V1_ACTUAL_PREFLIGHT.json','PHASE1_E3_CAPTURE_BOOTSTRAP_V2_ACTUAL_PREFLIGHT.json',1),
 ('PHASE1_E3_CAPTURE_V1_PREFLIGHT_STARTED_ONCE.json','PHASE1_E3_CAPTURE_BOOTSTRAP_V2_PREFLIGHT_STARTED_ONCE.json',1),
 ("==276 and value['source_mirror_required_files']==259","==280 and value['source_mirror_required_files']==263",1),
 ("gid='MOD4V1_PHASE1_E3_PASSIVE_CAPTURE_V1_'","gid='MOD4V1_PHASE1_E3_PASSIVE_CAPTURE_V1_BOOTSTRAP_FIX_V2_'",1),
 ('source_phase1_capture_materializer_v1/stage_phase1_capture_v1.py','source_phase1_capture_materializer_v2/stage_phase1_capture_v2.py',1),
 ('NEW_PHASE1_CAPTURE_ACTUAL_SOURCE_PREFLIGHT_PURPOSE_V1','NEW_PHASE1_CAPTURE_ACTUAL_SOURCE_PREFLIGHT_PURPOSE_V2',1)
 ],'payload={}')
derive('stage_phase1_e3_capture_after_preflight_v1_once.py','stage_phase1_e3_capture_bootstrap_v2_once.py',[
 ('PHASE1_E3_CAPTURE_V1_ACTUAL_STAGE.json','PHASE1_E3_CAPTURE_BOOTSTRAP_V2_ACTUAL_STAGE.json',1),
 ('PHASE1_E3_CAPTURE_V1_STAGE_STARTED_ONCE.json','PHASE1_E3_CAPTURE_BOOTSTRAP_V2_STAGE_STARTED_ONCE.json',1),
 ('PHASE1_E3_CAPTURE_V1_ACTUAL_PREFLIGHT.json','PHASE1_E3_CAPTURE_BOOTSTRAP_V2_ACTUAL_PREFLIGHT.json',1),
 ('0ee747167d7c3389e5e3541c527ac5a4f4244a2a91b08e7733f38e6c8d2fda98','e39fc8936136f89e708df6a9a26911135d0c1616c641564cf155235ff0d06f6d',1),
 ('(31219,expected)','(34834,expected)',1),
 ('ACTUAL_PHASE1_CAPTURE_FILE_MATERIALIZATION_NOT_ADMISSION_V1','ACTUAL_PHASE1_CAPTURE_FILE_MATERIALIZATION_NOT_ADMISSION_V2',1)
 ])
derive('dispatch_phase1_e3_capture_original_parent_v1_once.py','dispatch_phase1_e3_capture_bootstrap_v2_original_parent_once.py',[
 ('PHASE1_E3_CAPTURE_V1_ORIGINAL_PARENT_DISPATCH_ONCE.json','PHASE1_E3_CAPTURE_BOOTSTRAP_V2_ORIGINAL_PARENT_DISPATCH_ONCE.json',1),
 ('PHASE1_E3_CAPTURE_V1_PARENT_DISPATCH_STARTED_ONCE.json','PHASE1_E3_CAPTURE_BOOTSTRAP_V2_PARENT_DISPATCH_STARTED_ONCE.json',1),
 ('PHASE1_E3_CAPTURE_V1_ACTUAL_STAGE.json','PHASE1_E3_CAPTURE_BOOTSTRAP_V2_ACTUAL_STAGE.json',1),
 ("stage['receipt']['metadata_validation']['passed']","stage['receipt']['metadata_validation']['passed'] and stage['receipt']['metadata_validation']['source_derivation_version']==2 and len(stage['receipt']['metadata_validation']['original_helper_bootstrap']['sources'])==2",1),
 ('PHASE1_CAPTURE_SINGLE_ORIGINAL_PARENT_DISPATCH_RESULT_V1','PHASE1_CAPTURE_SINGLE_ORIGINAL_PARENT_DISPATCH_RESULT_V2',1)
 ],"out=R/'reports/PHASE1_E3_CAPTURE_BOOTSTRAP_V2_ORIGINAL_PARENT_DISPATCH_ONCE.json'")
with out.open('x',encoding='utf-8')as f:json.dump(dict(kind='NEW_V2_ONLY_PARENT_CALLER_SOURCE_DERIVATIONS_NOT_EXECUTED',epoch=time.time(),rows=rows,prior_closed_failure_required=True,actual_preflight_stage_parent_SDK_operations=0,wire_controller_parent_no_resource_gate_changes=True),f,indent=2)
print(json.dumps(dict(report=str(out),callers=[x['new']for x in rows],executed=False),indent=2))
