"""Keep the local V1 report-hash ABI error; create a new unused ordinary entry."""
from pathlib import Path
import json
import time

N = Path(__file__).resolve().parent
R = N / 'reports'
partial = R / 'SOURCE_ONLY81_MONITOR_V2_UPDATED_EXACT_PREARCHIVE_ACTUAL.json'
assert partial.exists() and partial.stat().st_size == 0
source = (N / 'archive_source_only81_same_journal_preparation_ordinary_unused_once.py').read_text('utf8')
assert source.count('source_SHA=H(source)') == 1
source = source.replace('source_SHA=H(source)', 'source_SHA=H(source.read_bytes())', 1)
assert source.count('SOURCE_ONLY81_MONITOR_V2_UPDATED_EXACT_PREARCHIVE_ACTUAL.json') == 1
source = source.replace('SOURCE_ONLY81_MONITOR_V2_UPDATED_EXACT_PREARCHIVE_ACTUAL.json', 'SOURCE_ONLY81_MONITOR_V2_UPDATED_EXACT_PREARCHIVE_V2_ACTUAL.json', 1)
with (N / 'archive_source_only81_same_journal_preparation_ordinary_v2_unused_once.py').open('x', encoding='utf8', newline='\n') as f:
    f.write(source)
with (R / 'ORDINARY81_LOCAL_HASH_HELPER_ABI_ERROR_CLASSIFICATION_AND_V2_SOURCE_ACTUAL.json').open('x', encoding='utf8') as f:
    json.dump(dict(epoch=time.time(), original_error='V1 passed pathlib.Path to archive utility H(bytes), TypeError before capture destination or Git mutation', original_V1_preserved=True, original_empty_partial_report=str(partial), original_empty_bytes=0, V2_only_changes='Read the local monitor source bytes before H, and use a new exclusive receipt filename', no_training_or_remote_model_or_budget_error=True, no_same_once_retry_or_trial_tag=True), f, indent=2)
print(json.dumps(dict(new_unused_ordinary_archiver_V2_ready=True, original_error_retained=True)))
