from pathlib import Path
import json,hashlib
from wave50_route_source_guard import verify_original_records as original
INIT_SHA='68401cae6402c5aa38797dabdbb7043f8036ed6fcbacd9c34fda0bdd95a813c5'
ORIGINAL35_SHA='b026ade6c98f2f4e5d2cd4c9208cdbc9b0749a3f8df4e0b29f31f4495d3047bd'

def verify_original_records(q,D):
 original(q,D);b=q.w.read(q.ctl.CANONICAL);ids=set();total=36000
 for r in b['budget_extensions']:
  assert r['extension_id'] not in ids and r['state']=='applied' and r['authorization_basis']=='explicit_user_request'
  ids.add(r['extension_id']);assert type(r['additional_training_seconds']) is int and r['additional_training_seconds']>0;total+=r['additional_training_seconds']
 assert total==b['authorized_training_seconds']==1188000 and len(ids)==7
 a=q.w.read(D/'reports/COMPLETE152_ROUTE_SECOND_SCOPE_DECISION.json')
 assert a['all_four_actual_complete_errorfree_fullraw_reviewed'] and a['full_own_training_trace_reviewed'] and a['default_same_scope_source_SHA']==INIT_SHA
 assert a['forward_complete']==12 and a['reverse_complete']==25 and a['bounded_second1800_justified_after_first300_short_exposure']
 assert a['no_third_blind_block_or70'] and not a['qualified50']
