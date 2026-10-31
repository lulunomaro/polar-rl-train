"""Derive current primary status from the one admitted small-report capture."""
from pathlib import Path
from datetime import datetime,timezone,timedelta
import json,time,tomllib
N=Path(__file__).resolve().parent;R=N/'reports'
def read(p):return json.loads(Path(p).read_bytes())
def put(n,v):
    with (R/n).open('x',encoding='utf8') as f:json.dump(v,f,ensure_ascii=False,indent=2,allow_nan=False)
def bjt(t):return datetime.fromtimestamp(t,timezone(timedelta(hours=8))).isoformat()
v=read(R/'ROOT199_PRIMARY197_ONE_SAVED_STATUS_RETURNED_ACTUAL.json')
assert v['authority']['passed'] and v['authority']['current197_active_at_read']
closed=read(R/'ROOT199_PRIMARY_STATUS_ALL_SSH_CLOSED_SESSION_RESTORED_FREE.json')
assert closed['all_owned_SSH_closed'] and closed['SESSION_restored'] and closed['global_serial_client_lease']=='FREE'
rows={Path(r['path']).name:r['value'] for r in v['source210']['files']}
p=rows['LATEST_PROGRESS.json'];final=rows['FINAL.json'];exit_=rows['NODE_EXIT_ACTUAL.json'];terminal=rows['NODE_TERMINAL_ACTUAL.json']
assert final['passed'] and terminal['row']['returncode']==0 and not terminal['row']['original_error']
assert exit_['all_own_children_waited'] and exit_['private_EX_released']
assert 'ORIGINAL_ERROR.json' not in rows
go=final['original_finite_owner_GO'];meta=final['final'];updates=final['actual_new_PPO_updates']
assert updates==p['new_PPO_updates']==57 and meta['saved_iteration']==5310+updates
assert meta['Adam_min']==meta['Adam_max']==106240+20*updates
assert meta['epoch']>=go['save_deadline']
old=read(N/'SCHEDULE_PUBLIC.json')['experts']['h1_210']
old194=read(R/'ROOT197_SAVED194_INITIAL_CPU_RETURNED_ACTUAL.json')
total_updates=old194['actual_new_PPO_updates']+updates
summary=dict(epoch=time.time(),human='非分支训练的如何？跳了吗？',
    status='PRIMARY197_WORKER_SAVED_COMPLETE_AND_EXITED__COHORT_E0_STILL_PENDING',
    original_run_id=v['authority']['run_id'],source_status_epoch=v['source210']['epoch'],
    source_status_BJT=bjt(v['source210']['epoch']),primary_final_saved_BJT=bjt(meta['epoch']),
    primary_node_exit_BJT=bjt(exit_['epoch']),primary_exit_code=0,
    latest_segment_updates=updates,total_original194_and197_updates=total_updates,
    saved_iteration=meta['saved_iteration'],Adam17_step=meta['Adam_min'],
    latest_segment_own_transitions=p['new_environment_transitions'],total_own_transitions=total_updates*480000,
    total_used_learning_window_seconds=old['old194_used_seconds']+meta['epoch']-go['learning_started_epoch'],
    original7200_learning_window_deadline_met=True,complete_final_producer_metadata=meta,
    final_model_contents_or_integrity_not_read_in_this_status=True,
    node_children_waited=True,primary_private_EX_released=True,
    full_cohort_shared_locks_CNone_costs_formal_CPU='PENDING original combined normal collector, not inferred from primary node exit',
    diagnostic=p['original_jump_diagnostic'],
    diagnostics_scope='flight_environment_controls accumulates original literal.was_in_flight.sum eachcontrol; root maximum is absolute world height',
    physical_flight_clearance_landing_stability_success='NOT_MEASURED by this saved progress producer',
    no_unique_episode_env_or_success_count_inferred=True,
    E0_training_change_or_status_poll=0,normal_collector_before213339_calls=0,
    model_raw_NPZ_SDK_GPU_reads=0,checkpoint_transfer_or_hash=0,
    reward_DR400N50_physics_unchanged=True,
    next='Original combined normal197 collector after21:33:39; NEWformals CPU then distinct frozen action-driven plane flight/landing/standing-forward-reverse regression',
    no_automatic_new_learning=True)
put('CURRENT_ACTUAL199_PRIMARY197_COMPLETE_SAVED_STATUS_NO_JUMP_SKILL_CLAIM.json',summary)
a=tomllib.loads(Path('C:/Users/lulu/.codex/automations/mod4-10/automation.toml').read_text('utf8'))
assert a['id']=='mod4-10' and a['kind']=='heartbeat' and a['status']=='ACTIVE'
prefix=f'''CURRENT_ACTUAL199_PRIMARY197_FINISHED_SAVED_CONTACT_FLIGHT_DIAGNOSTIC_NOT_SKILL_20261031 supersedes all-primary-still-learning/FIRST-only/latest5367-unknown wording below. FIRST READ {R.as_posix()}/CURRENT_ACTUAL199_PRIMARY197_COMPLETE_SAVED_STATUS_NO_JUMP_SKILL_CLAIM.json and ROOT199_PRIMARY197_ONE_SAVED_STATUS_RETURNED_ACTUAL.json, then existing197 workorder/binding/actual refs. This is the same197/198 cohort, not a new training phase.
Human asked non-E0 main status/has it jumped. ROOT199 performed a NEW frozen necessary single read:72 three small exact197 authority JSONs then CLOSE72, strict210 four existing small progress/FINAL/node-terminal/node-exit JSONs (maximum5; ORIGINAL_ERROR absent). Original entry actuallyRC0/allSSHclosed/SESSIONrestored/FREE. No model/raw/NPZ/SDK/GPU/hash/download/account write or normal collector. Purpose CONSUMED, never repeat this human status as a watcher.
Primary197 actually complete saved2026-10-31T21:04:22.380441+08:00, node exit21:04:35.755487/waitRC0/all own children waited/privateEX released. New57PPO/27360000own transitions/iteration5367/17Adam107380; original194+197 total368updates/176640000transitions. Combined7200learning-window deadline met by saved epochs (actual7203.066868543625s), not claim7200s optimizer time. New final17520927B SHA f286110a39a1062f96fd21038c05b772da5f5a72ebdab8421c403f73e5cc3afe is producer metadata only; NO extra model content read/transfer/qualification yet. Original owner197 still active at this status because E0 slot remains; don't clear canonical/hotadd/restart primary/change197 binding or infer whole-cohort CNone/costs. E0 untouched, original save21:43:39/nominal21:48:39 and combined collector earliest21:33:39 remain.
Saved primary diagnostics18703691 flight-env-controls/1368controls from original was_in_flight flag, root absolute worldmax.7122137547m, newsegment cumulative orientation356/closure867/timeouts26841. These are contact-history exposure and absolute height, NOT wheel jump height/unique env/episode/success/controlled landing. Human was told signs of contact-detected airborne status but no verified stable jump yet; no270 success. Reward/commands/400N50DR/physics/guards remain literal and unchanged. After BOTH original closed formal collection/NEW CPU qualification, freeze a distinct action-driven evaluation for actual continuous dualwheel flight/wheel clearance/landing and standing/forward/reverse retention; no blind extra training, no oldraw/eval replay.
197 unique training tag already CONSUMED: main5ff7cc6ba3780c9b00b4fc8c9eec8b847f50f0f4/tagobj5f0a2d4171d5e5a8d73017f23a0344c8844b76da/1501tags, all1500 oldobjectspeels protected. This199source/status/fullUTF8/definition/automation receipt is ordinary197 append only, no newtag/record197. ActualHEAD/refs/index override this historical main string. All next197 normal collector/NEWformals CPU/security/serial/caps below retain; no early combined model collection or additional watcher.\n\n'''
req=dict(mode='update',id=a['id'],kind=a['kind'],name=a['name'],prompt=prefix+a['prompt'],status=a['status'],rrule=a['rrule'],targetThreadId=a['target_thread_id'])
if 'notification_policy' in a:req['notificationPolicy']=a['notification_policy']
put('AUTOMATION199_PRIMARY_COMPLETE_SAVED_STATUS_UPDATE_REQUEST.json',req)
print(json.dumps(dict(passed=True,total_updates=total_updates,iteration=meta['saved_iteration'],saved_BJT=bjt(meta['epoch']),scope='Contact-flight evidence only, stable jump not measured')))
