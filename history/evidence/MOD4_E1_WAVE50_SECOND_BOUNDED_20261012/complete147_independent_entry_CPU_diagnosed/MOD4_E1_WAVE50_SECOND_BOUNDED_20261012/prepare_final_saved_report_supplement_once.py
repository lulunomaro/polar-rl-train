"""Prepare a new ordinary report supplement; no old archive once is replayed."""
from second50_io import *
p=D/'archive_final147_saved_supplement_actual.py';assert not p.exists()
text=(D/'archive_saved_delta_schema_reviewed_once.py').read_text(encoding='utf8');before='Append Wave50 second386 Git receipt and future direct146 reader evidence';assert text.count(before)==1;text=text.replace(before,'Append Wave50 own386 complete final, trace and candidate147 actual review evidence')
compile(text,str(p),'exec');p.write_text(text,encoding='utf8')
save('FINAL_SAVED_REPORT_SUPPLEMENT_PREPARED.json',dict(epoch=time.time(),source_path=str(p),source_SHA=H(p.read_bytes()),ordinary_supplement_only=True,no_new_trial_tag_or_old_record_archive_once_replay=True,known_current_capture_schema_validation_unchanged=True,large_originals_only_actualpathsizeSHA=True))
print('Prepared new final/candidate ordinary supplement; no previous archive replay')
