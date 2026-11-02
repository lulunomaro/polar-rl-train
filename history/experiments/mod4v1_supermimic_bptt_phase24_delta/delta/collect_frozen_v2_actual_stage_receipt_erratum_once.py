"""Read actual V2 stage receipt without replaying the successful source stage.
The first caller incorrectly requested V1 receipt filename AFTER remote rc0.
No source mutation, native parent, model, SDK, C or resource operation.
"""
from pathlib import Path
import sys,json,hashlib,time
R=Path(__file__).resolve().parent;out=R/'reports/FROZEN_E3_W35_BATCH_V2_ACTUAL_SOURCE_STAGE_RECEIPT_CORRECTED_V2.json';assert not out.exists();v=json.loads((R/'reports/FROZEN_E3_W35_BATCH_V2_ACTUAL_SOURCE_STAGE_V1.json').read_bytes());assert v['returncode']==0;expected=json.loads(v['stdout']);assert expected['staged']and expected['parent_launches']==0 and expected['model_stat_hash_open_decode']==0;assert not(R/'FROZEN_E3_W35_BATCH_V2_PARENT_DISPATCH_ONCE.json').exists();root=v['root'];sys.path.insert(0,str(R.parent/'mod4v1_experts_fulldr_rm70_20261101'));from project_connector import connect72
c=connect72();s=c.open_sftp()
try:
 for name in('PARENT_STARTED.json','PARENT_FROZEN_MICROBATCH_DISPATCH_ONCE.json','PARENT_EXIT_SCOPE.json','STAGE_ERROR_MICROBATCH_V2.json'):
  try:s.lstat(root+'/'+name)
  except FileNotFoundError:pass
  else:raise AssertionError('Unused source stage unexpectedly native-started or failed: '+name)
 with s.open(root+'/STAGE_COMPLETE_MICROBATCH_V2.json','rb')as f:raw=f.read()
 actual=json.loads(raw);assert actual==expected and actual['kind']=='SOURCE_MICROBATCH_STAGE_COMPLETE_NOT_DISPATCH_V2';v.update(stage=actual,stage_complete_bytes=len(raw),stage_complete_SHA=hashlib.sha256(raw).hexdigest(),collector_erratum=dict(epoch=time.time(),wrong_expected_filename='STAGE_COMPLETE_MICROBATCH_V1.json',actual_filename='STAGE_COMPLETE_MICROBATCH_V2.json',initial_local_caller_exit=1,remote_stage_actual_returncode=0,stage_replayed=False,SDK_PT_C_parent_operations=0));out.write_text(json.dumps(v,indent=2),encoding='utf-8');print(json.dumps(dict(report=str(out),root=root,actual_stage_passed=True,stage_complete_SHA=v['stage_complete_SHA'],stage_replayed=False,parent_not_started=True),indent=2))
finally:s.close();c.close()
