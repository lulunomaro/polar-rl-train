"""Continue only missing request; disclose Windows line endings and earlier errors."""
from pathlib import Path
import json,time,tomllib,hashlib
D=Path(__file__).resolve().parent;R=D/'reports';H=lambda b:hashlib.sha256(b).hexdigest()
old=D/'MONITOR_CURRENT_410_FINAL_PROMPT.md';new=D/'MONITOR_CURRENT_410_FINAL_BYTE_VERIFIED_PROMPT.md';assert new.exists()
final=json.loads((R/'ENTRY_SEED_FORMAL_FINAL_ACTUAL_REVIEW_1791705848191384400.json').read_bytes());assert final['checkpoint_bytes']==17616498
t=tomllib.loads(Path('C:/Users/lulu/.codex/automations/mod4-10/automation.toml').read_text(encoding='utf8'));assert t['prompt'].replace('\r\n','\n')==old.read_text(encoding='utf8') and t['rrule']=='FREQ=MINUTELY;INTERVAL=30' and t['status']=='ACTIVE'
text=new.read_text(encoding='utf8');assert '/17616498bytes/CPU102' in text
request=dict(epoch=time.time(),id=t['id'],kind=t['kind'],name=t['name'],status=t['status'],rrule=t['rrule'],target_thread_id=t['target_thread_id'],prior_prompt_actual_string_SHA=H(t['prompt'].encode()),new_prompt_normalized_string_SHA=H(text.encode()),original_checkpoint_byte_metadata_error=17615794,actual_own_checkpoint_bytes=17616498,actual_own_SHA=final['own']['checkpoint']['sha256'],actual_report='ENTRY_SEED_FORMAL_FINAL_ACTUAL_REVIEW_1791705848191384400.json',only_monitor_metadata_corrected=True,original_prompt_preserved=str(old),line_endings_explicit_normalization=True,original_prepare_request_error='AssertionError: actual TOML escaped CRLF versus Python read_text normalized LF; corrected prompt file already written, request not written',downstream_error='PowerShell missing-request nonterminating Get-Content error led JSON.parse Unexpected token G before any automation update',only_missing_request_continued=True,no_GPU_runtime_or_budget_action=True)
p=R/'ENTRY_FINAL_MONITOR_BYTE_IDENTITY_CORRECTION.json';assert not p.exists();p.write_text(json.dumps(request,indent=2),encoding='utf8')
print(json.dumps(dict(prepared=True,correct_prompt=str(new),original_errors_retained=True)))
