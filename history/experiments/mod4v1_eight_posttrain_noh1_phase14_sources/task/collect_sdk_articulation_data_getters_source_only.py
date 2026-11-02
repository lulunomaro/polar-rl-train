"""Exacteditableisaaclab6.1.14 source locatedbyactivePythonmetadata. Rawbytescopy/noSDKimportorApp."""
from pathlib import Path
import json,hashlib,urllib.parse
from project_connector import connect72
R=Path(__file__).resolve().parent;D=R/'diagnostics/W35_SDK_DATA_GETTER_ORIGIN_SOURCE_V1';origin=json.loads((D/'ORIGIN_READ_RECEIPT.json').read_bytes());dist=origin['python_origin']['distributions']['isaaclab'];url=json.loads(dist['direct_url']);base=urllib.parse.unquote(urllib.parse.urlparse(url['url']).path);assert base=='/home/egde/fangzhen_linux/third_party/IsaacLab-3.0.0-beta2.patch1/source/isaaclab';out=D/'SOURCE_FILES_READ_INDEX.json';assert not out.exists();c=connect72();s=c.open_sftp();rows=[]
try:
 for rel in('isaaclab/assets/articulation/articulation_data.py','isaaclab/assets/articulation/articulation.py'):
  remote=base+'/'+rel
  with s.open(remote,'rb')as f:raw=f.read()
  assert 0<len(raw)<4*1024**2;p=D/'editable_isaaclab'/rel;p.parent.mkdir(parents=True,exist_ok=True);assert not p.exists();p.write_bytes(raw);rows.append({'remote_path':remote,'local_copy':str(p),'bytes':len(raw),'SHA':hashlib.sha256(raw).hexdigest(),'byte_exact_no_Windows_EOL_translation':True})
finally:s.close();c.close()
v={'kind':'EXACT_ACTIVE_EDITABLE_SDK_ARTICULATION_SOURCE_NOT_RUNTIME_NUMERIC_PROOF','distribution_version':dist['version'],'active_origin_metadata':'ORIGIN_READ_RECEIPT.json','files':rows,'SDKimport_App_GPU_driver_PT_raw_canonical_calls':0};out.write_text(json.dumps(v,indent=2),encoding='utf-8');print(json.dumps(v,indent=2))
