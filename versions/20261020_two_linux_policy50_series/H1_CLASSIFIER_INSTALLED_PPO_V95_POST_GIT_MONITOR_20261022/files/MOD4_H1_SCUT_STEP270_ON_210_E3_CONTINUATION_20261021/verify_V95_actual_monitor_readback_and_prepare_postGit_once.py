from pathlib import Path
import ast,hashlib,json,time,tomllib
T=Path(__file__).resolve().parent;R=T/'reports'
req=json.loads((R/'V95_EXISTING_MONITOR_UPDATE_ARGS.json').read_bytes());p=Path('C:/Users/lulu/.codex/automations/mod4-10/automation.toml');actual=tomllib.loads(p.read_text('utf8'))
keys=dict(id='id',kind='kind',name='name',status='status',rrule='rrule',targetThreadId='target_thread_id',prompt='prompt')
if 'notificationPolicy' in req:keys['notificationPolicy']='notification_policy'
checks={k:req[k]==actual.get(v) for k,v in keys.items()};assert all(checks.values()),checks
h=lambda x:hashlib.sha256(x).hexdigest()
v=dict(epoch=time.time(),automation_id='mod4-10',all_fields_raw_exact=True,all_fields_verified_with_explicit_final_LF_normalization=True,no_normalization_needed=True,field_exact=checks,prompt_SHA=h(actual['prompt'].encode()),requested_prompt_SHA=h(req['prompt'].encode()),toml_SHA=h(p.read_bytes()),same_ACTIVE_hourly_original_target=True,H1_FINAL14_wholeCPU_known_term_installed_both_actual_PPO=True)
with (R/'V95_EXISTING_MONITOR_EXACT_READBACK_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(v,f,indent=2)
s=(T/'append_V94_postGit_monitor_ordinary_once.py').read_text('utf8')
s=s.replace("BASE = 'fa447fb73541a15ec7e77e9131c5f7ee7c9421dd'","BASE = 'f1af05ac8f83e09ad18e9c4b3224f112882e4343'").replace('H1_QUERY_REPAIR_V94_POST_GIT_MONITOR_20261022','H1_CLASSIFIER_INSTALLED_PPO_V95_POST_GIT_MONITOR_20261022')
s=s.replace('V94_EXISTING_MONITOR_EXACT_READBACK_ACTUAL.json','V95_EXISTING_MONITOR_EXACT_READBACK_ACTUAL.json')
start=s.index('    files = [');end=s.index('    sys.path.insert',start)
files="""    files = [
        T / 'prepare_V95_existing_monitor_closed_CPU_classifier_PPO_handoff_once.py',
        T / 'verify_V95_actual_monitor_readback_and_prepare_postGit_once.py',
        Path(__file__).resolve(),
        R / 'V95_GIT_MAIN_ALL_TAGS_AND_TEXT_BLOBS_VERIFIED_RECEIPT_ACTUAL.json',
        R / 'V95_EXISTING_MONITOR_UPDATE_ARGS.json',
        R / 'V95_EXISTING_MONITOR_APP_RECEIPT_ACTUAL.json',
        R / 'V95_EXISTING_MONITOR_EXACT_READBACK_ACTUAL.json',
        started,
    ]
"""
s=s[:start]+files+s[end:]
s=s.replace('H1_early_FINAL14_known_term_classification_single_postGit_monitor_receipt','H1_FINAL14_wholeCPU_classifier_installed_both_actual_PPO_single_postGit_monitor_receipt')
s=s.replace('H1_early_complete_FINAL14_producer_only=True,known_term_classifier_not_installed=True,current_E3_pair_GO_PPO_historical=True, deferred=[]',"H1_previous_FINAL14_wholeCPU_passed=True,known_term_classifier_installed=True,current_both_actual_GO_PPO_historical_snapshots=True, deferred=['e2']")
s=s.replace('Archive H1 query repair Git receipt and same monitor exact readback','Archive installed H1 classifier and both PPO Git receipt with same monitor exact readback')
ast.parse(s);(T/'append_V95_postGit_monitor_ordinary_once.py').open('x',encoding='utf8').write(s)
print(json.dumps(dict(exact_readback=True,prompt_chars=len(actual['prompt']),postGit_helper_prepared=True)))
