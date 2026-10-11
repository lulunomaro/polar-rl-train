from second_io import *
save('PRE_GPU_PREPARATION_READER_ERRORS.json',dict(epoch=time.time(),errors=[
 dict(attempt='Initial summarized dispatch filename',path=str(PRIOR/'dispatch_wave_exposure_actual_once.py'),error='Get-Content missing path; actual dispatch_wave_exposure_once.py subsequently read'),
 dict(attempt='Central sync helper filename',path=str(PRIOR/'sync_wave142_complete_scope_once.py'),error='Get-Content missing path; complete_wave142_scope_and_monitor_once.py subsequently read'),
 dict(attempt='Active schema helper filename',path=str(PRIOR/'verify_wave_active_schema_cpu_actual.py'),error='Get-Content missing path; verify_wave_own_active_schema_cpu_actual.py subsequently read'),
 dict(attempt='PowerShell inline Python probe',error='PowerShell ParserError before Python/remote execution; missing argument in parameter list; no probe or mutation occurred; subsequent file-based stage actual boundary succeeded')],source_errors_preserved=True,no_GPU_or_once_or_budget_replay=True))
print(json.dumps(dict(saved=True)))
