from wave_direction_io import *
import ast
s=(PRIOR/'review_entry_second_direct148_prefix_actual.py').read_text().replace('from entry_second_io import *','from wave_direction_io import *').replace('from review_entry_second_candidate_actual import','from review_direction_candidate_actual import')
s=s.replace("ENTRY_LOCAL/'reports/ENTRY148_COMPLETE_SCOPE_DECISION.json'","PRIOR/'reports/CANDIDATE149_COMPLETE_SCOPE_DECISION.json'")
s=s.replace("source['own']['checkpoint']['sha256']==SOURCE_SHA","source['own']['checkpoint']['sha256']==before['own_checkpoint']['sha256']=='9bfe7655b8a641660548c2a62d2ac3151e25bdf1f0e943d529099c017a2e986e'")
s=s.replace('ENTRY_SECOND_CANDIDATE_ACTUAL_REVIEW','DIRECTION_CANDIDATE_ACTUAL_REVIEW').replace('ENTRY_SECOND_DIRECT148_PREFIX_ACTUAL','DIRECTION_DIRECT149_PREFIX_ACTUAL').replace('source148','source149').replace('direct148','direct149').replace('DIRECT148_PREFIX_READER_ERROR','DIRECT149_PREFIX_READER_ERROR')
ast.parse(s);p=D/'review_direction_direct149_prefix_actual.py';assert not p.exists();p.write_text(s,encoding='utf8',newline='\n')
s=(PRIOR/'archive_entry_second_saved_supplement_actual.py').read_text().replace('from entry_second_io import *','from wave_direction_io import *').replace('for folder in (D,ENTRY_LOCAL):','for folder in (D,):').replace('Append Wave50 complete148 and source412 sameentry actual startup evidence','Append Wave50 source424 direction actual receipts and preserved preparation errors')
ast.parse(s);p=D/'archive_direction_saved_supplement_actual.py';assert not p.exists();p.write_text(s,encoding='utf8',newline='\n')
save('DIRECT149_AND_DELTA_READERS_PREPARED_ONLY.json',dict(epoch=time.time(),direct149_prepared_not_future_pass=True,ordinary_supplement_uses_actual_new_delta_no_record_or_tag_replay=True))
print(json.dumps(dict(prepared=True,no_future_pass=True)))
