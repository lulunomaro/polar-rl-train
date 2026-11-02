"""Onepublishedmetadata status snapshot, no models/raw/SDK/GPU/canonical operation."""
from pathlib import Path
import sys,json,datetime
D=Path(__file__).resolve().parent;sys.path.insert(0,str(D.parent));from project_connector import connect72
root=json.loads((D/'PAIR1_V4_STAGE_DISPATCH_RESULT.json').read_bytes())['root'];c=connect72();s=c.open_sftp();v={'root':root,'metadata_only':True}
try:
 for rel in('PREGO_RESOURCE_WAIT.json','OWNER_CURRENT.json','OWNER_ORIGINAL_ERROR.json','OWNER_EXIT_ACTUAL.json','roles/E0/GO_PRODUCTION.json','roles/CURB_PROTECTED878/GO_PRODUCTION.json'):
  try:
   with s.open(root+'/'+rel,'rb')as z:v[rel]=json.loads(z.read())
  except FileNotFoundError:v[rel]=None
finally:s.close();c.close()
p=D/'reports'/('PAIR1_V4_ADMISSION_STATUS_'+datetime.datetime.now().strftime('%Y%m%d_%H%M%S')+'.json');p.parent.mkdir(exist_ok=True);p.write_text(json.dumps(v,indent=2),encoding='utf-8');print(p);print(json.dumps(v,indent=2))
