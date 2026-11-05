from pathlib import Path
import json,sys
D=Path(__file__).resolve().parent;c=json.loads((D/'E0_D6_NATIVE_DIAGNOSTIC_CLOSED_RESULT.json').read_bytes());assert c['outer_actual_wait']['original_parent_reaped']is True and c['outer_actual_wait']['actual_wait_returncode']==1 and c['metadata']['ACTUAL_GROUP_ADMISSION.json']is None;out=D/'E0_D6_DIAG_PARENT_FAILURE_DETAIL.json';assert not out.exists();sys.path.insert(0,str(D.parent/'mod4v1_experts_fulldr_rm70_20261101'));from project_connector import connect72
client=connect72();s=client.open_sftp();r={}
try:
 for name in('PARENT_STARTED.json','PARENT_STDOUT_STDERR.log'):
  try:
   with s.open(c['root']+'/'+name,'rb')as f:
    f.seek(max(0,f.stat().st_size-12000));r[name]=f.read().decode('utf8','replace')
  except FileNotFoundError:r[name]=None
finally:s.close();client.close()
out.write_text(json.dumps(r,indent=2),encoding='utf8');print(json.dumps(r,indent=2))
