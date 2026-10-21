from pathlib import Path
import ast,hashlib,json,time,tomllib
T=Path(__file__).resolve().parent;R=T/'reports';req=json.loads((R/'V97_EXISTING_MONITOR_UPDATE_ARGS.json').read_bytes());p=Path('C:/Users/lulu/.codex/automations/mod4-10/automation.toml');actual=tomllib.loads(p.read_text('utf8'))
keys=dict(id='id',kind='kind',name='name',status='status',rrule='rrule',targetThreadId='target_thread_id',prompt='prompt')
if 'notificationPolicy' in req:keys['notificationPolicy']='notification_policy'
checks={k:req[k]==actual.get(v) for k,v in keys.items()};assert all(checks.values()),checks
h=lambda x:hashlib.sha256(x).hexdigest()
v=dict(epoch=time.time(),automation_id='mod4-10',all_fields_raw_exact=True,no_normalization_needed=True,field_exact=checks,prompt_SHA=h(actual['prompt'].encode()),requested_prompt_SHA=h(req['prompt'].encode()),toml_SHA=h(p.read_bytes()),same_ACTIVE_hourly_original_target=True,H1_complete57_original_disk_savedstop_verified_peer_headroom_and_pair7_PPO=True)
with (R/'V97_EXISTING_MONITOR_EXACT_READBACK_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(v,f,indent=2)
s=(T/'append_V96_postGit_monitor_ordinary_once.py').read_text('utf8')
assert s.count("BASE = 'c8374eb3020d632f6ba5c620ec565d47db89d0c8'")==1
s=s.replace("BASE = 'c8374eb3020d632f6ba5c620ec565d47db89d0c8'","BASE = 'b77c09cb8f843f99655acb9387ec58bb6f744cc2'").replace('H1_COMPLETE75_PEER_STORAGE_PPO_V96_POST_GIT_MONITOR_20261022','H1_COMPLETE57_PEER_HEADROOM_PAIR7_V97_POST_GIT_MONITOR_20261022').replace('V96_EXISTING_MONITOR_EXACT_READBACK_ACTUAL.json','V97_EXISTING_MONITOR_EXACT_READBACK_ACTUAL.json')
start=s.index('    files = [');end=s.index('    sys.path.insert',start)
files="""    files = [
        T / 'prepare_V97_existing_monitor_complete57_peer_headroom_pair7_once.py',
        T / 'verify_V97_actual_monitor_readback_and_prepare_postGit_once.py',
        Path(__file__).resolve(),
        R / 'V97_GIT_MAIN_ALL_TAGS_AND_TEXT_BLOBS_VERIFIED_RECEIPT_ACTUAL.json',
        R / 'V97_EXISTING_MONITOR_UPDATE_ARGS.json',
        R / 'V97_EXISTING_MONITOR_APP_RECEIPT_ACTUAL.json',
        R / 'V97_EXISTING_MONITOR_EXACT_READBACK_ACTUAL.json',
        started,
    ]
"""
s=s[:start]+files+s[end:]
s=s.replace('H1_complete75_original_disk_savedstop_peer_storage_and_both_PPO_single_postGit_receipt','H1_complete57_original_disk_savedstop_peer_headroom_pair7_PPO_single_postGit_receipt').replace('H1_previous_complete75_wholeCPU_passed=True','H1_previous_complete57_wholeCPU_passed=True').replace('Archive H1 complete75 peer storage and both PPO Git receipt with same monitor exact readback','Archive H1 complete57 peer headroom and pair7 PPO Git receipt with same monitor exact readback')
ast.parse(s);(T/'append_V97_postGit_monitor_ordinary_once.py').open('x',encoding='utf8').write(s)
print(json.dumps(dict(exact_readback=True,prompt_chars=len(actual['prompt']),postGit_helper_prepared=True)))
