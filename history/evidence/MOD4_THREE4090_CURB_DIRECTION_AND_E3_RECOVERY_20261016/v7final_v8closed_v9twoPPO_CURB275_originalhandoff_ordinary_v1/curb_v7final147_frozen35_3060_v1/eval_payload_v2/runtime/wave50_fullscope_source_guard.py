"""005 authorization and exact own35mm/ancestry binding for new50mm scope."""
from pathlib import Path
from wave_budget005_source_guard import verify_original_records as original
SOURCE_SHA='b026ade6c98f2f4e5d2cd4c9208cdbc9b0749a3f8df4e0b29f31f4495d3047bd'
ANCESTOR_SHA='3c97c14e91a5483d03cb979cd0de0858f7fd1f2a1758e8469c88b7546b02921e'
def verify_original_records(q,D):
 original(q,D)
 row=q.w.read(D/'reports/SOURCE_SELECTED.json');assert row['sha256']==SOURCE_SHA and q.base.sha(Path(row['path']))==SOURCE_SHA
 old=q.w.read(D/'reports/OWN369_ACTUAL_SOURCE_BOUNDARY.json');assert old['complete129_ancestor_SHA']==ANCESTOR_SHA and old['own_source_SHA']==SOURCE_SHA and old['actual_old_fullsave_PASSED_and_unique_closed']
 b=q.base.budget_state();assert b['authorized_training_seconds']==1188000 and len(b['budget_extensions'])==7
 assert b['remaining_training_seconds']>120
