"""005 authority remains unchanged; new entry scope pins approved diagnosis and own35 source."""
from pathlib import Path
from wave50_fullscope_source_guard import verify_original_records as old
def verify_original_records(q,D):
 old(q,D)
 d=q.w.read(D/'reports/COMPLETE147_ENTRY_AXIS_DECISION.json')
 assert d['candidate_forward_complete']==5 and d['candidate_reverse_complete']==25 and d['not_qualified50']
 assert d['new_entry_axis_approved'] and d['default_source_SHA']=='b026ade6c98f2f4e5d2cd4c9208cdbc9b0749a3f8df4e0b29f31f4495d3047bd'
