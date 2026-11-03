"""One own closed V1 failure-source purpose: inventory plus original helper source only."""
from pathlib import Path,PurePosixPath
import sys,json,hashlib,time
R=Path(__file__).resolve().parent;out=R/'reports/PHASE1_CAPTURE_V1_PRE_SDK_IMPORT_FAILURE_SOURCE_EVIDENCE_V1.json';D=R/'discovery/phase1_first_startup_failure_v1';assert not out.exists() and not D.exists()
v=json.loads((R/'reports/PHASE1_E3_CAPTURE_V1_FIRST_ACTUAL_ADMISSION_SNAPSHOT.json').read_bytes());a=v['actual']['published_metadata'];end=a['PARENT_EXIT_SCOPE.json'];wait=a['PHASE1_CAPTURE_PARENT_WAITED_ACTUAL_V1.json'];err=a['cases/E3/WORKER_ERROR.json'];assert end['all_own_children_waited'] and end['original_single_GPU_private_EX_released'] and end['original_global_finite_EX_released'] and wait['actual_parent_p_wait_returned'] and wait['returncode']==1 and "No module named 'launch_storage_contract'"in err['error'];root=v['actual']['root'];D.mkdir()
sys.path.insert(0,str(R.parent/'mod4v1_experts_fulldr_rm70_20261101'));from project_connector import connect72
c=connect72();s=c.open_sftp()
try:
 name='MATERIALIZED_STATIC_FILES_PHASE1_CAPTURE_V1.json'
 with s.open(root+'/'+name,'rb')as f:raw=f.read(8*1024*1024+1)
 assert len(raw)<=8*1024*1024;inventory=json.loads(raw);rows=inventory['files'];assert len(rows)==3675
 with(D/name).open('xb')as f:f.write(raw)
 matches=[r for r in rows if PurePosixPath(r['relative']).name in ('launch_storage_contract.py','n80_gpu_capacity.py')];assert matches
 observed=[]
 for row in matches:
  rel=PurePosixPath(row['relative']);assert not rel.is_absolute() and '..'not in rel.parts and rel.suffix=='.py'
  with s.open(root+'/'+str(rel),'rb')as f:b=f.read(262145)
  assert len(b)<=262144 and (len(b),hashlib.sha256(b).hexdigest())==(row['bytes'],row['SHA'])
  dst=D.joinpath(*rel.parts);dst.parent.mkdir(parents=True,exist_ok=True)
  with dst.open('xb')as f:f.write(b)
  observed.append(dict(relative=str(rel),bytes=len(b),SHA256=hashlib.sha256(b).hexdigest(),local_source=str(dst),actual_opened_source_only=True))
 assert {PurePosixPath(x['relative']).name for x in observed}=={'launch_storage_contract.py','n80_gpu_capacity.py'}
 result=dict(kind='ACTUAL_CLOSED_PHASE1_V1_PRE_SDK_MISSING_MODULE_SOURCE_EVIDENCE_V1',epoch=time.time(),root=root,actual_resource_admission=a['ACTUAL_GROUP_ADMISSION.json'],actual_worker_error=err,actual_parent_exit=end,actual_external_parent_wait=wait,source_grade=a['PHASE1_CAPTURE_GROUP_CLOSED_SOURCE_GRADE_V1.json'],actual_static_inventory_bytes=len(raw),actual_static_inventory_SHA256=hashlib.sha256(raw).hexdigest(),actual_helper_sources=observed,classification='PRE_SDK_BOOTSTRAP_MODULE_RESOLUTION_FAILURE_NOT_QUALITY_SCORE',SDK_constructor_not_reached_inference='line35 import failed before Torch44/runpy48/env49; producer counters and FINAL absent remain null',actual_policy_BPTT_updates=None,gate1='UNKNOWN',capture_interface_passed=False,stage2_GO=False,model_raw_C_GPU_SDK_lock_signal_operations=0,old_root_consumed=True)
 with out.open('x',encoding='utf-8')as f:json.dump(result,f,indent=2)
 print(json.dumps(dict(report=str(out),sources=observed,actual_parent_wait_returncode=wait['returncode'],SDK_inferred_not_reached=True),indent=2))
finally:s.close();c.close()
