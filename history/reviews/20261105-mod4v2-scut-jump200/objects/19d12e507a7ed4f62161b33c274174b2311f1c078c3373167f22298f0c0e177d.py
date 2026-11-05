from pathlib import Path
from datetime import datetime,timezone,timedelta
import json,time
N=Path(__file__).resolve().parent;G=Path('C:/Users/lulu/Desktop/claude/mjcf/polar-rl-train')
D=G/'history/reviews/20261105-mod4v2-scut-jump200';A=N/'newton_fudan_final620_1h/episode_reset04'
read=lambda p:json.loads(Path(p).read_bytes())
actual=read(A/'reports/FIRST_ACTUAL_RETURNED.json');files=actual['files']
first=files['production/FIRST_UPDATED.json'];go=files['GO_PRODUCTION.json']
collector=read(A/'reports/POSTROUND_EXACT_CIM.json')
compat=read(N/'supermimic_compatibility01/RESULT.json');warm=read(N/'supermimic_compatibility01/WARMSTART_CPU.json')
assert first['iteration']==621 and compat['passed'] and warm['passed']
stamp=lambda epoch:datetime.fromtimestamp(epoch,timezone(timedelta(hours=8))).isoformat()
report=dict(epoch=time.time(),status='VALID_NEWTON_FIRST621_AND_SUPERMIMIC_H32_NATIVE_COMPATIBILITY',
    root=str(A),remote=read(A/'PLAN.json')['remote_root'],FIRST=first,
    full_state_restore=files['production/FULL_STATE_RESTORE.json'],GO=go,
    times={key:stamp(go[key])for key in ['learning_started_epoch','save_deadline','nominal_end_epoch']},
    sole_collector=collector,SuperMimic=compat,warmstart=warm,
    no_active_source_hotpatch=True,source_PPO_checkpoint_unchanged=True,
    production_BPTT_worker_not_yet_implemented=True,
    production_switch_ready=False,
    next='While sole35288 collects current one-hour PPO, complete finite BPTT worker/evaluator and preserve source PPO. At fullsave review numerical resets/all80/nativeplayback, then switch only through actual verified BPTT route.',
    performance=dict(first_control_samples_per_s=first['samples_per_second'],
        collection_s=first['collection_seconds'],learn_s=first['learning_seconds'],
        collection_fraction=first['collection_seconds']/(first['collection_seconds']+first['learning_seconds']),
        actual_physics_world_steps_per_control=8,whole_loop_graph=False,
        solver_graph=True,full_end_to_end_profile_not_done=True,
        old_driver_conditional_nodes_disabled=True))
with(A/'reports/VALID_FIRST621_AND_SUPERMIMIC_NATIVE_H32.json').open('x',encoding='utf8')as f:json.dump(report,f,indent=2)
for p in [N.parents[1]/'admin/CURRENT_STATE.json',D/'WORK_ORDER.json']:
 o=read(p);o.update(epoch=time.time(),current_training=report['status'],
    current_training_root=str(A),current_training_remote=report['remote'],
    local_controller=collector,next=report['next'])
 o['newton_migration'].update(status=report['status'],production_running=True,current_root=str(A),
    current_remote=report['remote'],FIRST=first,GO=go,sole_collector=collector,
    native_recipe='Fudan16 unchanged / 20k /400physics100feedback50policy',
    first_numerical_resets=47,full_end_to_end_profile_not_done=True)
 o['supermimic_interleaving'].update(implementation_started=True,
    started_after_actual_FIRST621=True,native_H32_BPTT_passed=True,
    four_optimizers_replay_RNG_save_restore_passed=True,
    PPO_warmstart_CPU_passed=True,source_binding=str(G/'project/isaac/mod4v2_scut/SUPERMIMIC_BINDINGS.json'),
    production_worker_pending=True,production_switch_ready=False,
    next='Implement finite worker/evaluate/resume for actual saved production PPO checkpoint; do not inject into running process')
 o['supermimic_interleaving'].pop('not_started_reason',None)
 o['other_automation_observed']={'id':'mod4-200-rl-bptt','actual':'ACTIVE foreign standing-forward chat',
    'action':'Not touched; historical PAUSED instruction is stale relative to actual foreign automation ownership'}
 p.write_text(json.dumps(o,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps(dict(saved=True,FIRST=621,local_times=report['times'],sole=35288,SuperMimic_H32_passed=True)))
