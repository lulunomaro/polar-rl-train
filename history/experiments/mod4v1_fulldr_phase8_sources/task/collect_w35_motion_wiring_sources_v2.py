"""Second targeted small-source set: exact command/obs/reward/action wiring; no model/raw/SDK."""
from pathlib import Path
import json,hashlib,datetime
from project_connector import connect72
R=Path(__file__).resolve().parent;D=R/'diagnostics/W35_MOTION_WIRING_SOURCE_V2';assert not D.exists();D.mkdir(parents=True);d=json.loads(sorted((R/'reports').glob('W35_adaptation_dispatch_*.json'))[-1].read_bytes());root=d['new_job']+'/runtime/isaac/mod4';rows=[];c=connect72();s=c.open_sftp()
try:
 for name in ('learning208_v3.py','terrain208_v3.py','e1_scene_query_resource.py','scut_flat_rescue.py','retained_flat_command_math.py','config_mod4v1_w35.py','fixed_si_observations.py','e1_fieldset.py'):
  try:
   st=s.stat(root+'/'+name);assert st.st_size<2000000
   with s.open(root+'/'+name,'rb')as f:raw=f.read()
  except FileNotFoundError:rows.append({'name':name,'present':False});continue
  (D/name).write_bytes(raw);rows.append({'name':name,'present':True,'bytes':len(raw),'SHA':hashlib.sha256(raw).hexdigest(),'source_path':root+'/'+name})
finally:s.close();c.close()
v={'kind':'TARGETED_OWN_COMPLETED_W35_COMMAND_OBS_REWARD_ACTION_SOURCE_READONLY_V2','rows':rows,'PT_raw_or_SDK_or_canonical_access':False,'target_source_executed_or_mutated':False};(D/'SOURCE_READ_RECEIPT.json').write_text(json.dumps(v,indent=2),encoding='utf-8');print(json.dumps(v,indent=2))
