from pathlib import Path
import ast,hashlib,json,subprocess,time
R=Path(__file__).resolve().parent;O=R.parent;T=O.parent;W=T.parent;C=W/'MOD4_WORKSPACE_CLEANUP_AUTHORIZED_20261021_V88';G=W/'polar-rl-train'
P=T/'H1_STEP270_REWARD_TUCK_CLEARANCE_V4_RESOURCE_V55_20261024';N=T/'H1_STEP270_REWARD_TUCK_CLEARANCE_V4_RESOURCE_V56_20261024'
read=lambda p:json.loads(p.read_bytes())
original_source="""from pathlib import Path
import json
T=Path('MOD4_H1_SCUT_STEP270_ON_210_E3_CONTINUATION_20261021');P=T/'H1_STEP270_REWARD_TUCK_CLEARANCE_V4_RESOURCE_V55_20261024';N=T/'H1_STEP270_REWARD_TUCK_CLEARANCE_V4_RESOURCE_V56_20261024';O=T/'H1_STEP270_TUCK_V3_FIRST_CLOSED39_REPLAY_20261023'
r=lambda p:json.loads(p.read_bytes());p=r(P/'reports/PAIR_COMPLETE_MODELS_AND_ORIGINAL_COST_CPU_ACTUAL.json');a=r(N/'reports/PAIR_ACTUAL_GO_POSITIVE_PPO_UUID_CREATE_ARGV_VERIFIED_ACTUAL.json');h=r(O/'reports/CURRENT_CLEARANCE_TUCK_V4_CURRENT55_CLOSED_HEALTH_RETENTION_EPISODE_CPU_ACTUAL.json')
print(json.dumps(dict(models={k:dict(updates:v['updates'],Adam:v['Adam'],SHA:v['final']['SHA'],actual_cost:v['actual_cost']) for k,v in p['models'].items()},actual_cost_sumonce=p['actual_cost_sumonce'],remaining_closure_snapshot=p['remaining_actual_snapshot'],health={k:h['health'][k] for k in ('control_steps','actual_physics_callbacks','expected_physics_callbacks','unknown_task_reset_events','integrity_task_reset_events','stop_reason')},runid=a['run_id'],h1_first=a['source210']['current']['rows']['h1']['latest_save']['updates'],e3_first=a['source72']['latest_save']['updates'],gate_epoch=max(x['nominal_end_epoch'] for x in a['source210']['current']['go'].values())-900)))
"""
original_stderr='''  File "<stdin>", line 5
    print(json.dumps(dict(models={k:dict(updates:v['updates'],Adam:v['Adam'],SHA:v['final']['SHA'],actual_cost:v['actual_cost']) for k,v in p['models'].items()},actual_cost_sumonce=p['actual_cost_sumonce'],remaining_closure_snapshot=p['remaining_actual_snapshot'],health={k:h['health'][k] for k in ('control_steps','actual_physics_callbacks','expected_physics_callbacks','unknown_task_reset_events','integrity_task_reset_events','stop_reason')},runid=a['run_id'],h1_first=a['source210']['current']['rows']['h1']['la
                                                ^
SyntaxError: invalid syntax
'''
# Consume existing JSON receipts only. The original inline code never parsed.
p=read(P/'reports/PAIR_COMPLETE_MODELS_AND_ORIGINAL_COST_CPU_ACTUAL.json');a=read(N/'reports/PAIR_ACTUAL_GO_POSITIVE_PPO_UUID_CREATE_ARGV_VERIFIED_ACTUAL.json');h=read(R/'CURRENT_CLEARANCE_TUCK_V4_CURRENT55_CLOSED_HEALTH_RETENTION_EPISODE_CPU_ACTUAL.json')
summary=dict(models={k:dict(updates=v['updates'],Adam=v['Adam'],SHA=v['final']['SHA'],actual_cost=v['actual_cost']) for k,v in p['models'].items()},actual_cost_sumonce=p['actual_cost_sumonce'],remaining_closure_snapshot=p['remaining_actual_snapshot'],health={k:h['health'][k] for k in ('control_steps','actual_physics_callbacks','expected_physics_callbacks','unknown_task_reset_events','integrity_task_reset_events','stop_reason')},runid=a['run_id'],h1_first=a['source210']['current']['rows']['h1']['latest_save']['updates'],e3_first=a['source72']['latest_save']['updates'],gate_epoch=max(x['nominal_end_epoch'] for x in a['source210']['current']['go'].values())-900)
report=dict(epoch=time.time(),original_inline_source=original_source,original_stderr_verbatim_tool_return=original_stderr,original_returncode=1,original_error_scope='SyntaxError from colons in dict keyword arguments; parse failed before reading any report',no_original_host_query_or_model_read_or_budget_change=True,corrected_reader_source=str(Path(__file__).resolve()),corrected_reader_SHA=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),corrected_summary_from_existing_JSON=summary,not_new_training_or_rollout=True,needs_same_phase_ordinary_supplement=True)
with (R/'CLOSED55_POST_ARCHIVE_INLINE_READER_SYNTAX_ERROR_AND_JSON_ONLY_CORRECTION_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(report,f,ensure_ascii=False,indent=2)
source=C/'append_current_clearance_v4_closed55_pair56_ordinary_once.py';dest=C/'append_current_clearance_v4_closed55_pair56_local_reader_supplement_once.py';s=source.read_text('utf8');ast.parse(s);assert not dest.exists();dest.write_text(s,'utf8')
head=subprocess.check_output(['git','-C',str(G),'rev-parse','HEAD'],text=True).strip();assert head=='f1376cbd4ddf67e743858cca60d43d477bf2d540'
cfg=dict(destination='current_clearance_v4_closed55_pair56_local_reader_supplement_20261024',base_HEAD=head,title='Preserve closed55 local summary reader syntax error and JSON-only correction')
with (C/'reports/CURRENT_CLEARANCE_V4_CLOSED55_PAIR56_LOCAL_READER_SUPPLEMENT_CONFIG.json').open('x',encoding='utf8') as f:json.dump(cfg,f,indent=2)
print(json.dumps(summary))
