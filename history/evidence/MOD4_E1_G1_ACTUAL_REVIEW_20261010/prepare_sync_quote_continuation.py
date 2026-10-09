"""Preserve rejected sync; continue only its not-yet-executed CAS after exact uploaded bytes."""
from pathlib import Path
import ast,json,time
D=Path(__file__).resolve().parent;R=D/'reports'
error=json.loads((R/'POSTWINDOW_METADATA_SYNC_ERROR.json').read_bytes());assert 'SyntaxError: unterminated string literal' in error['error']
s=(D/'sync_postwindow_actual_once.py').read_text(encoding='utf8')
s=s.replace('POSTWINDOW_METADATA_SYNC_STARTED','POSTWINDOW_METADATA_FINISH_STARTED').replace('POSTWINDOW_METADATA_SYNC_ERROR','POSTWINDOW_METADATA_FINISH_ERROR').replace('E1-G1-POSTWINDOW-METADATA-02','E1-G1-POSTWINDOW-METADATA-QUOTE-CONTINUATION-03')
bad="   with f.open(E+'/'+name,'wbx') as out:out.write(raw)\n   assert f.open(E+'/'+name).read()==raw"
assert s.count(bad)==1;s=s.replace(bad,"   assert f.open(E+'/'+name).read()==raw,('Already uploaded payload differs; no rewrite',name)")
assert s.count("code='''")==1;s=s.replace("code='''","code=r'''")
ast.parse(s);p=D/'finish_postwindow_sync_quote_reviewed_once.py';assert not p.exists();p.write_text(s,encoding='utf8')
(R/'SYNC_QUOTE_REJECTION_REVIEW.json').write_text(json.dumps(dict(epoch=time.time(),trial_id='E1-G1-POSTWINDOW-METADATA-QUOTE-REVIEW-03',original_sync_rejection_retained=True,uploaded_reports_bytes_verified_before_reuse=True,original_remote_code_SyntaxError_before_any_CAS_or_current_or_handoff_write=True,new_continuation_only_for_unexecuted_metadata_operations=True,no_GPU_PPO_runtime_or_budget_mutation=True),indent=2),encoding='utf8')
