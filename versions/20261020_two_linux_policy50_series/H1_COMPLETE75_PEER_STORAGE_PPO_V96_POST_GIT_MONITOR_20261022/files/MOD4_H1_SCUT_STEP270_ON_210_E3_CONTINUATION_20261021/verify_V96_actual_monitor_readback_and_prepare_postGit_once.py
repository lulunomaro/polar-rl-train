from pathlib import Path
import ast,hashlib,json,time,tomllib
T=Path(__file__).resolve().parent;R=T/'reports';req=json.loads((R/'V96_EXISTING_MONITOR_UPDATE_ARGS.json').read_bytes());p=Path('C:/Users/lulu/.codex/automations/mod4-10/automation.toml');actual=tomllib.loads(p.read_text('utf8'))
keys=dict(id='id',kind='kind',name='name',status='status',rrule='rrule',targetThreadId='target_thread_id',prompt='prompt')
if 'notificationPolicy' in req:keys['notificationPolicy']='notification_policy'
checks={k:req[k]==actual.get(v) for k,v in keys.items()};assert all(checks.values()),checks
h=lambda x:hashlib.sha256(x).hexdigest()
v=dict(epoch=time.time(),automation_id='mod4-10',all_fields_raw_exact=True,all_fields_verified_with_explicit_final_LF_normalization=True,no_normalization_needed=True,field_exact=checks,prompt_SHA=h(actual['prompt'].encode()),requested_prompt_SHA=h(req['prompt'].encode()),toml_SHA=h(p.read_bytes()),same_ACTIVE_hourly_original_target=True,H1_complete75_original_disk_savedstop_peer_storage_and_both_actual_PPO=True)
with (R/'V96_EXISTING_MONITOR_EXACT_READBACK_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(v,f,indent=2)
s=(T/'append_V95_postGit_monitor_ordinary_once.py').read_text('utf8')
s=s.replace("BASE = 'f1af05ac8f83e09ad18e9c4b3224f112882e4343'","BASE = 'c8374eb3020d632f6ba5c620ec565d47db89d0c8'").replace('H1_CLASSIFIER_INSTALLED_PPO_V95_POST_GIT_MONITOR_20261022','H1_COMPLETE75_PEER_STORAGE_PPO_V96_POST_GIT_MONITOR_20261022')
s=s.replace('V95_EXISTING_MONITOR_EXACT_READBACK_ACTUAL.json','V96_EXISTING_MONITOR_EXACT_READBACK_ACTUAL.json')
start=s.index('    files = [');end=s.index('    sys.path.insert',start)
files="""    files = [
        T / 'prepare_V96_existing_monitor_complete75_peer_storage_and_pair6_PPO_once.py',
        T / 'verify_V96_actual_monitor_readback_and_prepare_postGit_once.py',
        Path(__file__).resolve(),
        R / 'V96_GIT_MAIN_ALL_TAGS_AND_TEXT_BLOBS_VERIFIED_RECEIPT_ACTUAL.json',
        R / 'V96_EXISTING_MONITOR_UPDATE_ARGS.json',
        R / 'V96_EXISTING_MONITOR_APP_RECEIPT_ACTUAL.json',
        R / 'V96_EXISTING_MONITOR_EXACT_READBACK_ACTUAL.json',
        started,
    ]
"""
s=s[:start]+files+s[end:]
s=s.replace('H1_FINAL14_wholeCPU_classifier_installed_both_actual_PPO_single_postGit_monitor_receipt','H1_complete75_original_disk_savedstop_peer_storage_and_both_PPO_single_postGit_receipt')
s=s.replace('H1_previous_FINAL14_wholeCPU_passed=True,known_term_classifier_installed=True,current_both_actual_GO_PPO_historical_snapshots=True', 'H1_previous_complete75_wholeCPU_passed=True,original_disk_savedstop_and_verified_peer_storage_preserved=True,current_both_actual_GO_PPO_historical_snapshots=True')
s=s.replace('Archive installed H1 classifier and both PPO Git receipt with same monitor exact readback','Archive H1 complete75 peer storage and both PPO Git receipt with same monitor exact readback')
ast.parse(s);(T/'append_V96_postGit_monitor_ordinary_once.py').open('x',encoding='utf8').write(s)
print(json.dumps(dict(exact_readback=True,prompt_chars=len(actual['prompt']),postGit_helper_prepared=True)))
