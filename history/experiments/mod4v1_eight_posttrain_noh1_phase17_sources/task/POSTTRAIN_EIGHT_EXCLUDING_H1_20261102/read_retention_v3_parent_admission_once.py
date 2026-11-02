from pathlib import Path
import sys,json
D=Path(__file__).resolve().parent;R=D.parent;sys.path.insert(0,str(R));from project_connector import connect72
p=D/'reports/PAIR1_RETENTION_V3_ADMISSION_STATUS.json';assert not p.exists();root=json.loads((R/'PAIR1_POSTTRAIN_RETENTION_GROUP_DISPATCH_ONCE_V3.json').read_bytes())['root'];c=connect72();s=c.open_sftp();v={'root':root,'models_raw_SDK_C_operations':0}
try:
 for rel in('PARENT_STARTED.json','ACTUAL_GROUP_ADMISSION.json','BOUNDED_ORIGINAL_RESOURCE_WAIT.json','CHILDREN.json','GROUP_BARRIER_STATUS.json','PARENT_ORIGINAL_ERROR.json','PARENT_EXIT_SCOPE.json','GROUP_SUPERVISOR_STDOUT_STDERR.log'):
  try:
   with s.open(root+'/'+rel,'rb')as z:raw=z.read()
   v[rel]=raw.decode()if rel.endswith('.log')else json.loads(raw)
  except FileNotFoundError:v[rel]=None
finally:s.close();c.close()
p.write_text(json.dumps(v,indent=2),encoding='utf-8');print(p);print(json.dumps(v,indent=2))
