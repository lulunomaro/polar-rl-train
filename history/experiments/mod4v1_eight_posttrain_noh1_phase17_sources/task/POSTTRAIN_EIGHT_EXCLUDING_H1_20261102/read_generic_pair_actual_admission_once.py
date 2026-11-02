from pathlib import Path
import argparse,json,sys
D=Path(__file__).resolve().parent;sys.path.insert(0,str(D.parent));from project_connector import connect72
q=argparse.ArgumentParser();q.add_argument('--pair',required=True,type=int,choices=(2,3,4));a=q.parse_args();out=D/'reports'/('PAIR'+str(a.pair)+'_GENERIC_V2_ACTUAL_FIRST_ADMISSION_SNAPSHOT.json');assert not out.exists();d=json.loads((D/('PAIR'+str(a.pair)+'_GENERIC_V2_ORIGINAL_OWNER_DISPATCH_ONCE.json')).read_bytes());root=d['root'];c=connect72();s=c.open_sftp();v=dict(root=root,models_SDK_C_read_or_write_bycollector=0)
try:
 paths=['OWNER_CURRENT.json','PREGO_RESOURCE_WAIT.json','OWNER_ORIGINAL_ERROR.json','OWNER_EXIT_ACTUAL.json']
 for role in d['roles']:paths+=['roles/'+role+'/'+n for n in('GO_PRODUCTION.json','ROOT_ADMISSION_ACTUAL.json','WORKER_IDENTITY_ACTUAL.json')]
 for rel in paths:
  try:
   with s.open(root+'/'+rel,'rb')as f:v[rel]=json.loads(f.read())
  except FileNotFoundError:v[rel]=None
finally:s.close();c.close()
out.write_text(json.dumps(v,indent=2),encoding='utf-8');print(out);print(json.dumps(v,indent=2))
