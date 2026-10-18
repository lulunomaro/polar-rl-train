from pathlib import Path
import ast,json,time
B=Path(__file__).resolve().parent
s=(B/'archive_fifth_hour_three_closed_sources_unique_once.py').read_text('utf-8')
assert "'actual_third_hour_closed_sources/REPORT_CAPTURE_INDEX.json'" in s
s=s.replace("'actual_third_hour_closed_sources/REPORT_CAPTURE_INDEX.json'","'actual_fourth_hour_closed_sources/REPORT_CAPTURE_INDEX.json'")
ast.parse(s)
with (B/'archive_fifth_hour_three_closed_sources_V2_unique_once.py').open('x',encoding='utf-8') as f:f.write(s)
(B/'reports/FIFTH_ARCHIVE_INDEX_LOOKUP_FIX_V2_PREPARED.json').write_text(json.dumps(dict(epoch=time.time(),
    original_failure_before_note_DEST_record_commit_tag=True,corrected_actual_prior_index_only=True,
    no_GPU_model_or_account_change=True),indent=2),encoding='utf-8')
