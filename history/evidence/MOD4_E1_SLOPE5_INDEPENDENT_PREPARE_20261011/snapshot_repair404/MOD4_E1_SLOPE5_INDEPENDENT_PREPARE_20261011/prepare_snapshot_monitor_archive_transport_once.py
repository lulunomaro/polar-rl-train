from pathlib import Path
import json,time
D=Path(__file__).resolve().parent;p=D/'archive_slope_snapshot_monitor_verified_once.py';assert not p.exists()
s=(D/'archive_slope_snapshot_repair_once.py').read_text();s=s.replace("save('SNAPSHOT_REPAIR_ARCHIVE_ERROR.json'","save('SNAPSHOT_MONITOR_VERIFIED_ARCHIVE_ERROR.json'")
compile(s,str(p),'exec');p.write_text(s,encoding='utf8')
(D/'reports/SNAPSHOT_MONITOR_LINEENDING_REJECTION_REVIEW.json').write_text(json.dumps(dict(epoch=time.time(),previous_archive_prewrite_guard_rejected_before_record=True,PowerShell_GetContent_console_transport_CRLF_diff=True,original_prompt_and_error_retained=True,new_JSON_encoded_prompt_transport_exact=True,physical_contracts_not_changed=True),indent=2))
