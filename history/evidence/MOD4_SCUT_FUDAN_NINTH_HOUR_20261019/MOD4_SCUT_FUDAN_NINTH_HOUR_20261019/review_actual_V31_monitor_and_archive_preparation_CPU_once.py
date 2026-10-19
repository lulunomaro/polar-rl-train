from pathlib import Path
import ast,json,re,time,tomllib
B=Path(__file__).resolve().parent;W=B.parent;P=W/'MOD4_SCUT_FUDAN_EIGHTH_HOUR_20261019'
args=json.loads((B/'AUTOMATION_ACTUAL_SAME_RECIPE_NINTH_HOUR_V31_ARGS.json').read_bytes())
actual=tomllib.loads((Path.home()/'.codex/automations/mod4-10/automation.toml').read_text('utf8'))
for key in ('prompt','rrule','status','kind','name'):assert actual[key]==args[key]
assert actual['target_thread_id']==args['targetThreadId'] and actual['status']=='ACTIVE'
helpers=[]
for p in [B/'collect_next_hour_missing_closed_finals_bounded_owner_wait_V2_once.py',B/'review_next_closed_hour_finals_whole_model_original_cost_CPU_once.py',*(B/'future_same_recipe_hour_templates').glob('*.py')]:
    s=p.read_text('utf8');ast.parse(s);helpers.append(str(p))
    if p.parent==B:assert '293563' in s and '281824' not in s
assert 'T3sf10_1910v15' in (B/'future_same_recipe_hour_templates/deploy_three_next_closed_source_hours_once.py').read_text('utf8')
with (B/'reports/AUTOMATION_V31_ACTUAL_READBACK_AND_FUTURE_HELPERS_CPU_ACTUAL.json').open('x',encoding='utf8') as f:
    json.dump(dict(epoch=time.time(),status='PASS',actual_prompt_rrule_status_target_exact=True,original_ACTIVE_hourly_target_preserved=True,prepared_AST_checked_helpers=helpers,closing_owner_binding=293563,future_only_reserved='T3sf10_1910v15',no_transport_or_GPU_or_account_change=True),f,indent=2)
s=(P/'archive_eighth_reward_hour_closed_sources_yaw_objective_unique_once.py').read_text('utf8')
s=s.replace("G=W/'MOD4_SCUT_FUDAN_SEVENTH_HOUR_20261019'","G=W/'MOD4_SCUT_FUDAN_EIGHTH_HOUR_20261019'")
s=s.replace("BASE='df17c5510a94bdb542fdc7cacc86abd2a0e41ef2'","BASE='9c85feb90693d2c0a8d691df58dad6564ab7a338'")
s=s.replace('scut-fudan-eighth-hour-closed-sources-yaw-objective-review','scut-fudan-ninth-hour-closed-sources-local-late-yaw-recurrence')
s=s.replace('Continue three experts from seventh reward-hour finals and review local holding with original yaw-rate objectives','Continue three experts from eighth reward-hour finals and review recurrent late local yaw drift')
s=s.replace('history/evidence/MOD4_SCUT_FUDAN_SEVENTH_HOUR_20261019/REPORT_CAPTURE_INDEX.json','history/evidence/MOD4_SCUT_FUDAN_EIGHTH_HOUR_20261019/REPORT_CAPTURE_INDEX.json')
s=s.replace('SEVENTH_SCUT_FUDAN_HOUR_NEW_SOURCE_LOCAL_MUJOCO_BEHAVIOR_ACTUAL.json','EIGHTH_SCUT_FUDAN_HOUR_NEW_SOURCE_LOCAL_MUJOCO_BEHAVIOR_ACTUAL.json')
s=s.replace('Actual seventh-hour whole models17Adam CPU/cost/out/locks; identical reward bytes and installed target SDK/RSL/runtime; three new GO/positive PPO/GPU compute; four new-source local traces with original recovery events and mixed normal drift, source-only yaw-rate objective review and preserved lookup failures; original physics/accounting retained.','Actual eighth-hour whole models17Adam CPU/cost/out/locks; identical reward bytes and installed SDK/RSL/runtime; ninth-hour three GO/positive PPO/GPU compute; four new-source local traces with 1/1/1 jump events, increased clearance and recurrent late yaw breach, smaller normal drift; original physics/accounting and player retained.')
s=re.sub(r'\b1392\b','1394',s);s=re.sub(r'\b1393\b','1395',s);s=s.replace('all1392old_objects_peels_exact','all1394old_objects_peels_exact')
ast.parse(s);target=B/'archive_ninth_reward_hour_closed_sources_late_yaw_unique_once.py'
with target.open('x',encoding='utf8') as f:f.write(s)
print(json.dumps(dict(actual_monitor_readback=True,helpers=len(helpers),archive_helper_prepared=str(target))))
