from route_second_io import *
rows=[]
for src,dst in (('collect_resource449_candidate_actual.py','collect_resource449_postexit_candidate_actual.py'),('review_resource449_candidate_actual.py','review_resource449_postexit_candidate_actual.py'),('review_resource449_complete_dynamic_family_trace_actual.py','review_resource449_postexit_complete_trace_actual.py')):
    text=(D/src).read_text()
    if src.startswith('collect_'):
        a='e1_WAVE50_route_startup_resource_reviewed_observation_PASSED.json';b='e1_WAVE50_route_startup_resource_reviewed_observation_INDEPENDENT_POSTEXIT_PASSED.json'
    else:a='RESOURCE449_OWN_FORMAL_CPU_ACTUAL_';b='RESOURCE449_INDEPENDENT_OWN_FORMAL_CPU_ACTUAL_'
    assert a in text;text=text.replace(a,b);p=D/dst;assert not p.exists();compile(text,str(p),'exec');p.write_text(text,encoding='utf8');rows.append(dict(path=str(p),sha256=H(p.read_bytes())))
save('RESOURCE449_POSTEXIT_REVIEWED_READERS_PREPARED.json',dict(epoch=time.time(),passed=True,readers=rows,only_explicit_independent_postexit_receipt_source_selected=True,all_physical_schema_thresholds_raw_protocol_byte_source_unchanged=True,compiled_only_not_candidate_future_pass=True,no_GPU_or_budget_mutation=True))
print(json.dumps(dict(prepared=True,count=len(rows))))
