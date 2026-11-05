from pathlib import Path
import hashlib,json,time

N=Path(__file__).resolve().parent
G=Path('C:/Users/lulu/Desktop/claude/mjcf/polar-rl-train')
D=G/'history/reviews/20261105-mod4v2-scut-jump200'
read=lambda p:json.loads(Path(p).read_bytes())
native=read(N/'supermimic_worker03/RESULT.json')
cli=read(N/'supermimic_cli04/FINAL.json')
resume=read(N/'supermimic_cli_resume05/FINAL.json')
evaluation=read(N/'supermimic_cli04/evaluation80/RESULT.json')
assert native['passed']and cli['verified_BPTT_steps']==2 and resume['verified_BPTT_steps']==3
assert evaluation['passed_execution']and evaluation['independent_first_episodes']==80
report=dict(epoch=time.time(),kind='SUPERMIMIC_FINITE_WORKER_RESUME_AND_EVALUATOR_NATIVE',
    production_PT_reads=0,remote_connections=0,current_production_changed=False,
    native_worker=native,finite_CLI=cli,resumed_finite_CLI=resume,
    evaluator={k:evaluation[k]for k in ('passed_execution','independent_first_episodes','seed',
        'optimizer_operations','source_SHA','jump200_success','jump200_wholeclear',
        'jump200_landed_top','ground_validated_flight','all80_manifold','actual_poses')},
    test_source='New local random PPO checkpoint only; not the production actor or production skill evaluation',
    replay_steps20k=64,replay_estimated_bytes20k=2261760000,
    actual_native_images_reviewed=True,
    image_paths=[str(N/'supermimic_cli04/evaluation80/recorded_native'/('local_bptt_test_'+view+'.png'))for view in ('side','top')],
    native_observation='env0/1/40/41 spawn descent, then pitched chassis and grounded wheels; end1.02-1.30s, no autonomous jump or top landing. Random local teacher test is only worker integration evidence.',
    original_failure_preserved=str(N/'supermimic_worker02/RESULT.json'),
    specific_failure_repair='Evaluator history now uses actual env.num_envs rather than hardcoded80; finite worker03 and80 evaluator pass',
    fullsave_safeexit_verified=True,numerical_invalid_replay_labels_excluded=True,
    learner_source_unchanged=True,own_original_PPO_source_complete_checkpoint_retained=True,
    physical_resume='7components/DR/RNG streams restored then declared fresh physical reset; replay seals stream boundary and clears observation history',
    production_switch_ready=False,
    pending='Current original one-hour PPO must return complete final/all80/native review; then prepare frozen SuperMimic segment and validate20k real runtime/admission/memory',
    reader_failures_preserved=[dict(path='runtime_refs/runtime/isaac/mod4/spring_pressure_component.py',reason='Components reside in referenced shared runtime, not narrow reset-bank references'),
        dict(path='runtime_refs/runtime/isaac/mod4/action_delay_physics_queue.py',reason='Same corrected reference runtime')])
with(N/'reports/SUPERMIMIC_FINITE_WORKER_AND_EVAL.json').open('x',encoding='utf8')as f:json.dump(report,f,indent=2)
for p in [N.parents[1]/'admin/CURRENT_STATE.json',D/'WORK_ORDER.json']:
    value=read(p)
    value['supermimic_interleaving'].update(production_worker_pending=False,
        finite_CLI_actual_BPTT_and_fullsave=True,finite_resume_BPTT=True,
        evaluator_native80_interface_passed=True,invalid_numerical_replay_excluded=True,
        replay_steps20k=64,replay_bytes_estimate20k=2261760000,
        report=str(N/'reports/SUPERMIMIC_FINITE_WORKER_AND_EVAL.json'),
        production_switch_ready=False,
        next='Original sole35288 finishes PPO/80; review newfinal actual80/poses/numerical resets. Then prepare_supermimic_boundary with true checkpoint/owner-release/native review and launch direct freeGPU finite H32 segment. No second current collector.')
    p.write_text(json.dumps(value,indent=2,ensure_ascii=False),encoding='utf8')
print(json.dumps(dict(saved=True,finite_BPTT_steps=2,resumed_BPTT_steps=3,local_test_eval_successes=0,production_unchanged=True)))
