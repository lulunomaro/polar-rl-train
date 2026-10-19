"""Prepare a separate unique stage after the user's new authorization and real learning."""
from pathlib import Path
import ast
B=Path(__file__).resolve().parent;P=B.parent/'MOD4_SCUT_FUDAN_NINTH_HOUR_20261019'
s=(P/'archive_ninth_reward_hour_closed_sources_late_yaw_unique_once.py').read_text('utf8')
s=s.replace("G=W/'MOD4_SCUT_FUDAN_EIGHTH_HOUR_20261019'","G=W/'MOD4_SCUT_FUDAN_NINTH_HOUR_20261019'")
s=s.replace("BASE='9c85feb90693d2c0a8d691df58dad6564ab7a338'","BASE='eb315bf2b20b7cd1e2e56aca206da5e813d52705'")
s=s.replace("ID='scut-fudan-ninth-hour-closed-sources-local-late-yaw-recurrence'","ID='scut-fudan-tenth-hour-user-authorized-shared-gpu-continuation'")
s=s.replace("DEST=REPO/'history/evidence'/B.name","DEST=REPO/'history/evidence'/(B.name+'_USER_SHARED_GPU_CONTINUATION')")
s=s.replace('ACTUAL_SCUT_FUDAN_REWARD_TRAINING_NOTE_UTF8.txt','ACTUAL_USER_SHARED_GPU_TRAINING_NOTE_UTF8.txt').replace('ACTUAL_SCUT_FUDAN_REWARD_TAG_UTF8.txt','ACTUAL_USER_SHARED_GPU_TRAINING_TAG_UTF8.txt')
s=s.replace("TITLE='Continue three experts from eighth reward-hour finals and review recurrent late local yaw drift'","TITLE='Start tenth SCUT-Fudan hour with user-authorized H1 GPU sharing and original memory/save/accounting guards'")
s=s.replace('assert len(old)==1394','assert len(old)==1397')
s=s.replace('MOD4_SCUT_FUDAN_EIGHTH_HOUR_20261019/REPORT_CAPTURE_INDEX.json','MOD4_SCUT_FUDAN_TENTH_HOUR_20261019/REPORT_CAPTURE_INDEX.json')
s=s.replace("B/'STAGE_SUMMARY.md'","B/'USER_SHARED_GPU_STAGE_SUMMARY.md'")
s=s.replace("text={'.py','.ps1','.bat','.md','.txt','.json','.toml','.yml','.yaml'}","text={'.py','.ps1','.bat','.md','.txt','.json','.jsonl','.toml','.yml','.yaml'}")
s=s.replace('reports/THREE_NEXT_CLOSED_SOURCES_ONE_HOUR_CPU_PREPARED_ACTUAL.json','reports/THREE_NEXT_CLOSED_SOURCES_USER_SHARED_GPU_CPU_PREPARED_ACTUAL.json')
s=s.replace('reports/EIGHTH_SCUT_FUDAN_HOUR_NEW_SOURCE_LOCAL_MUJOCO_BEHAVIOR_ACTUAL.json','reports/NINTH_SCUT_FUDAN_HOUR_NEW_SOURCE_LOCAL_MUJOCO_BEHAVIOR_ACTUAL.json')
s=s.replace('Actual eighth-hour whole models17Adam CPU/cost/out/locks; identical reward bytes and installed SDK/RSL/runtime; ninth-hour three GO/positive PPO/GPU compute; four new-source local traces with 1/1/1 jump events, increased clearance and recurrent late yaw breach, smaller normal drift; original physics/accounting and player retained.','Human explicit instruction recorded; only unused H1 resource admission changed to allow same-GPU coexistence. Original7000MiB/RAM/disk/locks/save/source/recipe/accounting guards retained. All target manifests and current SDK/RSL/source CPU passed; actual tenth-hour three GO/positive PPO/matching worker GPU compute verified. Hour-end collectors bound306868 and same-recipe sharing-aware future templates prepared; original errors and player retained, no behavior replay.')
s=s.replace("assert len(git('tag','--list').splitlines())==1395","assert len(git('tag','--list').splitlines())==1398").replace('total_tags=1395,all1394old_objects_peels_exact=True','total_tags=1398,all1397old_objects_peels_exact=True')
needle=' old={}\n'
replacement=" import tomllib\n args=json.loads((B/'AUTOMATION_ACTUAL_TENTH_USER_SHARED_GPU_V33_ARGS.json').read_bytes());actual=tomllib.loads((Path.home()/'.codex/automations/mod4-10/automation.toml').read_text('utf8'))\n for key in ('name','kind','prompt','status','rrule'):assert actual[key]==args[key]\n assert actual['target_thread_id']==args['targetThreadId'] and actual['status']=='ACTIVE'\n with (B/'reports/AUTOMATION_V33_SHARED_GPU_ACTUAL_READBACK_AND_FUTURE_HELPERS_CPU.json').open('x',encoding='utf8') as stream:json.dump(dict(epoch=time.time(),actual_name_prompt_kind_status_rrule_target_exact=True,original_ACTIVE_hourly_target_preserved=True,collectors_bound_owner306868=True,future_sharing_authorization_retained=True),stream,indent=2)\n old={}\n"
assert needle in s;s=s.replace(needle,replacement,1)
ast.parse(s)
with (B/'archive_tenth_user_shared_GPU_actual_learning_unique_once.py').open('x',encoding='utf8',newline='\n') as stream:stream.write(s)
print('Distinct actual shared-GPU learning archival stage prepared, not yet recorded.')
