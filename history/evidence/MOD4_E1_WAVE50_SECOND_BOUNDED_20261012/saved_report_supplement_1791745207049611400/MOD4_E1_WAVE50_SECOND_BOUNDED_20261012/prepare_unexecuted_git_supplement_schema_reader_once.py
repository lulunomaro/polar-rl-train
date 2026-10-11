"""Continue only pre-capture supplement rejected by legacy index schema."""
from second50_io import *
import subprocess
assert subprocess.run(['git','-C',str(W/'polar-rl-train'),'status','--porcelain'],capture_output=True,text=True,check=True).stdout==''
assert not list((W/'polar-rl-train/history/evidence'/D.name).glob('saved_report_supplement_*'))
p=D/'archive_saved_delta_schema_reviewed_once.py';assert not p.exists()
text=(D/'archive_saved_delta_actual.py').read_text(encoding='utf8');before="for row in json.loads(p.read_bytes()).get('entries',[]):\n   if row.get('Git_path')"
after="for row in json.loads(p.read_bytes()).get('entries',[]):\n   if 'sha256' not in row:continue # Legacy other-project shape is not reused as coverage.\n   if row.get('Git_path')"
assert text.count(before)==1;text=text.replace(before,after);compile(text,str(p),'exec');p.write_text(text,encoding='utf8')
save('GIT_SUPPLEMENT_LEGACY_INDEX_SCHEMA_REJECTION_REVIEW.json',dict(epoch=time.time(),original_reader='archive_saved_delta_actual.py',original_KeyError_sha256_and_source_retained=True,106_other_project_legacy_rows_use_source_sha256_archive_path=True,repaired_reader=str(p),legacy_rows_not_reused_as_current_evidence_coverage=True,known_current_Git_path_archivedSHA_exact_validation_unchanged=True,rejection_before_capture_commit_push=True,original_stage_objects_047eb5ef_and459baf_preserved=True,only_unexecuted_ordinary_supplement_continued=True,no_GPU_training_budget_record_tag_replay=True))
print('Prepared independent known-schema supplement reader; original error retained')
