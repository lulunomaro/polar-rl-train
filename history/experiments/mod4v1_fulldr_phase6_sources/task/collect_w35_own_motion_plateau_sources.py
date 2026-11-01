"""Read only small Python/manifest files from this own completed producer case to diagnose velocity plateau.
No checkpoint/telemetry/budget reads, no imports of target source or SDK.
"""
from pathlib import Path
import json,hashlib,datetime
from project_connector import connect72
R=Path(__file__).resolve().parent;D=R/'diagnostics/W35_MOTION_PLATEAU_SOURCE_V1';assert not D.exists();D.mkdir(parents=True);d=json.loads(sorted((R/'reports').glob('W35_adaptation_dispatch_*.json'))[-1].read_bytes());job=d['new_job'];rows=[];c=connect72();s=c.open_sftp()
try:
 for rel in ('runtime/isaac/mod4/command208_v3.py','train/command208_v3.py','command208_v3.py','lib/command208_v3.py','runtime/isaac/mod4/train_mod4v1_w35.py','runtime/isaac/mod4/mod4_task.py','runtime/isaac/mod4/mod4_observations.py','runtime/isaac/mod4/physics_clock.py','runtime/isaac/mod4/field214.py','field214.py','original_run_manifest.json'):
  try:
   st=s.stat(job+'/'+rel);assert st.st_size<2000000
   with s.open(job+'/'+rel,'rb')as f:raw=f.read()
  except FileNotFoundError:rows.append({'relative':rel,'present':False});continue
  dest=D/rel;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(raw);rows.append({'relative':rel,'present':True,'bytes':len(raw),'SHA':hashlib.sha256(raw).hexdigest(),'source_path':job+'/'+rel,'local_copy':str(dest)})
finally:s.close();c.close()
v={'kind':'OWN_W35_COMPLETED_PRODUCER_SMALL_SOURCE_READONLY','captured_local':datetime.datetime.now().astimezone().isoformat(),'job':job,'rows':rows,'PT_raw_or_SDK_or_canonical_access':False,'source_executed':False,'motivation':'PPO80 reduces basecontacts918to128 but newfull32 completecommands >=.1m/s all9122outsideoldbound and meanalong.0280m/s; inspect sourcecommand/observation/reward/action/routewiring beforeblindnewwindow'};p=D/'SOURCE_READ_RECEIPT.json';p.write_text(json.dumps(v,ensure_ascii=False,indent=2),encoding='utf-8');print(json.dumps(v,ensure_ascii=False,indent=2))
