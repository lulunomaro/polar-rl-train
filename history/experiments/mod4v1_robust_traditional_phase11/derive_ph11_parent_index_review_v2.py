"""Narrow fix: own read-only Git JSONL ledger is metadata, not physics raw."""
from pathlib import Path
import ast,json,hashlib
R=Path(__file__).resolve().parent;old=R/'review_ph11_parent_index_and_allowlist_v1.py';new=R/'review_ph11_parent_index_and_allowlist_v2.py';note=R/'PH11_PARENT_INDEX_REVIEW_LEDGER_ERRATUM_002.json'
assert not new.exists()and not note.exists()
s=old.read_text(encoding='utf-8');before="assert p.suffix.lower()not in('.jsonl','.o','.axf','.lib','.zip','.exe','.bin','.usd','.usda','.usdc','.tgz','.pyc'),str(p)";after="assert p.suffix.lower()not in('.jsonl','.o','.axf','.lib','.zip','.exe','.bin','.usd','.usda','.usdc','.tgz','.pyc') or (p==(P/'GIT_READONLY_LEDGER.jsonl').resolve() and p.stat().st_size<65536),str(p)"
assert s.count(before)==1 and s.count('PH11_PARENT_INDEX_REVIEW_V1')==2
v=s.replace(before,after).replace('PH11_PARENT_INDEX_REVIEW_V1','PH11_PARENT_INDEX_REVIEW_V2')
assert v.replace(after,before).replace('PH11_PARENT_INDEX_REVIEW_V2','PH11_PARENT_INDEX_REVIEW_V1')==s
ast.parse(v)
with new.open('x',encoding='utf-8',newline='\n')as f:f.write(v)
receipt=dict(status='NEW_PARENT_OWN_METADATA_LEDGER_CLASSIFICATION_FIX_NOT_SOURCE_OR_POLICY_CHANGE',old_script_SHA=hashlib.sha256(old.read_bytes()).hexdigest(),new_script_SHA=hashlib.sha256(new.read_bytes()).hexdigest(),old_error_preserved='PH11_PARENT_INDEX_REVIEW_V1_ERROR.json',old_error_owned_text_reads32_no_original_payload=True,exact_one_exception='SOURCE_PREPARATION/GIT_READONLY_LEDGER.jsonl <65536B; actual18rows read; allotherphysical jsonl and binaries still forbidden',review_INDEX_list_has_only_one_true_jsonl_and_five_jsonl_txt_text_logs=True,byte_inverse_exact=True,only_other_change='New V2 output/error names; originalV1 not overwritten/reexecuted',source_snapshot_or_controller_or_originals_modified=False,new_model_PHY_QA_Git_calls=0)
with note.open('x',encoding='utf-8',newline='\n')as f:json.dump(receipt,f,indent=2);f.write('\n')
print(json.dumps(receipt,indent=2))
