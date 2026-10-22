from pathlib import Path
import ast,hashlib,json,time,tomllib
T=Path(__file__).resolve().parent;R=T/'reports';req=json.loads((R/'V100_EXISTING_MONITOR_UPDATE_ARGS.json').read_bytes());p=Path('C:/Users/lulu/.codex/automations/mod4-10/automation.toml');actual=tomllib.loads(p.read_text('utf8'))
keys=dict(id='id',kind='kind',name='name',status='status',rrule='rrule',targetThreadId='target_thread_id',prompt='prompt')
if 'notificationPolicy' in req:keys['notificationPolicy']='notification_policy'
checks={k:req[k]==actual.get(v) for k,v in keys.items()};assert all(checks.values()),checks
H=lambda b:hashlib.sha256(b).hexdigest();v=dict(epoch=time.time(),automation_id='mod4-10',all_fields_raw_exact=True,no_normalization_needed=True,field_exact=checks,prompt_SHA=H(actual['prompt'].encode()),requested_prompt_SHA=H(req['prompt'].encode()),toml_SHA=H(p.read_bytes()),same_ACTIVE_hourly_original_target=True,H1_complete118_actual2401_passed_pair10_both_PPO=True,no_270mm_result_claim=True)
with (R/'V100_EXISTING_MONITOR_EXACT_READBACK_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(v,f,indent=2)
s=(T/'append_V99_postGit_monitor_ordinary_once.py').read_text('utf8');assert s.count("BASE = '8e270d1011bf6a41902bc22e6909fdebdcb7dec6'")==1
s=s.replace("BASE = '8e270d1011bf6a41902bc22e6909fdebdcb7dec6'","BASE = 'a1c6e8e3f3b2003494cd09894c3960a12ba7d679'").replace('H1_COMMAND_AUDIT_INSTALLED_PAIR9_V99_POST_GIT_MONITOR_20261022','H1_COMPLETE118_AUDIT2401_PAIR10_V100_POST_GIT_MONITOR_20261022').replace('V99_EXISTING_MONITOR_EXACT_READBACK_ACTUAL.json','V100_EXISTING_MONITOR_EXACT_READBACK_ACTUAL.json')
start=s.index('    files = [');end=s.index('    sys.path.insert',start)
s=s[:start]+'''    files = [
        T / 'prepare_V100_existing_monitor_complete118_pair10_once.py',
        T / 'verify_V100_monitor_and_prepare_one_postGit_once.py',
        Path(__file__).resolve(),
        R / 'V100_GIT_MAIN_ALL_TAGS_AND_TEXT_BLOBS_VERIFIED_RECEIPT_ACTUAL.json',
        R / 'V100_EXISTING_MONITOR_UPDATE_ARGS.json',
        R / 'V100_EXISTING_MONITOR_APP_RECEIPT_ACTUAL.json',
        R / 'V100_EXISTING_MONITOR_EXACT_READBACK_ACTUAL.json',
        started,
    ]
'''+s[end:]
start=s.index('    index = dict(epoch=');end=s.index("    path = D / 'COMPLETE_FILE_CAPTURE_INDEX.json'",start)
s=s[:start]+"    index = dict(epoch=time.time(),kind='H1_complete118_actual_audit2401_passed_pair10_both_PPO_postGit_receipt',entries=entries,ordinary_followup_only=True,no_new_record_or_tag=True,no_training_host_transport_GPU_PPO_or_account_write=True,existing_monitor_updated_and_raw_exact_readback_verified=True,H1_new_complete118_source=True,actual_GPU_control2401_passed=True,no_270mm_result_claim=True,deferred=['e2'])\n"+s[end:]
s=s.replace('Archive installed H1 audit repair pair9 Git receipt with same monitor exact readback','Archive H1 complete118 and actual audit2401 pair10 Git receipt with same monitor exact readback')
ast.parse(s);(T/'append_V100_postGit_monitor_ordinary_once.py').open('x',encoding='utf8').write(s)
print(json.dumps(dict(exact_readback=True,prompt_chars=len(actual['prompt']),one_postGit_helper_prepared=True)))
