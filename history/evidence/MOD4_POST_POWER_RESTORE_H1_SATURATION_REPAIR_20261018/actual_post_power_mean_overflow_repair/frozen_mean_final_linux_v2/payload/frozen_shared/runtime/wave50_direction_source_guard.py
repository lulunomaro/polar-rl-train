"""005 and the accepted35 initial source remain strict; complete149 pins a new direction axis."""
from wave50_entry_source_guard import verify_original_records as old
def verify_original_records(q,D):
 old(q,D)
 a=q.w.read(D/'reports/COMPLETE149_DIRECTION_AXIS_DECISION.json')
 assert a['all_four_actual_complete_errorfree_fullraw_reviewed'] and a['candidate_forward_complete']==1 and a['candidate_reverse_complete']==25
 assert a['E0_and_accepted_CURB20_WAVE35_SLOPE_frozen_gate_untrained']
