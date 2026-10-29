from pathlib import Path
import ast,hashlib,json,time
N=Path(__file__).resolve().parent;Q=N.parent/'MOD4_H1_OVERNIGHT_FUDAN_SUPERMIMIC_REPAIR_GOAL_20261027/TWO116_DIRECT_COMMAND_FIRST_CLOSING_INITIAL_CPU_SOURCE_V1'
rows=[]
for seed in ('seed27','seed28'):
    old=Q/('review_NEW116_'+seed+'_formal_initial_whole_CPU_UNUSED_once.py');raw=old.read_bytes();a=('payloads_v2/'+seed).encode();b=('payloads/'+seed).encode();assert raw.count(a)==1
    new=raw.replace(a,b);assert new.replace(b,a)==raw;ast.parse(new.decode('utf8'))
    target=Q/('review_NEW116_'+seed+'_formal_initial_whole_CPU_PATH_V2_UNUSED_once.py');assert not target.exists();target.write_bytes(new)
    witness=N/'payloads'/seed/'job0/source/H1_closed86_policy_only_update138.pt';assert witness.is_file()
    rows.append(dict(original=str(old),original_SHA=hashlib.sha256(raw).hexdigest(),selected=str(target),selected_SHA=hashlib.sha256(new).hexdigest(),only_actual_payload_directory_changed=True,witness_path=str(witness),witness_bytes=witness.stat().st_size,no_model_content_read=True))
old=Q/'review_TWO116_NEW_fudan270_formals_shared_witness_initial_CPU_UNUSED_once.py';raw=old.read_bytes();new=raw.replace(b"'_formal_initial_whole_CPU_UNUSED_once.py'",b"'_formal_initial_whole_CPU_PATH_V2_UNUSED_once.py'").replace(b'TWO116_INITIAL_TWO_FORMAL_CPU_CONSUMED_ACTUAL.json',b'TWO116_INITIAL_TWO_FORMAL_CPU_CONSUMED_PATH_V2_ACTUAL.json')
assert new!=raw and new.replace(b"'_formal_initial_whole_CPU_PATH_V2_UNUSED_once.py'",b"'_formal_initial_whole_CPU_UNUSED_once.py'").replace(b'TWO116_INITIAL_TWO_FORMAL_CPU_CONSUMED_PATH_V2_ACTUAL.json',b'TWO116_INITIAL_TWO_FORMAL_CPU_CONSUMED_ACTUAL.json')==raw
target=Q/'review_TWO116_NEW_fudan270_formals_shared_witness_initial_CPU_PATH_V2_UNUSED_once.py';assert not target.exists();target.write_bytes(new)
with (Q/'reports/INITIAL116_ORIGINAL_PATH_REFUSAL_AND_EXACT_PATH_V2_SOURCE_REPAIR.json').open('x',encoding='utf8') as f:json.dump(dict(epoch=time.time(),original_failed_before_any_checkpoint_decode=True,original_missing_witness_path_not_a_failed_model=False,decoded_model_or_witness_before_fix=0,rows=rows,selected_wrapper=str(target),no_reader_guard_relaxation=True),f,indent=2)
print(json.dumps(dict(source_only=True,selected=str(target),checkpoint_reads=0)))
