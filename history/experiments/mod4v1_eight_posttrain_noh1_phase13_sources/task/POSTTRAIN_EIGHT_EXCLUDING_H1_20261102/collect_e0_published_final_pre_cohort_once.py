from pathlib import Path
import sys,json
D=Path(__file__).resolve().parent;sys.path.insert(0,str(D.parent));from project_connector import connect72
p=D/'reports/PAIR1_V4_E0_PUBLISHED_FINAL_PRE_COHORT.json';assert not p.exists();root=json.loads((D/'PAIR1_V4_STAGE_DISPATCH_RESULT.json').read_bytes())['root'];c=connect72();s=c.open_sftp();v={'root':root,'cohort_still_pending_Curb878':True,'PT_SDK_raw_C_calls':0}
try:
 for rel in('roles/E0/production/FINAL.json','roles/E0/PARENT_WAITED_ACTUAL.json','roles/E0/production/APP_CLOSED.json','roles/E0/production/ENV_CLOSE_RETURNED.json'):
  try:
   with s.open(root+'/'+rel,'rb')as z:v[rel]=json.loads(z.read())
  except FileNotFoundError:v[rel]=None
finally:s.close();c.close()
p.write_text(json.dumps(v,indent=2),encoding='utf-8');print(p);print(json.dumps(v,indent=2))
