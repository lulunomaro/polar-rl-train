"""Persist actualclosed1940 and the new fullrestore/update/sole receiver."""
from pathlib import Path
from datetime import datetime,timezone,timedelta
import json,time
N=Path(__file__).resolve().parent
G=Path('C:/Users/lulu/Desktop/claude/mjcf/polar-rl-train')
D=G/'history/reviews/20261105-mod4v2-scut-jump200'
P=N/'supermimic_final881_host_replay02_1h';A=N/'supermimic_final1940_residual025_1h'
read=lambda p:json.loads(Path(p).read_bytes())
old=read(P/'reports/POSTROUND_FULL_RETURNED.json')['files']
diag=read(P/'reports/SUPERMIMIC_CLOSED_LEARNER_AND_ALL80.json')
actual=read(A/'reports/FIRST_ACTUAL_RETURNED.json');f=actual['files']
validation=read(A/'reports/FIRST_VALIDATION.json')
first=f['production/FIRST_UPDATED.json'];restore=f['production/FULL_STATE_RESTORE.json']
assert validation['valid']and first['iteration']==1941 and first['new_verified_BPTT_steps']==1
assert restore['source_iteration']==1940 and restore['counts']['pi_bptt_optimizer_steps']==1908
assert restore['all4_optimizers_replay_RNG_7components_restored']
assert restore['target_policy_residual_scale']==.25
collector=read(A/'reports/POSTROUND_EXACT_CIM.json');go=f['GO_PRODUCTION.json']
plan=read(A/'PLAN.json');video=read(P/'evaluation/actual_video/RENDER_REPORT.json')
report=dict(epoch=time.time(),status='ACTUAL_VALID_FIRST1941_FULL1940_RESTORE_RESIDUAL025_SOLE75124',
    root=str(A),remote=plan['remote_root'],FIRST=first,restore=restore,GO=go,collector=collector,
    window_local={key:datetime.fromtimestamp(go[key],timezone(timedelta(hours=8))).isoformat()
        for key in ('learning_started_epoch','save_deadline','nominal_end_epoch')},
    previous_final1940=dict(checkpoint=old['production/FINAL.json']['checkpoint'],
        counts=diag['learner']['counts'],samples=diag['learner']['sim_steps'],
        source_PPO_preserved=True,all4Adam_replay_RNG_finite=True,
        independent80=diag['all80'],owner=old['OWNER_EXIT.json'],
        complete_worker_log=diag['logs']['WORKER.log'],complete_eval_log=diag['logs']['EVAL.log'],
        full_log_errors=diag['full_log_errors'],all4new_actualpose_images_native_reviewed=True,
        video=video,all4_video_keyframes_native_reviewed=True),
    residual025_candidate=read(N/'reports/FINAL1940_AND_RESIDUAL025_CANDIDATE.json'),
    candidate_native_reviewed=True,full_resume_local_test=read(N/'reports/RESIDUAL025_FULL_RESUME_TEST.json'),
    cumulative_actual_seconds_before=plan['cumulative_authorized_seconds_before_this_segment'],
    first_large_unclipped_gradients_are_finite=True,
    first_unclipped_parameter_grad=first['bptt']['parameter_grad_norm'],
    policy_grad_clip_norm=1.,policy_grad_clip_value=.1,
    high_imagined_objective_not_a_skill_claim=True,
    specific_change='Residual output1.0to.25, keep full learned weights/4Adam/replay/RNG/Fudan16/20k/physical interfaces',
    current_numerical_constraint_counts_are_restored_cumulative=True,
    current_new_first_numerical_resets=first['numerical_resets']-old['production/FINAL.json']['numerical_resets'],
    current_new_first_constraint_resets=first['constraint_resets']-old['production/FINAL.json']['constraint_resets'],
    next='Only exact75124local/errors/POSTROUND files whilehealthy; no secondSSH/PTdecode/reader/hotpatch. Originalowner fullsave/safeclose/immediate80, then uniqueSuperMimicdiagnosis and currentnativepose review. No stairs until actual200mmsuccess.')
with(N/'reports/FINAL1940_AND_VALID_FIRST1941_RESIDUAL025.json').open('x',encoding='utf8')as stream:json.dump(report,stream,indent=2)
with(P/'reports/FINAL1940_VIDEO_NATIVE_REVIEW.json').open('x',encoding='utf8')as stream:
    json.dump(dict(epoch=time.time(),model_SHA=diag['checkpoint']['SHA'],
        video=video['media_identity'][0],all4_keyframes_reviewed=True,
        observation='Actualmesh playback shows spawnfall then forwardlean/longlegs and low frontguidecontact before edge;0wholeclear/toplanding.',
        NN=0,physics=0,PT_reads=0),stream,indent=2)
for p in [N.parents[1]/'admin/CURRENT_STATE.json',D/'WORK_ORDER.json']:
    value=read(p)
    value.update(epoch=time.time(),current_training=report['status'],current_training_root=str(A),
        current_training_remote=plan['remote_root'],local_controller=collector,next=report['next'])
    value['newton_migration'].update(status=report['status'],current_root=str(A),
        current_remote=plan['remote_root'],source_root=str(P),source_iteration=1940,
        source_SHA=diag['checkpoint']['SHA'],FIRST=first,GO=go,FIRST_pending=False,
        production_running=True,sole_collector=collector)
    value['supermimic_interleaving'].update(current_root=str(A),FIRST=first,restore=restore,GO=go,
        sole_collector=collector,actual_launch_pending_FIRST=False,production_switch_ready=True,
        actual_final1940_complete=True,actual_final1940_unique_decode_done=True,
        actual_final1940_independent80_native_review_done=True,actual_final1940_success=0,
        policy_residual_scale=.25,source_BPTT_counts=diag['learner']['counts'],
        cumulative_actual_seconds_before_current=report['cumulative_actual_seconds_before'],
        next=report['next'],actual_final_review_pending=True)
    value['previous_supermimic_final1940']=report['previous_final1940']
    p.write_text(json.dumps(value,indent=2,ensure_ascii=False),encoding='utf8')
print(json.dumps(dict(saved=True,status=report['status'],window=report['window_local'],
    newFIRST=first['iteration'],sole=collector['row']['ProcessId'])))
