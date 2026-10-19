"""Prepare one archival stage for actual closure, failure, two-slot learning and CPU repair."""
from pathlib import Path
import ast
B=Path(__file__).resolve().parent;P=B.parent/'MOD4_SCUT_FUDAN_NINTH_HOUR_20261019'
s=(P/'archive_ninth_reward_hour_closed_sources_late_yaw_unique_once.py').read_text('utf8')
s=s.replace("G=W/'MOD4_SCUT_FUDAN_EIGHTH_HOUR_20261019'","G=W/'MOD4_SCUT_FUDAN_TENTH_HOUR_20261019'")
s=s.replace("BASE='9c85feb90693d2c0a8d691df58dad6564ab7a338'","BASE='94a970b4817f6de9bcde33ff03e313dfec312fd6'")
s=s.replace("ID='scut-fudan-ninth-hour-closed-sources-local-late-yaw-recurrence'","ID='scut-fudan-eleventh-hour-partial-continuation-and-h1-sharing-inheritance-repair'")
s=s.replace("TITLE='Continue three experts from eighth reward-hour finals and review recurrent late local yaw drift'","TITLE='Preserve eleventh-hour H1 pre-GO inheritance failure, two healthy expert learning and prepared safe repair'")
s=s.replace('THREE_REAL_GPU_ACTUAL_PPO_LEARNING_METADATA_VERIFIED_OR_PENDING.json','TWO_HEALTHY_EXPERTS_PPO_AND_H1_PREGO_FAILURE_METADATA_V2_ACTUAL.json')
s=s.replace("assert learning['three_actual_PPO_learning_verified'] and f['passed_all_three_whole_final_models_CPU']","assert learning['two_healthy_actual_PPO_learning_verified'] and not learning['three_actual_PPO_learning_verified'] and not learning['experts']['h1']['actual_GO'] and f['passed_all_three_whole_final_models_CPU']")
s=s.replace('assert len(old)==1394','assert len(old)==1398')
s=s.replace('MOD4_SCUT_FUDAN_EIGHTH_HOUR_20261019/REPORT_CAPTURE_INDEX.json','MOD4_SCUT_FUDAN_TENTH_HOUR_20261019_USER_SHARED_GPU_CONTINUATION/REPORT_CAPTURE_INDEX.json')
s=s.replace("text={'.py','.ps1','.bat','.md','.txt','.json','.toml','.yml','.yaml'}","text={'.py','.ps1','.bat','.md','.txt','.json','.jsonl','.toml','.yml','.yaml'}")
s=s.replace('reports/EIGHTH_SCUT_FUDAN_HOUR_NEW_SOURCE_LOCAL_MUJOCO_BEHAVIOR_ACTUAL.json','reports/TENTH_SCUT_FUDAN_HOUR_NEW_SOURCE_LOCAL_MUJOCO_BEHAVIOR_ACTUAL.json')
s=s.replace('Actual eighth-hour whole models17Adam CPU/cost/out/locks; identical reward bytes and installed SDK/RSL/runtime; ninth-hour three GO/positive PPO/GPU compute; four new-source local traces with 1/1/1 jump events, increased clearance and recurrent late yaw breach, smaller normal drift; original physics/accounting and player retained.','Actual tenth-hour three full finals with all17Adam/17parameter changes and original10935.826829433441s cost/out/locks. Eleventh H1 pre-GO node admission failure preserved, no H1worker/GO/charge; E2/E3 actual GO/positive PPO/matching compute continue under sole original writer318576. Controller-copy overwrite reproduced and sharing-aware resource override/predeploy exact-byte regression passed on CPU. Separate partial closing/two-new-finals plus retained hour10 H1-source reviewer and unused twelfth repair templates prepared without live owner/worker stop or extra writer. Four new tenth-source local trajectories only; source/recipe/physics/budget/player unchanged.')
s=s.replace("assert len(git('tag','--list').splitlines())==1395","assert len(git('tag','--list').splitlines())==1399").replace('total_tags=1395,all1394old_objects_peels_exact=True','total_tags=1399,all1398old_objects_peels_exact=True')
needle=' old={}\n'
replacement=" import tomllib\n args=json.loads((B/'AUTOMATION_ACTUAL_PARTIAL_ELEVENTH_REPAIR_V34_ARGS.json').read_bytes());actual=tomllib.loads((Path.home()/'.codex/automations/mod4-10/automation.toml').read_text('utf8'))\n for key in ('name','kind','prompt','status','rrule'):assert actual[key]==args[key]\n assert actual['target_thread_id']==args['targetThreadId'] and actual['status']=='ACTIVE'\n with (B/'reports/AUTOMATION_V34_PARTIAL_ELEVENTH_ACTUAL_READBACK_CPU.json').open('x',encoding='utf8') as stream:json.dump(dict(epoch=time.time(),actual_name_prompt_kind_status_rrule_target_exact=True,original_ACTIVE_hourly_target_preserved=True,actual_two_GO_H1failure_and318576_binding=True,no_second_monitor_or_live_training_change=True),stream,indent=2)\n old={}\n"
assert needle in s;s=s.replace(needle,replacement,1)
ast.parse(s)
with (B/'archive_partial_eleventh_two_learning_H1_failure_repair_unique_once.py').open('x',encoding='utf8',newline='\n') as stream:stream.write(s)
print('Unique actual partial-cohort archival helper prepared, not recorded yet.')
