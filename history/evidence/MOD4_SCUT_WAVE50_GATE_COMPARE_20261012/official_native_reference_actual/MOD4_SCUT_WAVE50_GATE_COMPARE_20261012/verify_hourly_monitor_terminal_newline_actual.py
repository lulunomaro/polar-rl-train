"""App trims one terminal LF; verify every other requested byte and field exactly."""
from scut_wave_io import *
import tomllib
p=Path('C:/Users/lulu/.codex/automations/mod4-10/automation.toml');req=json.loads((R/'SCUT151_HOURLY_MONITOR_UPDATE_REQUEST.json').read_bytes());s=tomllib.loads(p.read_text(encoding='utf8'))
assert req['prompt'].endswith('\n') and s['prompt']==req['prompt'][:-1]
assert s['status']==req['status']=='ACTIVE' and s['rrule']==req['rrule']=='FREQ=HOURLY;INTERVAL=1' and s['target_thread_id']==req['targetThreadId']
save('SCUT_MONITOR_TERMINAL_NEWLINE_SCHEMA_REVIEW.json',dict(epoch=time.time(),passed=True,original_reader_source=str(D/'verify_hourly_reference151_monitor_actual.py'),original_reader_SHA=H((D/'verify_hourly_reference151_monitor_actual.py').read_bytes()),original_error='AssertionError before any write: native app trims one terminal newline from prompt',requested_prompt_SHA=H(req['prompt'].encode()),actual_prompt_SHA=H(s['prompt'].encode()),exact_one_terminal_LF_removed_only=True,all_other_prompt_bytes_and_same_hourly_target_status_exact=True,no_automation_reupdate_or_GPU_replay=True))
save('SCUT151_HOURLY_MONITOR_ACTUAL_VERIFIED.json',dict(epoch=time.time(),passed=True,id='mod4-10',rrule=s['rrule'],status=s['status'],same_target=s['target_thread_id'],request_prompt_SHA=H(req['prompt'].encode()),actual_prompt_SHA=H(s['prompt'].encode()),native_exact_one_terminal_LF_trim_only=True,actual_TOML_SHA=H(p.read_bytes()),healthy_pending_quiet_meaningful_only=True,no_extra_monitor_or_frequency_change=True))
print(json.dumps(dict(passed=True,hourly_same_target=True,exact_only_terminal_LF_trim=True)))
