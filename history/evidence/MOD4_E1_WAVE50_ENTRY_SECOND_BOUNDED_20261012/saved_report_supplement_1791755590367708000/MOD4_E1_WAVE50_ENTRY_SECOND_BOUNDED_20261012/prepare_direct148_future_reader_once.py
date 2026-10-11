"""Prepare original physical prefix comparison, bind complete148 actual field names."""
from entry_second_io import *
text=(W/'MOD4_E1_WAVE50_SECOND_BOUNDED_20261012/review_second50_direct146_prefix_actual.py').read_text().replace('from second50_io import *','from entry_second_io import *').replace('from review_second50_candidate_actual import','from review_entry_second_candidate_actual import').replace('SECOND50_CANDIDATE_ACTUAL_REVIEW_','ENTRY_SECOND_CANDIDATE_ACTUAL_REVIEW_')
text=text.replace("PRIOR/'reports/WAVE50_146_COMPLETE_SCOPE_DECISION.json'","ENTRY_LOCAL/'reports/ENTRY148_COMPLETE_SCOPE_DECISION.json'").replace("before['collection']","before['actual_collection']").replace("before['review']","before['full_actual_review']").replace('SECOND50_DIRECT146','ENTRY_SECOND_DIRECT148').replace('DIRECT146','DIRECT148').replace('direct146','direct148').replace('source146','source148')
compile(text,'future-direct148','exec');p=D/'review_entry_second_direct148_prefix_actual.py';assert not p.exists();p.write_text(text,encoding='utf8',newline='\n')
save('DIRECT148_FUTURE_READER_PREPARED.json',dict(epoch=time.time(),path=str(p),sha256=H(p.read_bytes()),complete148_source_SHA=SOURCE_SHA,ownfuture_fullcandidate_only=True,original1N_allprefix_and_unchanged_window_contract=True,prepared_not_future_pass=True))
print(json.dumps(dict(prepared=True,future_pass_not_claimed=True)))
