"""Exactown8dGPUrestoration certificate smallJSONonly, notPT/full32success claim."""
from pathlib import Path
import json,hashlib,datetime
from project_connector import connect72
R=Path(__file__).resolve().parent;d=json.loads((R/'reports/W35_after_resume89aca_eval_dispatch_20261102_070117.json').read_bytes());B=d['new_job'];source=d['new_source_model'];D=R/'staged_sources/W35_NEW8D_GPU_FULLRESTORE_CERTIFICATE_V1';assert not D.exists();D.mkdir();c=connect72();s=c.open_sftp()
try:
 with s.open(B+'/actual_latest32/FULLRESTORE227_BEFORE_CONTROL.json','rb')as f:raw=f.read()
 v=json.loads(raw);assert v['passed']and v['source_SHA']==source['SHA']and v['iteration']==32643 and v['Adam17']==654500 and v['actor_critic_STD_optimizer_verified'];(D/'FULLRESTORE227_BEFORE_CONTROL.json').write_bytes(raw);index={'kind':'ACTUAL_NEW8D_SOURCE_FULL20K_GPU_RESTORE_METADATA_NOT_FULL32_COMPLETION','remote_path':B+'/actual_latest32/FULLRESTORE227_BEFORE_CONTROL.json','bytes':len(raw),'SHA':hashlib.sha256(raw).hexdigest(),'newsource_model_SHA':source['SHA'],'iteration':v['iteration'],'Adam17':v['Adam17'],'actual_cached_source_LR':v['actual_LR'],'source_core_STD_optimizer_verified':v['actor_critic_STD_optimizer_verified'],'model_opens_or_raw_SDK_canonical_access_by_collector':False,'does_not_claim_full32_closed_or_RM70_graduation':True};(D/'CERTIFICATE_INDEX.json').write_text(json.dumps(index,indent=2),encoding='utf-8');print(json.dumps(index,indent=2))
finally:s.close();c.close()
