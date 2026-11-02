"""One later bounded connect/stat of EXACT recorded7b path; no modelbyte/hash/decode."""
from pathlib import Path
import datetime,json,sys,traceback
B=Path(__file__).resolve().parent;T=B.parent;sys.path.insert(0,str(T));from project_connector import connect_original
path='/home/egde/rl_candidates/MOD4_S3_E1_CURB20_DIRECTION_EXPOSURE_MATCHED_20261011/learning_logs/2026-10-11_19-52-45_e1_CURB20_direction_exposure_matched_observation_1791719370686304629/model_32114.pt'
r=dict(kind='CURB141_EXACT_ORIGINAL_PATH_LATER_METADATA_RETRY',path=path,expected_SHA='7b70032fcb577390cee01c887b57c1e3d9818f9bf87f54977444d592c033db43',source_byte_reads_hashes_decodes=0,no_alternate_actor_or_latest_search=True);c=sf=None
try:
 c=connect_original();sf=c.open_sftp()
 try:s=sf.stat(path);r.update(status='EXACT_PATH_STAT_EXISTS_NO_CONTENT_READ',exists=True,bytes=s.st_size,mtime=s.st_mtime)
 except OSError as e:
  if getattr(e,'errno',None)!=2:raise
  r.update(status='EXACT_PATH_STAT_MISSING',exists=False,errno=2)
except BaseException:r.update(status='ORIGINAL_NODE_NETWORK_STAT_NOT_OBTAINED_NOT_CLAIMED_MISSING',error=traceback.format_exc());raise
finally:
 if sf:sf.close()
 if c:c.close()
 out=T/'reports'/('CURB141_exact_original_metadata_retry_v3_'+datetime.datetime.now().strftime('%Y%m%d_%H%M%S')+'.json');out.write_text(json.dumps(r,ensure_ascii=False,indent=2),encoding='utf-8')
 with (B/'CURB141_EXACT_ORIGINAL_METADATA_V3.json').open('x',encoding='utf-8') as f:json.dump(r,f,ensure_ascii=False,indent=2)
 print(json.dumps(dict(report=str(out),data=r),ensure_ascii=False,indent=2))
