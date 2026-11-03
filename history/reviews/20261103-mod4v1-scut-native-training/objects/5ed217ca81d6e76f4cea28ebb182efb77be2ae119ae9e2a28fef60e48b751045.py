"""Publish actual native diagnostic closure and current repaired FIRST/fullsave."""
from pathlib import Path
from datetime import datetime,timezone,timedelta
import json,time,hashlib

N=Path(__file__).resolve().parent;A=N/'env20000_repair_e0_1h_20261104';R=A/'reports';Q=N/'env20000_1h/action_clip_eval1'
G=Path('C:/Users/lulu/Desktop/claude/mjcf/polar-rl-train');D=G/'history/reviews/20261103-mod4v1-scut-native-training'
read=lambda p:json.loads(Path(p).read_bytes())
f=read(R/'FIRST_ACTUAL_RETURNED.json')['files'];first=f['production/FIRST_UPDATED.json'];go=f['GO_PRODUCTION.json']
assert first['actual_onpolicy_samples']==480000 and first['full_save']
assert first['gradient']['steps']==20 and first['gradient']['actor_norm']>0 and first['gradient']['critic_norm']>0
assert first['checkpoint']['format']=='MOD4V1_SCUT_FULL_V3'
binding=read(R/'POSTROUND_EXACT_CIM.json')
assert binding['row']['ProcessId']==52704
w=read(D/'WORK_ORDER.json')
stamp=datetime.now(timezone.utc).isoformat();local=lambda t:datetime.fromtimestamp(t,timezone(timedelta(hours=8))).isoformat()
w.update(captured_at=stamp,status='REPAIRED_E0_20000ENV1H_ACTUAL_GO_FIRST_FULLSAVE_LIVE',
    human_latest='找其他的卡，一共四张呢；同GPU少量占用可用；20000环境一小时',
    FIRST=first,GO=go,owner_current=f['OWNER_CURRENT.json'],worker=f['OWNER_CURRENT.json']['worker'],
    local_controller=binding['row'],local_controller_role='sole postround receiver; originalowner handles save/exit/eval',
    original_admission=f['ROOT_ADMISSION_ACTUAL.json'],
    initialization=f['production/FINETUNE_INITIALIZATION.json'],startup=f['production/STARTUP.json'],
    resource_blocker=None,original_save_local=local(go['save_deadline']),original_nominal_local=local(go['nominal_end_epoch']),
    training_completed=False,evaluation_completed=False,trained_skill=False,strict_successes=0,
    next='Sole localreceiver52704 alive: localreads only,no secondSSH/watcher/launch/FIRST/bind. It waits originalsave+45 then finite fullreturn after ownexit/independent80. View actual savedposes and all80/manifold, decide continuation; no oldonce replay.')
w['consumed']=['REPAIRED_E0_LAUNCH','REPAIRED_E0_FIRSTfinitewait','REPAIRED_E0_POSTROUND_BIND','REPAIRED_E0_POSTROUND_ONCE']
w['archive_previous_native_phase']=w.pop('archive',None)
w['archive']=dict(recorded=False,phase='mod4v1-scut-repair-native-e0-20000env1h',
    instruction='Record this new actual recovery phase once; afterwards ordinarysupplement. Existing nativephase tag remains protected.')
w['repair_implementation_commit']='bf08f3019a9176f10d4b5bf9c7fd008b3e52c333'
(D/'WORK_ORDER.json').write_text(json.dumps(w,ensure_ascii=False,indent=2),encoding='utf8',newline='\n')
S=N.parents[1];p=S/'admin/CURRENT_STATE.json';s=read(p)
s.update(epoch=time.time(),human_latest_request=w['human_latest'],current_training=w['status'],mod4v1_scut_native_20000_1h=w,next=w['next'])
s['archive_previous_phase']=s.get('archive');s['archive']=w['archive']
p.write_text(json.dumps(s,ensure_ascii=False,indent=2),encoding='utf8',newline='\n')
with(R/'FIRST_BIND_HANDOFF.json').open('x',encoding='utf8',newline='\n')as stream:json.dump(dict(captured_at=stamp,
    run_id=go['run_id'],GO=go,FIRST=first,source_initializer=w['initialization'],sole_receiver=binding,
    save_local=w['original_save_local'],nominal_local=w['original_nominal_local'],
    previous_diagnostic_native_review=str(Q/'reports/ACTUAL_REPAIRED_NATIVE_REVIEW.json'),
    no_skill_claim=True,no_extra_model_reads=0),stream,ensure_ascii=False,indent=2)
print(json.dumps(dict(status=w['status'],owner=w['launch']['pid'],worker=w['worker']['pid'],receiver=binding['row']['ProcessId'],
    save_local=w['original_save_local'],nominal_local=w['original_nominal_local'],fullsave_SHA=first['checkpoint']['SHA'])))
