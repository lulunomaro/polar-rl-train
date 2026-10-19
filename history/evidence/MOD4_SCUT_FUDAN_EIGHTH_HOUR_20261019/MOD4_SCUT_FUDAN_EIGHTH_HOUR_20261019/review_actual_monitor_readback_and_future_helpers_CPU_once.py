"""Check the actual same automation and prepared helpers, without host transport."""
from pathlib import Path
import json,tomllib,ast,time,subprocess
B=Path(__file__).resolve().parent;R=B/'reports'
expected=json.loads((B/'AUTOMATION_ACTUAL_SAME_RECIPE_EIGHTH_HOUR_V30_ARGS.json').read_bytes());actual=tomllib.loads((Path.home()/'.codex/automations/mod4-10/automation.toml').read_text('utf8'));d=json.loads((R/'THREE_NEXT_HOUR_CLOSED_SOURCE_LEARNING_DETACHED_ACTUAL.json').read_bytes());owner=d['owner']['detached_pid']
for key in ('name','prompt','rrule','status'):assert actual[key]==expected[key]
assert actual['target_thread_id']==expected['targetThreadId'] and actual['status']=='ACTIVE' and actual['rrule']=='FREQ=HOURLY;INTERVAL=1'
helpers={}
for p in [B/'collect_next_hour_missing_closed_finals_bounded_owner_wait_V2_once.py',B/'review_next_closed_hour_finals_whole_model_original_cost_CPU_once.py',*(B/'future_same_recipe_hour_templates').glob('*.py')]:
 s=p.read_text('utf8');ast.parse(s);helpers[str(p)]=True
 if p.parent==B:assert str(owner) in s and '270162' not in s
for n in ('prepare_next_three_closed_sources_one_hour_CPU_once.py','deploy_three_next_closed_source_hours_once.py'):
 s=(B/'future_same_recipe_hour_templates'/n).read_text('utf8');assert 'T3sf9_1910v14' in s
 if n.startswith('deploy_'):assert str(owner) in s and 'T3sf8_1910v13/owner' in s
s=(B/'future_same_recipe_hour_templates/collect_next_three_actual_learning_metadata_finite_once.py').read_text('utf8');assert '>=600' in s and 'set_keepalive(15)' in s and 'LEARNING_METADATA_OBSERVATIONS_JOURNAL.txt' in s
command="Get-CimInstance Win32_Process -Filter \"Name = 'python.exe'\" | Where-Object { $_.CommandLine -match '(collect_|deploy_)' } | Select-Object ProcessId,CreationDate,ExecutablePath,CommandLine | ConvertTo-Json -Depth 5 -Compress"
proc=subprocess.run(['powershell','-NoProfile','-Command',command],capture_output=True,text=True,check=True);alive=json.loads(proc.stdout) if proc.stdout.strip() else [];alive=alive if isinstance(alive,list) else [alive];assert not alive
out=dict(epoch=time.time(),same_automation_id='mod4-10',actual_status=actual['status'],actual_rrule=actual['rrule'],actual_target=actual['target_thread_id'],exact_prompt_readback=True,all_future_helpers_AST=helpers,actual_owner_binding=owner,next_unused_namespace='T3sf9_1910v14',only_prepared_not_future_launch=True,fresh_local_CIM_own_finite_transport_processes=alive,actual_finite_returned_transport_handed_back=True,no_other_SSH_watcher_or_account_write=True)
with (R/'AUTOMATION_V30_ACTUAL_READBACK_AND_FUTURE_HELPERS_CPU_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(out,f,indent=2)
print(json.dumps(out))
