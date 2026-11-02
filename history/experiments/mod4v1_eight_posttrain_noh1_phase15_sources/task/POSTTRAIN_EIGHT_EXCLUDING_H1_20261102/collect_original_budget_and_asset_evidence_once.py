"""Readonly original deployed SOURCE+small actual evidence; no PT/modelstat/raw/SDK/authority writes."""
from pathlib import Path
import json,hashlib,sys,datetime
R=Path(__file__).resolve().parent.parent;sys.path.insert(0,str(R));from project_connector import connect72
D=Path(__file__).resolve().parent/'parent_source/original_budget_and_asset_refs';assert not D.exists();D.mkdir();root='/home/lc01/Zonglin Li/zonglin2/tasks/MOD4V1_W35_RESUME89ACA_WAIT_V4_20261102_054158_1793569318385718000';names=['three_slot_common_v1.py','single_writer72_authority_V85M_source.py','evidence/NEW_ASSET_NATIVE_ACTUAL.json','evidence/NEW_TARGET_SDK_FULL32_ACTUAL.json','evidence/RM70_SCOPE_REUSE_ACTUAL.json'];c=connect72();s=c.open_sftp();rows=[]
try:
 for rel in names:
  remote=root+'/'+rel;st=s.stat(remote);assert st.st_size<=5000000,(rel,st.st_size)
  with s.open(remote,'rb')as f:raw=f.read()
  assert len(raw)==st.st_size;p=D/rel;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(raw);row={'remote_source':remote,'relative':rel,'bytes':len(raw),'SHA':hashlib.sha256(raw).hexdigest(),'local':str(p)};rows.append(row)
finally:s.close();c.close()
report={'kind':'EXACT_ORIGINAL_DEPLOYED_BUDGET_HELPERS_AND_ACTUAL_ASSET_PROOF_METADATA_ONLY','rows':rows,'source_models_stat_hash_decode':0,'raw_SDK_canonical_or_GO_operations':0,'no_Ready_or_newtraining_pass_inferred':True};p=D/'INDEX.json';p.write_text(json.dumps(report,indent=2),encoding='utf-8');print(p);print(json.dumps(report,indent=2))
