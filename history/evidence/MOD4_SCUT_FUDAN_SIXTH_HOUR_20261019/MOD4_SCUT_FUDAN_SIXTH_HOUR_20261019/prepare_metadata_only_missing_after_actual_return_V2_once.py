"""New bounded reader only after the first10054 reader actually returned."""
from pathlib import Path
import ast,json,time,subprocess,hashlib
B=Path(__file__).resolve().parent;R=B/'reports'
cmd="Get-CimInstance Win32_Process -Filter \"Name = 'python.exe'\" | Where-Object { $_.CommandLine -match '(collect_|deploy_)' } | Select-Object ProcessId,CreationDate,ExecutablePath,CommandLine | ConvertTo-Json -Depth 5 -Compress"
r=subprocess.run(['powershell','-NoProfile','-Command',cmd],capture_output=True,text=True,check=True);assert not r.stdout.strip()
errors=list(R.glob('THREE_REAL_LEARNING_FINITE_COLLECTOR_ORIGINAL_ERROR_*.json'));assert len(errors)==1
required=['THREE_REAL_LEARNING_TARGET72_NATIVE_OR_PRODUCTION_BOUND_METADATA_ACTUAL.json','THREE_REAL_LEARNING_SOURCE210_METADATA_ACTUAL.json','THREE_REAL_LEARNING_ONE_ORIGINAL_OWNER_ACTUAL_CURRENT.json','THREE_REAL_GPU_ACTUAL_PPO_LEARNING_METADATA_VERIFIED_OR_PENDING.json'];assert all(not (R/n).exists() for n in required)
p=B/'collect_next_three_actual_learning_metadata_finite_once.py';s=p.read_text('utf8')
s=s.replace('THREE_REAL_LEARNING_METADATA_FINITE_COLLECTOR_STARTED_ACTUAL.json','THREE_REAL_LEARNING_METADATA_FINITE_COLLECTOR_V2_ONLY_MISSING_STARTED_ACTUAL.json').replace('THREE_REAL_LEARNING_FINITE_COLLECTOR_ORIGINAL_ERROR_','THREE_REAL_LEARNING_FINITE_COLLECTOR_V2_ONLY_MISSING_ORIGINAL_ERROR_')
q='journal.write(json.dumps(dict(observation=observations,actual=target))';assert q in s;s=s.replace(q,"journal.write(json.dumps(dict(reader='V2_only_missing_after_actual10054return',observation=observations,actual=target))")
ast.parse(s);dest=B/'collect_next_three_actual_learning_metadata_only_missing_V2_finite_once.py'
with dest.open('x',encoding='utf8') as f:f.write(s)
with (R/'METADATA_READER_ACTUAL_RETURN_AND_ONLY_MISSING_V2_CPU_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(dict(epoch=time.time(),fresh_CIM_own_finite_alive=[],prior_reader_error=dict(path=str(errors[0]),bytes=errors[0].stat().st_size,SHA=hashlib.sha256(errors[0].read_bytes()).hexdigest()),new_reader=dict(path=str(dest),bytes=dest.stat().st_size,SHA=hashlib.sha256(dest.read_bytes()).hexdigest()),missing_metadata_only=required,max_same_connection_seconds=600,keepalive15_already_existed=True,append_only_journal_retained=True,no_GPU_Task_native_PT_raw_replay_or_account_write=True),f,indent=2)
print('Actual old reader returned; independent V2 prepared for missing metadata only.')
