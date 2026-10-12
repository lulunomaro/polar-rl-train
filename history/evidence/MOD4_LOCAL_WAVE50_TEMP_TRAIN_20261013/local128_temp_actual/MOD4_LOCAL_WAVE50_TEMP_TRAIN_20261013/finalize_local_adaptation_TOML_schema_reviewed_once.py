from pathlib import Path
import json,time,hashlib
D=Path(__file__).resolve().parent;R=D/'reports'
original=D/'finalize_local_adaptation_evidence_once.py';raw=original.read_bytes()
error=R/'FINALIZE_ORIGINAL_TOML_SCHEMA_ERROR_RETAINED.json';assert not error.exists()
error.write_text(json.dumps(dict(epoch=time.time(),classification='observer_TOML_schema_before_monitor_receipt_or_source_capture_or_GPU',source_path=str(original),source_sha256=hashlib.sha256(raw).hexdigest(),original_error="KeyError: 'targetThreadId'",actual_TOML_key='target_thread_id',automation_update_already_actualsuccess_no_repeat_update=True,training_worker_not_changed_or_restarted=True),ensure_ascii=False,indent=2),encoding='utf8')
assert not (R/'LOCAL_TEMP_HOURLY_MONITOR_ACTUAL_VERIFIED.json').exists() and not (D/'actual_v10_component_capture').exists()
text=raw.decode('utf8');assert text.count("cfg[k]==req[k]")==1 and text.count("cfg['targetThreadId']")==1
text=text.replace("cfg[k]==req[k]","cfg['target_thread_id' if k=='targetThreadId' else k]==req[k]").replace("cfg['targetThreadId']","cfg['target_thread_id']")
reviewed=D/'finalize_local_adaptation_TOML_reviewed_payload.py';assert not reviewed.exists();reviewed.write_text(text,encoding='utf8')
namespace={'__name__':'independent_TOML_reviewed_continuation','__file__':str(reviewed)};exec(compile(text,str(reviewed),'exec'),namespace);namespace['main']()
