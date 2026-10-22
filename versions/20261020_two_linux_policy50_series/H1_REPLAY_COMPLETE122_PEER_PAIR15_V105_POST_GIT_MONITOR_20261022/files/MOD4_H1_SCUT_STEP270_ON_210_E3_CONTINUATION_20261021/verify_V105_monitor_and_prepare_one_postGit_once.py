from pathlib import Path
import ast,hashlib,json,time,tomllib
T=Path(__file__).resolve().parent;R=T/'reports';req=json.loads((R/'V105_EXISTING_MONITOR_UPDATE_ARGS.json').read_bytes());p=Path('C:/Users/lulu/.codex/automations/mod4-10/automation.toml');actual=tomllib.loads(p.read_text('utf8'))
keys=dict(id='id',kind='kind',name='name',status='status',rrule='rrule',targetThreadId='target_thread_id',prompt='prompt')
if 'notificationPolicy' in req:keys['notificationPolicy']='notification_policy'
checks={k:req[k]==actual.get(v) for k,v in keys.items()};assert all(checks.values()),checks
H=lambda b:hashlib.sha256(b).hexdigest();v=dict(epoch=time.time(),automation_id='mod4-10',all_fields_raw_exact=True,no_normalization_needed=True,field_exact=checks,prompt_SHA=H(actual['prompt'].encode()),requested_prompt_SHA=H(req['prompt'].encode()),toml_SHA=H(p.read_bytes()),same_ACTIVE_hourly_original_target=True,current_pair15_both_PPO=True,user_recorded_replay_diagnosis_saved_no_reward_or_clock_change=True,no_270mm_or_graduation_claim=True)
with (R/'V105_EXISTING_MONITOR_EXACT_READBACK_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(v,f,indent=2)
s=(T/'append_V104_postGit_monitor_ordinary_once.py').read_text('utf8').replace("BASE = '826d99ad2a2ad7845e3f3c2f928a5e63d848e398'","BASE = 'e6fa55bb06a51b19a68b3ed96a008aff963f25b9'").replace('H1_COMPLETE122_PEER_PAIR14_V104_POST_GIT_MONITOR_20261022','H1_REPLAY_COMPLETE122_PEER_PAIR15_V105_POST_GIT_MONITOR_20261022').replace('V104_EXISTING_MONITOR_EXACT_READBACK_ACTUAL.json','V105_EXISTING_MONITOR_EXACT_READBACK_ACTUAL.json')
start=s.index('    files = [');end=s.index('    sys.path.insert',start)
s=s[:start]+'''    files = [
        T / 'prepare_V105_existing_monitor_replay_diagnosis_pair15_once.py',
        T / 'verify_V105_monitor_and_prepare_one_postGit_once.py',
        Path(__file__).resolve(),
        R / 'V105_GIT_MAIN_ALL_TAGS_AND_TEXT_BLOBS_VERIFIED_RECEIPT_ACTUAL.json',
        R / 'V105_EXISTING_MONITOR_UPDATE_ARGS.json',
        R / 'V105_EXISTING_MONITOR_APP_RECEIPT_ACTUAL.json',
        R / 'V105_EXISTING_MONITOR_EXACT_READBACK_ACTUAL.json',
        started,
    ]
'''+s[end:]
start=s.index('    index = dict(epoch=');end=s.index("    path = D / 'COMPLETE_FILE_CAPTURE_INDEX.json'",start)
s=s[:start]+"    index = dict(epoch=time.time(),kind='Recorded_step_replay_diagnosis_pair14_complete122_77_pair15_BOTH_PPO_postGit',entries=entries,ordinary_followup_only=True,no_new_record_or_tag=True,no_training_host_transport_GPU_PPO_or_account_write=True,existing_monitor_updated_and_raw_exact_readback_verified=True,replay_diagnosis_no_reward_or_request_clock_change=True,current_pair15_future_FINAL_or_retention_counts_not_claimed=True,no_formal_270mm_claim=True,deferred=['e2'])\n"+s[end:]
s=s.replace('Archive complete122 retained raw peer storage and pair14 Git receipt with same monitor exact readback','Archive recorded step replay diagnosis and pair15 Git receipt with same monitor exact readback')
ast.parse(s);(T/'append_V105_postGit_monitor_ordinary_once.py').open('x',encoding='utf8').write(s)
print(json.dumps(dict(exact_readback=True,prompt_chars=len(actual['prompt']),one_postGit_helper_prepared=True)))
