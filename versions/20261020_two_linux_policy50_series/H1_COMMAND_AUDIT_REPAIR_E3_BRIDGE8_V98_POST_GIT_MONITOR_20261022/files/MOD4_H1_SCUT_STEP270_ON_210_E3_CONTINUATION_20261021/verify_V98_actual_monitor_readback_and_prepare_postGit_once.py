from pathlib import Path
import ast,hashlib,json,time,tomllib
T=Path(__file__).resolve().parent;R=T/'reports';req=json.loads((R/'V98_EXISTING_MONITOR_UPDATE_ARGS.json').read_bytes());p=Path('C:/Users/lulu/.codex/automations/mod4-10/automation.toml');actual=tomllib.loads(p.read_text('utf8'));keys=dict(id='id',kind='kind',name='name',status='status',rrule='rrule',targetThreadId='target_thread_id',prompt='prompt')
if 'notificationPolicy' in req:keys['notificationPolicy']='notification_policy'
checks={k:req[k]==actual.get(v) for k,v in keys.items()};assert all(checks.values()),checks
H=lambda b:hashlib.sha256(b).hexdigest();v=dict(epoch=time.time(),automation_id='mod4-10',all_fields_raw_exact=True,no_normalization_needed=True,field_exact=checks,prompt_SHA=H(actual['prompt'].encode()),requested_prompt_SHA=H(req['prompt'].encode()),toml_SHA=H(p.read_bytes()),same_ACTIVE_hourly_original_target=True,H1_failed100_not_a_FINAL_E3_continues_and_audit_CPU_uninstalled=True)
with (R/'V98_EXISTING_MONITOR_EXACT_READBACK_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(v,f,indent=2)
s=(T/'append_V97_postGit_monitor_ordinary_once.py').read_text('utf8');assert s.count("BASE = 'b77c09cb8f843f99655acb9387ec58bb6f744cc2'")==1;s=s.replace("BASE = 'b77c09cb8f843f99655acb9387ec58bb6f744cc2'","BASE = '8930b047d87bfe695dc895f91cd13b5c4e19cf0c'").replace('H1_COMPLETE57_PEER_HEADROOM_PAIR7_V97_POST_GIT_MONITOR_20261022','H1_COMMAND_AUDIT_REPAIR_E3_BRIDGE8_V98_POST_GIT_MONITOR_20261022').replace('V97_EXISTING_MONITOR_EXACT_READBACK_ACTUAL.json','V98_EXISTING_MONITOR_EXACT_READBACK_ACTUAL.json')
start=s.index('    files = [');end=s.index('    sys.path.insert',start)
files="""    files = [
        T / 'prepare_V98_existing_monitor_command_audit_repair_E3_bridge8_once.py',
        T / 'verify_V98_actual_monitor_readback_and_prepare_postGit_once.py',
        Path(__file__).resolve(),
        R / 'V98_GIT_MAIN_ALL_TAGS_AND_TEXT_BLOBS_VERIFIED_RECEIPT_ACTUAL.json',
        R / 'V98_EXISTING_MONITOR_UPDATE_ARGS.json',
        R / 'V98_EXISTING_MONITOR_APP_RECEIPT_ACTUAL.json',
        R / 'V98_EXISTING_MONITOR_EXACT_READBACK_ACTUAL.json',
        started,
    ]
"""
s=s[:start]+files+s[end:]
start=s.index('    index = dict(epoch=');end=s.index("    path = D / 'COMPLETE_FILE_CAPTURE_INDEX.json'",start)
index="""    index = dict(epoch=time.time(),kind='H1_failed100_legacy_zero_audit_CPU_repair_not_installed_E3_bridge8_PPO_postGit_receipt',entries=entries,ordinary_followup_only=True,no_new_record_or_tag=True,no_training_host_transport_GPU_PPO_or_account_write=True,existing_monitor_updated_and_canonical_readback_verified=True,H1_no_FINAL=True,H1_audit_candidate_CPU_not_installed=True,current_only_E3_bridge8_PPO_historical_snapshot=True,deferred=['e2','h1'])
"""
s=s[:start]+index+s[end:];s=s.replace('Archive H1 complete57 peer headroom and pair7 PPO Git receipt with same monitor exact readback','Archive H1 command audit repair and E3 bridge8 Git receipt with same monitor exact readback')
assert "receipt['all_fields_raw_exact']" in s;ast.parse(s);(T/'append_V98_postGit_monitor_ordinary_once.py').open('x',encoding='utf8').write(s)
print(json.dumps(dict(exact_readback=True,prompt_chars=len(actual['prompt']),postGit_helper_prepared=True)))
