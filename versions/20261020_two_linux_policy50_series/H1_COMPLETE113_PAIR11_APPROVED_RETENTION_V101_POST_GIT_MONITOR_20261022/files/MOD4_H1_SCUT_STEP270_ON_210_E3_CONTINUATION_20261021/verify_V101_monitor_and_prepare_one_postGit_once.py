from pathlib import Path
import ast,hashlib,json,time,tomllib
T=Path(__file__).resolve().parent;R=T/'reports';req=json.loads((R/'V101_EXISTING_MONITOR_UPDATE_ARGS.json').read_bytes());p=Path('C:/Users/lulu/.codex/automations/mod4-10/automation.toml');actual=tomllib.loads(p.read_text('utf8'))
keys=dict(id='id',kind='kind',name='name',status='status',rrule='rrule',targetThreadId='target_thread_id',prompt='prompt')
if 'notificationPolicy' in req:keys['notificationPolicy']='notification_policy'
checks={k:req[k]==actual.get(v) for k,v in keys.items()};assert all(checks.values()),checks
H=lambda b:hashlib.sha256(b).hexdigest();v=dict(epoch=time.time(),automation_id='mod4-10',all_fields_raw_exact=True,no_normalization_needed=True,field_exact=checks,prompt_SHA=H(actual['prompt'].encode()),requested_prompt_SHA=H(req['prompt'].encode()),toml_SHA=H(p.read_bytes()),same_ACTIVE_hourly_original_target=True,current_pair11_both_PPO_and_explicit_approved_future_retention=True,retention_not_installed_or_270mm_success_claimed=True)
with (R/'V101_EXISTING_MONITOR_EXACT_READBACK_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(v,f,indent=2)
s=(T/'append_V100_postGit_monitor_ordinary_once.py').read_text('utf8');assert s.count("BASE = 'a1c6e8e3f3b2003494cd09894c3960a12ba7d679'")==1
s=s.replace("BASE = 'a1c6e8e3f3b2003494cd09894c3960a12ba7d679'","BASE = '7b45c1ca211c834ca62bee1ead76042aa8474bd6'").replace('H1_COMPLETE118_AUDIT2401_PAIR10_V100_POST_GIT_MONITOR_20261022','H1_COMPLETE113_PAIR11_APPROVED_RETENTION_V101_POST_GIT_MONITOR_20261022').replace('V100_EXISTING_MONITOR_EXACT_READBACK_ACTUAL.json','V101_EXISTING_MONITOR_EXACT_READBACK_ACTUAL.json')
start=s.index('    files = [');end=s.index('    sys.path.insert',start)
s=s[:start]+'''    files = [
        T / 'prepare_V101_existing_monitor_approved_future_retention_once.py',
        T / 'verify_V101_monitor_and_prepare_one_postGit_once.py',
        Path(__file__).resolve(),
        R / 'V101_GIT_MAIN_ALL_TAGS_AND_TEXT_BLOBS_VERIFIED_RECEIPT_ACTUAL.json',
        R / 'V101_EXISTING_MONITOR_UPDATE_ARGS.json',
        R / 'V101_EXISTING_MONITOR_APP_RECEIPT_ACTUAL.json',
        R / 'V101_EXISTING_MONITOR_EXACT_READBACK_ACTUAL.json',
        started,
    ]
'''+s[end:]
start=s.index('    index = dict(epoch=');end=s.index("    path = D / 'COMPLETE_FILE_CAPTURE_INDEX.json'",start)
s=s[:start]+"    index = dict(epoch=time.time(),kind='H1_complete113_episode_snapshot_pair11_PPO_explicit_approved_future_trace_retention_postGit',entries=entries,ordinary_followup_only=True,no_new_record_or_tag=True,no_training_host_transport_GPU_PPO_or_account_write=True,existing_monitor_updated_and_raw_exact_readback_verified=True,approved_retention_future_only_not_installed=True,no_formal_270mm_claim=True,deferred=['e2'])\n"+s[end:]
s=s.replace('Archive H1 complete118 and actual audit2401 pair10 Git receipt with same monitor exact readback','Archive complete113 pair11 and approved future retention Git receipt with same monitor exact readback')
ast.parse(s);(T/'append_V101_postGit_monitor_ordinary_once.py').open('x',encoding='utf8').write(s)
print(json.dumps(dict(exact_readback=True,prompt_chars=len(actual['prompt']),one_postGit_helper_prepared=True)))
