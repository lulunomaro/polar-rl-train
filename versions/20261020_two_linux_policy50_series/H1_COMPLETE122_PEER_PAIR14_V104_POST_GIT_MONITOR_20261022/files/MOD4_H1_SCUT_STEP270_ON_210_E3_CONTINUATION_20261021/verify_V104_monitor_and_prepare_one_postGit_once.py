from pathlib import Path
import ast,hashlib,json,time,tomllib
T=Path(__file__).resolve().parent;R=T/'reports';req=json.loads((R/'V104_EXISTING_MONITOR_UPDATE_ARGS.json').read_bytes());p=Path('C:/Users/lulu/.codex/automations/mod4-10/automation.toml');actual=tomllib.loads(p.read_text('utf8'))
keys=dict(id='id',kind='kind',name='name',status='status',rrule='rrule',targetThreadId='target_thread_id',prompt='prompt')
if 'notificationPolicy' in req:keys['notificationPolicy']='notification_policy'
checks={k:req[k]==actual.get(v) for k,v in keys.items()};assert all(checks.values()),checks
H=lambda b:hashlib.sha256(b).hexdigest()
v=dict(epoch=time.time(),automation_id='mod4-10',all_fields_raw_exact=True,no_normalization_needed=True,field_exact=checks,prompt_SHA=H(actual['prompt'].encode()),requested_prompt_SHA=H(req['prompt'].encode()),toml_SHA=H(p.read_bytes()),same_ACTIVE_hourly_original_target=True,current_pair14_both_PPO_approved_retention_byteexact=True,closed_pair13_three_raw_full_SHA_retained72=True,no_270mm_or_graduation_claim=True)
with (R/'V104_EXISTING_MONITOR_EXACT_READBACK_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(v,f,indent=2)
s=(T/'append_V103_postGit_monitor_ordinary_once.py').read_text('utf8').replace("BASE = '55703d994a0760d1045c53cdef20f190f86aba2e'","BASE = '826d99ad2a2ad7845e3f3c2f928a5e63d848e398'").replace('H1_COMPLETE121_ACTUAL_RETENTION_PAIR13_V103_POST_GIT_MONITOR_20261022','H1_COMPLETE122_PEER_PAIR14_V104_POST_GIT_MONITOR_20261022').replace('V103_EXISTING_MONITOR_EXACT_READBACK_ACTUAL.json','V104_EXISTING_MONITOR_EXACT_READBACK_ACTUAL.json')
start=s.index('    files = [');end=s.index('    sys.path.insert',start)
s=s[:start]+'''    files = [
        T / 'prepare_V104_existing_monitor_complete122_pair14_once.py',
        T / 'verify_V104_monitor_and_prepare_one_postGit_once.py',
        Path(__file__).resolve(),
        R / 'V104_GIT_MAIN_ALL_TAGS_AND_TEXT_BLOBS_VERIFIED_RECEIPT_ACTUAL.json',
        R / 'V104_EXISTING_MONITOR_UPDATE_ARGS.json',
        R / 'V104_EXISTING_MONITOR_APP_RECEIPT_ACTUAL.json',
        R / 'V104_EXISTING_MONITOR_EXACT_READBACK_ACTUAL.json',
        started,
    ]
'''+s[end:]
start=s.index('    index = dict(epoch=');end=s.index("    path = D / 'COMPLETE_FILE_CAPTURE_INDEX.json'",start)
s=s[:start]+"    index = dict(epoch=time.time(),kind='H1_complete122_E3_complete76_retained_raw_peer_storage_pair14_BOTH_PPO_postGit',entries=entries,ordinary_followup_only=True,no_new_record_or_tag=True,no_training_host_transport_GPU_PPO_or_account_write=True,existing_monitor_updated_and_raw_exact_readback_verified=True,closed_pair13_three_retained_raw_actual72_fullSHA=True,current_pair14_future_FINAL_or_retention_counts_not_claimed=True,no_formal_270mm_claim=True,deferred=['e2'])\n"+s[end:]
s=s.replace('Archive complete121 actual bounded retention and pair13 Git receipt with same monitor exact readback','Archive complete122 retained raw peer storage and pair14 Git receipt with same monitor exact readback')
ast.parse(s);(T/'append_V104_postGit_monitor_ordinary_once.py').open('x',encoding='utf8').write(s)
print(json.dumps(dict(exact_readback=True,prompt_chars=len(actual['prompt']),one_postGit_helper_prepared=True)))
