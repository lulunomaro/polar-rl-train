"""ReadexactW35v2producerandS50complete-save metadata once, noPT/raw/SDK/C. Currentgenericcollector'solderW35markerlistisnotproofrestoreabsent."""
from pathlib import Path
import json,sys
D=Path(__file__).resolve().parent;sys.path.insert(0,str(D.parent));from project_connector import connect72
out=D/'reports/PAIR4_EXACT_ACTUAL_RUNTIME_PROGRESS_METADATA_ONCE.json';assert not out.exists();r=json.loads((D/'PAIR4_GENERIC_V2_ORIGINAL_OWNER_DISPATCH_ONCE.json').read_bytes());root=r['root'];c=connect72();s=c.open_sftp();data={}
try:
 paths=['roles/W35/production/'+n for n in('ACTUAL_W35_RM70_V3_FULLSTATE_BEFORE_NEW_CONTROL.json','NATIVE24_W35_RM70_V3_ACTUAL.json','LATEST_PROGRESS.json','latest_complete.json','ORIGINAL_W35_RM70_V3_ERROR.json')]
 try:
  folder='roles/SLOPE_INDEPENDENT50/production/';names=sorted(n for n in s.listdir(root+'/'+folder)if n.startswith('COMPLETE_CHECKPOINT_RECEIPT_')and n.endswith('.json'))
  if names:paths.append(folder+names[-1])
 except FileNotFoundError:pass
 for rel in paths:
  try:
   with s.open(root+'/'+rel,'rb')as f:data[rel]=json.loads(f.read())
  except FileNotFoundError:data[rel]=None
finally:s.close();c.close()
v=dict(kind='EXACT_OWN_PRODUCER_RUNTIME_PROGRESS_NOT_INFERRED_FROM_GENERIC_MARKER',root=root,metadata=data,modelstat_hash_read_raw_SDK_C_replay=0);out.write_text(json.dumps(v,indent=2),encoding='utf-8');print(out);print(json.dumps(v,indent=2))
