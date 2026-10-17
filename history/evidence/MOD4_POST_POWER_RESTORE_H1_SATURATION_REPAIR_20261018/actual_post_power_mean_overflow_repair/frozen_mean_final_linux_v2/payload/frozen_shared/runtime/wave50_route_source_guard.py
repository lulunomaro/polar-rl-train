from wave50_direction_source_guard import verify_original_records as original
def verify_original_records(q,D):
 original(q,D);a=q.w.read(D/'reports/COMPLETE151_ROUTE_AXIS_DECISION.json')
 assert a['all_four_actual_complete_errorfree_fullraw_reviewed'] and a['forward_complete']==9 and a['reverse_complete']==26
 assert a['default_source_SHA']=='b026ade6c98f2f4e5d2cd4c9208cdbc9b0749a3f8df4e0b29f31f4495d3047bd' and a['new_route_only_scope_authorized_by004005']
