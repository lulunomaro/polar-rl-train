"""Only derive the parent-authorized metadata suffix correction; no freeze or native call."""
from pathlib import Path
import hashlib,json,difflib
O=Path(__file__).resolve().parent

def rec(p):
 b=p.read_bytes();return {'path':str(p),'bytes':len(b),'SHA':hashlib.sha256(b).hexdigest()}
old=O/'prepare_v8_once.py';new=O/'prepare_v8_suffix_repair001.py'
before=old.read_bytes();a=b'EXECUTION_LEDGER_V6_01.json\'';b=b'EXECUTION_LEDGER_V6_01.jsonl\''
assert hashlib.sha256(before).hexdigest()=='3a1a99e131b4988d0379b252f1281f39142c412ece37bd8878ed9ed499f29410'
assert before.count(a)==1
source=before.replace(a,b,1);assert source.replace(b,a,1)==before
assert not new.exists()
records=[]
for name in ('prepare_v8_once.py','prepare_01.log','PREPARATION_LEDGER_01.jsonl','PRE_NATIVE_STOP_RESULT_01.json','METHOD.md','PARENT_CONTINUATION_SCOPE.json','compile_v8_once.py'):
 current=O/name;snapshot=O/'revisions'/'prepare_attempt_01'/name
 assert current.read_bytes()==snapshot.read_bytes(),name
 records.append({'current':rec(current),'original_snapshot':rec(snapshot),'byte_equal':True})
new.write_bytes(source)
patch=''.join(difflib.unified_diff(before.decode('utf-8').splitlines(True),source.decode('utf-8').splitlines(True),fromfile='prepare_attempt_01/prepare_v8_once.py',tofile='prepare_v8_suffix_repair001.py'))
with (O/'PREPARER_SUFFIX_ONLY_001.patch').open('x',encoding='utf-8',newline='') as f:f.write(patch)
receipt={'status':'EXACT_ONE_METADATA_SUFFIX_DERIVATION_BEFORE_SECOND_FREEZE','parent_scope':rec(O/'PARENT_METADATA_SUFFIX_REPAIR_001.json'),'original_scope':rec(O/'PARENT_CONTINUATION_SCOPE.json'),'first_failure_records_unchanged':records,'old_preparer':rec(old),'new_preparer':rec(new),'patch':rec(O/'PREPARER_SUFFIX_ONLY_001.patch'),'exact_byte_inverse':True,'only_substitution':"EXECUTION_LEDGER_V6_01.json' -> EXECUTION_LEDGER_V6_01.jsonl'",'old_script_not_overwritten':True,'executor_or_compile_flags_changes':0,'metadata_freeze_runs_in_this_helper':0,'native_calls':0}
with (O/'SUFFIX_REPAIR_RECEIPT_001.json').open('x',encoding='utf-8',newline='\n') as f:json.dump(receipt,f,indent=2,ensure_ascii=False,allow_nan=False);f.write('\n')
print(json.dumps({'status':receipt['status'],'new_preparer':receipt['new_preparer'],'old_preparer':receipt['old_preparer'],'byte_inverse':True,'native':0}))
