"""Oneactualcomplete-saveproducerprogressread; no .ptstat/hash/read, raw, SDK, C orreplay."""
from pathlib import Path
import json,sys
D=Path(__file__).resolve().parent;sys.path.insert(0,str(D.parent));from project_connector import connect72
out=D/'reports/PAIR3_ACTUAL_LATEST_COMPLETE_SAVE_PROGRESS_METADATA_ONCE.json';assert not out.exists();r=json.loads((D/'PAIR3_GENERIC_V2_ORIGINAL_OWNER_DISPATCH_ONCE.json').read_bytes());root=r['root'];c=connect72();s=c.open_sftp();rows=[]
try:
 for role in r['roles']:
  folder=root+'/roles/'+role+'/production';rel='latest_complete.json'
  if role=='SLOPE135':
   names=sorted(n for n in s.listdir(folder)if n.startswith('COMPLETE_CHECKPOINT_RECEIPT_')and n.endswith('.json'));rel=names[-1]if names else None
  value=None
  if rel:
   try:
    with s.open(folder+'/'+rel,'rb')as f:value=json.loads(f.read())
   except FileNotFoundError:pass
  rows.append(dict(role=role,published_save_receipt_path=folder+'/'+rel if rel else None,published_save_receipt=value))
finally:s.close();c.close()
v=dict(kind='ACTUAL_NEW_COMPLETE_SAVE_PRODUCER_PROGRESS_NOT_ROLLOUT_OR_INFERRED_PPO',root=root,rows=rows,model_stat_hash_read_SDK_raw_C_or_replay_operations=0);out.write_text(json.dumps(v,indent=2),encoding='utf-8');print(out);print(json.dumps(v,indent=2))
