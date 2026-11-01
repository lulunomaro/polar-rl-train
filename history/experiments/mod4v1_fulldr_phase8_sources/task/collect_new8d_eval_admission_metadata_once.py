"""Oneownednew8dactualadmission/startupmetadata snapshot. No raw/model/SDK driver/canonical accesses."""
from pathlib import Path
import json,datetime
from project_connector import connect72
R=Path(__file__).resolve().parent;d=json.loads((R/'reports/W35_after_resume89aca_eval_dispatch_20261102_070117.json').read_bytes());job=d['new_job'];c=connect72();s=c.open_sftp();v={'kind':'OWN_NEW8D_FULL32_ACTUAL_ADMISSION_STARTUP_METADATA_ONLY','job':job,'new_source_SHA':d['new_source_model']['SHA'],'files':{},'model_raw_SDK_driver_canonical_access':False}
try:
 for rel in('PARENT_STARTED.json','WAIT_ORIGINAL_RESOURCES.json','ACTUAL_EVAL_ADMISSION.json','WORKER_IDENTITY.json','TASK_ADMITTED.json','PARENT_ORIGINAL_ERROR.json','PARENT_EXIT_SCOPE.json','actual_latest32/FULLRESTORE227_BEFORE_CONTROL.json','actual_latest32/ORIGINAL227_EVAL_ERROR.json'):
  try:
   with s.open(job+'/'+rel,'rb')as f:v['files'][rel]=json.loads(f.read())
  except FileNotFoundError:continue
finally:s.close();c.close()
p=R/'reports'/('W35_NEW8D_ADMISSION_METADATA_'+datetime.datetime.now().strftime('%Y%m%d_%H%M%S')+'.json');p.write_text(json.dumps(v,ensure_ascii=False,indent=2),encoding='utf-8');print('REPORT',p);print(json.dumps({k:x for k,x in v.items()if k!='files'},indent=2));print(json.dumps({k:x for k,x in v['files'].items()if k not in('TASK_ADMITTED.json','actual_latest32/FULLRESTORE227_BEFORE_CONTROL.json')},ensure_ascii=False,indent=2));full=v['files'].get('actual_latest32/FULLRESTORE227_BEFORE_CONTROL.json');print('FULLRESTORE_AVAILABLE',bool(full))
