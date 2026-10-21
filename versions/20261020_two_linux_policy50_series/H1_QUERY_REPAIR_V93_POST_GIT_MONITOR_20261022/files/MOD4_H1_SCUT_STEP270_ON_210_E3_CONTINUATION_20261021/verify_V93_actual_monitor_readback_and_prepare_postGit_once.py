from pathlib import Path
import ast,hashlib,json,time,tomllib
T=Path(__file__).resolve().parent;R=T/'reports';G=T.parent/'polar-rl-train'
req=json.loads((R/'V93_EXISTING_MONITOR_UPDATE_ARGS.json').read_bytes());p=Path('C:/Users/lulu/.codex/automations/mod4-10/automation.toml');actual=tomllib.loads(p.read_text('utf8'))
keys=dict(id='id',kind='kind',name='name',status='status',rrule='rrule',targetThreadId='target_thread_id',prompt='prompt')
if 'notificationPolicy' in req:keys['notificationPolicy']='notification_policy'
checks={k:req[k]==actual.get(v) for k,v in keys.items()};assert all(checks.values()),checks
h=lambda x:hashlib.sha256(x).hexdigest()
v=dict(epoch=time.time(),automation_id='mod4-10',all_fields_raw_exact=True,all_fields_verified_with_explicit_final_LF_normalization=True,no_normalization_needed=True,field_exact=checks,prompt_SHA=h(actual['prompt'].encode()),requested_prompt_SHA=h(req['prompt'].encode()),toml_SHA=h(p.read_bytes()),same_ACTIVE_hourly_original_target=True,H1_failed_repair_not_installed_E3_bridge7_actual_PPO=True)
with (R/'V93_EXISTING_MONITOR_EXACT_READBACK_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(v,f,indent=2)
old=(T/'append_V92_actual_PPO_postGit_monitor_V2_ordinary_once.py').read_text('utf8')
new=old.replace("BASE = '2874aedc26db486ea19e4a2328ee2f746af1d6e6'","BASE = '5678e3fe73bd12163d6c713a6e528b0063f2e76c'").replace('H1_STEP270_PPO_V92_POST_GIT_MONITOR_20261021','H1_QUERY_REPAIR_V93_POST_GIT_MONITOR_20261022')
new=new.replace('V92_EXISTING_MONITOR_EXACT_READBACK_ACTUAL.json','V93_EXISTING_MONITOR_EXACT_READBACK_ACTUAL.json')
start=new.index('    files = [');end=new.index('    sys.path.insert',start)
files="""    files = [
        T / 'prepare_V93_existing_monitor_actual_failure_repair_handoff_once.py',
        T / 'verify_V93_actual_monitor_readback_and_prepare_postGit_once.py',
        Path(__file__).resolve(),
        R / 'V93_GIT_MAIN_ALL_TAGS_AND_TEXT_BLOBS_VERIFIED_RECEIPT_ACTUAL.json',
        R / 'V93_EXISTING_MONITOR_UPDATE_ARGS.json',
        R / 'V93_EXISTING_MONITOR_APP_RECEIPT_ACTUAL.json',
        R / 'V93_EXISTING_MONITOR_EXACT_READBACK_ACTUAL.json',
        started,
    ]
"""
new=new[:start]+files+new[end:]
new=new.replace('actual_H1_step270_E3_PPO_single_postGit_monitor_receipt','H1_failed_query_arena_repair_E3_bridge7_single_postGit_monitor_receipt').replace('Archive H1 step270 PPO actual Git receipt and same monitor exact readback','Archive H1 query repair Git receipt and same monitor exact readback')
new=new.replace('no_new_H1_GO_since_first_metadata_or_skill_result=True','H1_failed_no_FINAL_and_repair_not_installed=True,E3_bridge7_actual_GO_PPO=True')
ast.parse(new);(T/'append_V93_postGit_monitor_ordinary_once.py').write_text(new,encoding='utf8')
print(json.dumps(dict(exact_readback=True,prompt_chars=len(actual['prompt']),postGit_helper_prepared=True)))
