"""Bind saved monitor size to the actual own final, retain earlier metadata typo."""
from pathlib import Path
import json,time,tomllib,hashlib
D=Path(__file__).resolve().parent;R=D/'reports';H=lambda b:hashlib.sha256(b).hexdigest()
final=json.loads((R/'ENTRY_SEED_FORMAL_FINAL_ACTUAL_REVIEW_1791705848191384400.json').read_bytes());actual=final['checkpoint_bytes'];assert actual==17616498
old=D/'MONITOR_CURRENT_410_FINAL_PROMPT.md';new=D/'MONITOR_CURRENT_410_FINAL_BYTE_VERIFIED_PROMPT.md';assert not new.exists()
text=old.read_text(encoding='utf8');bad='SHA2fe67400d4119b94dbf33d7770b7fec44a9c73c568256e8161c3d8298ad73a04/17615794bytes';good=bad.replace('17615794',str(actual));assert text.count(bad)==1;text=text.replace(bad,good,1);new.write_text(text,encoding='utf8')
t=tomllib.loads(Path('C:/Users/lulu/.codex/automations/mod4-10/automation.toml').read_text(encoding='utf8'));assert t['prompt']==old.read_text(encoding='utf8') and t['rrule']=='FREQ=MINUTELY;INTERVAL=30' and t['status']=='ACTIVE'
request=dict(epoch=time.time(),id=t['id'],kind=t['kind'],name=t['name'],status=t['status'],rrule=t['rrule'],target_thread_id=t['target_thread_id'],prior_prompt_SHA=H(t['prompt'].encode()),new_prompt_SHA=H(text.encode()),original_checkpoint_byte_metadata_error=17615794,actual_own_checkpoint_bytes=actual,actual_own_SHA=final['own']['checkpoint']['sha256'],actual_report='ENTRY_SEED_FORMAL_FINAL_ACTUAL_REVIEW_1791705848191384400.json',only_monitor_metadata_corrected=True,original_prompt_preserved=str(old),no_GPU_or_runtime_or_budget_action=True)
p=R/'ENTRY_FINAL_MONITOR_BYTE_IDENTITY_CORRECTION.json';assert not p.exists();p.write_text(json.dumps(request,indent=2),encoding='utf8')
print(json.dumps(dict(prompt_path=str(new),actual_checkpoint_bytes=actual,original_metadata_retained=True)))
