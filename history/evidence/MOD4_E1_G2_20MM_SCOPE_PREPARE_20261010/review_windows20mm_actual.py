"""Independent CPU review of actual3060 20mm output, explicitly without central bridge equivalence."""
from pathlib import Path
import json,time,traceback,hashlib
from review20mm_allowlist_actual import audit
D=Path(__file__).resolve().parent;R=D/'reports'
def main():
 v=json.loads(sorted(R.glob('WINDOWS_VERSIONED_ACTUAL_*.json'))[-1].read_bytes());assert v['central_bridge_bytes_not_yet_verified'] and v['current_attention'] is None
 assert len(v['cases'])==1 and not v['pending'];reviews={}
 for jid,row in v['cases'].items():
  p,m,r=row['probe'],row['manifest'],row['result'];assert row['raw_SHA_exact']
  assert r['checkpoint']['sha256']==m['artifacts']['checkpoint']['sha256']==p['checkpoint_sha256']=='655a36b78926bc17d4230996fe152b62d0f997f3037105d5247582697440481f'
  assert r['runtime_archive_sha256']==m['artifacts']['runtime']['sha256']=='c4255fe5c3407a42019416fdffa6d6786a51b84ae4312f6e362e2b2a60ba1271'
  assert m['no_learning'] and not m['canonical_write_authority'] and r['exit_code']==0 and not r['errors'] and not r['error_files']
  reviews[jid]=audit(p,R/'windows_independent'/jid)
 summary={k:dict(groups=x['groups'],ordinary=x['base_review']['ordinary'],closure_mm=x['base_review']['closure_mm']) for k,x in reviews.items()}
 report=dict(epoch=time.time(),trial_id='E1-G2-WINDOWS-CPU-FULLROUTE-REVIEW-01',input_report=str(sorted(R.glob('WINDOWS_VERSIONED_ACTUAL_*.json'))[-1]),review=reviews,summary=summary,actual3060_model_data_ground_contact_and_fullroute_independently_reviewed=True,central_bridge_bytes_NOT_yet_verified=True,no_native20k_PPO_or_learning_admission=True,not_RM70mm_or_fullE1_graduation=True,new_budget_seconds=0)
 out=R/('WINDOWS_20MM_CPU_REVIEW_'+str(int(report['epoch']))+'.json');assert not out.exists();out.write_text(json.dumps(report,indent=2),encoding='utf8');print(json.dumps(dict(report=str(out),summary=summary,central_bridge_bytes_not_yet_verified=True)))
if __name__=='__main__':
 try:main()
 except Exception:
  out=R/('WINDOWS_20MM_CPU_REVIEW_ERROR_'+str(int(time.time()))+'.json');assert not out.exists();out.write_text(json.dumps(dict(epoch=time.time(),trial_id='E1-G2-WINDOWS-CPU-FULLROUTE-READER-01',error=traceback.format_exc(),reader_only_no_production_mutation=True),indent=2),encoding='utf8');raise
