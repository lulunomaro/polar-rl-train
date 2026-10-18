from pathlib import Path
import ast,json,time,tomllib
B=Path(__file__).resolve().parent;R=B/'reports';a=json.loads((B/'AUTOMATION_ACTUAL_SAME_RECIPE_SECOND_HOUR_V24_ARGS.json').read_bytes());v=tomllib.loads((Path.home()/'.codex/automations/mod4-10/automation.toml').read_text('utf8'))
assert v['prompt'].strip()==a['prompt'].strip() and v['rrule']==a['rrule']=='FREQ=HOURLY;INTERVAL=1' and v['status']==a['status']=='ACTIVE' and v['target_thread_id']==a['targetThreadId']=='01a07a2d-9036-7531-a012-692df9f56353'
files=[]
for p in [*B.glob('collect_next_hour_missing_closed*.py'),*B.glob('review_next_closed_hour_finals*.py'),*(B/'future_same_recipe_hour_templates').glob('*.py')]:
 text=p.read_text('utf8');ast.parse(text);files.append(str(p))
 if p.parent.name!='future_same_recipe_hour_templates':assert '212000' in text and '197995' not in text
future=(B/'future_same_recipe_hour_templates/collect_next_three_actual_learning_metadata_finite_once.py').read_text('utf8');assert '.get(\'active_rows\',0)>0' not in future and 'set_keepalive(15)' in future
assert 'T3sf3_1910v8' in (B/'future_same_recipe_hour_templates/prepare_next_three_closed_sources_one_hour_CPU_once.py').read_text('utf8')
report=dict(epoch=time.time(),actual_saved_monitor_prompt_exact=True,original_hourly_status_target_unchanged=True,future_closing_bound_owner212000=True,future_templates_AST=files,future_same_recipe_learning_metadata_requires_positive_PPO_not_instantaneous_public4_active=True,future_reward_readout_still_collected=True,no_runtime_or_GPU_or_budget_change=True)
with (R/'AUTOMATION_V24_ACTUAL_READBACK_AND_FUTURE_HELPERS_CPU_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(report,f,indent=2)
print(json.dumps(dict(saved_monitor_exact=True,future_helpers_AST=len(files))))
