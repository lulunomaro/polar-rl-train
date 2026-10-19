"""Create the archival helper for the actual resource-pending stage, not a launch receipt."""
from pathlib import Path
import ast
B=Path(__file__).resolve().parent;P=B.parent/'MOD4_SCUT_FUDAN_NINTH_HOUR_20261019'
s=(P/'archive_ninth_reward_hour_closed_sources_late_yaw_unique_once.py').read_text('utf8')
s=s.replace("G=W/'MOD4_SCUT_FUDAN_EIGHTH_HOUR_20261019'","G=W/'MOD4_SCUT_FUDAN_NINTH_HOUR_20261019'")
s=s.replace("BASE='9c85feb90693d2c0a8d691df58dad6564ab7a338'","BASE='4abc1fecadf35671603e1885a1925b8cdbf817f8'")
s=s.replace("ID='scut-fudan-ninth-hour-closed-sources-local-late-yaw-recurrence'","ID='scut-fudan-ninth-hour-closed-tenth-hour-gpu-resource-pending'")
s=s.replace("TITLE='Continue three experts from eighth reward-hour finals and review recurrent late local yaw drift'","TITLE='Close ninth SCUT-Fudan hour and prepare unchanged continuation pending H1 GPU admission'")
s=s.replace('One unique record after actual deployment','One unique record after actual closure and a retained resource admission hold')
before=" d=json.loads((B/'reports/THREE_NEXT_HOUR_CLOSED_SOURCE_LEARNING_DETACHED_ACTUAL.json').read_bytes());learning=json.loads((B/'reports/THREE_REAL_GPU_ACTUAL_PPO_LEARNING_METADATA_VERIFIED_OR_PENDING.json').read_bytes());f=json.loads((G/'reports/THREE_HOUR_ALL_CLOSED_FINAL_MODELS_ORIGINAL_COST_CPU_ACTUAL.json').read_bytes());assert learning['three_actual_PPO_learning_verified'] and f['passed_all_three_whole_final_models_CPU']"
after=" d=json.loads((B/'reports/THREE_NEXT_CLOSED_SOURCES_ONE_HOUR_CPU_PREPARED_ACTUAL.json').read_bytes());learning=json.loads((B/'reports/TENTH_PREPARED_RESOURCE_HOLD_AFTER_TRANSPORT_RETURN_CPU_ACTUAL.json').read_bytes());f=json.loads((G/'reports/THREE_HOUR_ALL_CLOSED_FINAL_MODELS_ORIGINAL_COST_CPU_ACTUAL.json').read_bytes());assert d['passed'] and learning['no_new_owner_nodes_workers_GO'] and f['passed_all_three_whole_final_models_CPU'];assert not (B/'reports/THREE_NEXT_HOUR_DEPLOY_STARTED_ACTUAL.json').exists()"
assert before in s;s=s.replace(before,after)
s=s.replace('assert len(old)==1394','assert len(old)==1396').replace('MOD4_SCUT_FUDAN_EIGHTH_HOUR_20261019/REPORT_CAPTURE_INDEX.json','MOD4_SCUT_FUDAN_NINTH_HOUR_20261019/REPORT_CAPTURE_INDEX.json')
s=s.replace('Actual prior closure:','Actual ninth-hour closure:').replace('Actual new dispatch and learning metadata:','Prepared sources and actual resource hold; no tenth-hour dispatch:')
s=s.replace("text={'.py','.ps1','.bat','.md','.txt','.json','.toml','.yml','.yaml'}","text={'.py','.ps1','.bat','.md','.txt','.json','.jsonl','.toml','.yml','.yaml'}")
s=s.replace('reports/EIGHTH_SCUT_FUDAN_HOUR_NEW_SOURCE_LOCAL_MUJOCO_BEHAVIOR_ACTUAL.json','reports/NINTH_SCUT_FUDAN_HOUR_NEW_SOURCE_LOCAL_MUJOCO_BEHAVIOR_ACTUAL.json')
s=s.replace("'--kind','training'","'--kind','diagnostic'")
s=s.replace('Actual eighth-hour whole models17Adam CPU/cost/out/locks; identical reward bytes and installed SDK/RSL/runtime; ninth-hour three GO/positive PPO/GPU compute; four new-source local traces with 1/1/1 jump events, increased clearance and recurrent late yaw breach, smaller normal drift; original physics/accounting and player retained.','Actual ninth-hour full finals, all17Adam/17parameter changes, finite CPU/cost/out/canonical and locks; identical prepared recipe with33negative cases; H1 unknown peer in closure snapshot and10append-only resource observations, transport10054 retained; tenth-hour not dispatched. Four new-source local traces1/1/1jump,15s jump yaw holding and greater normal drift. Premature CPU receipt-reader errors and V2 missing-only completion retained; original accounting, physics and player unchanged.')
s=s.replace("assert len(git('tag','--list').splitlines())==1395","assert len(git('tag','--list').splitlines())==1397").replace('total_tags=1395,all1394old_objects_peels_exact=True','total_tags=1397,all1396old_objects_peels_exact=True')
# Verify the actual saved automation before capturing all text and its tool receipt.
needle=" old={}\n"
replacement=" import tomllib\n args=json.loads((B/'AUTOMATION_RESOURCE_PENDING_V32_ARGS.json').read_bytes());actual=tomllib.loads((Path.home()/'.codex/automations/mod4-10/automation.toml').read_text('utf8'))\n for key in ('name','kind','prompt','status','rrule'):assert actual[key]==args[key]\n assert actual['target_thread_id']==args['targetThreadId'] and actual['status']=='ACTIVE'\n with (B/'reports/AUTOMATION_V32_RESOURCE_PENDING_ACTUAL_READBACK_CPU.json').open('x',encoding='utf8') as stream:json.dump(dict(epoch=time.time(),actual_name_prompt_kind_status_rrule_target_exact=True,existing_ACTIVE_hourly_same_target=True,no_second_monitor_or_budget=True),stream,indent=2)\n old={}\n"
assert needle in s;s=s.replace(needle,replacement,1)
ast.parse(s)
with (B/'archive_ninth_closed_tenth_resource_pending_unique_once.py').open('x',encoding='utf8',newline='\n') as stream:stream.write(s)
print('Actual resource-pending archival helper prepared; no record or tag yet.')
