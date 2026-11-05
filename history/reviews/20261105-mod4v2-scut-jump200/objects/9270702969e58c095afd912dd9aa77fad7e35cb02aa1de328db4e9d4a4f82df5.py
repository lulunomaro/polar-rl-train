"""Record the completed original review and separate bounded-residual trial."""
from pathlib import Path
import json,time
N=Path(__file__).resolve().parent
A=N/'supermimic_final881_host_replay02_1h';B=N/'residual025_final1940_eval80'
read=lambda p:json.loads(Path(p).read_bytes())
f=read(A/'reports/POSTROUND_FULL_RETURNED.json')['files']
assert read(A/'reports/POSTROUND_COMPLETED.json')['complete']
assert not f['OWNER_EXIT.json']['error']and f['OWNER_EXIT.json']['all_own_waited']
assert read(A/'reports/SUPERMIMIC_CLOSED_LEARNER_AND_ALL80.json')['passed']
native=dict(epoch=time.time(),all_actual_images_reviewed=True,complete_all80_review=True,
    model_SHA=f['production/FINAL.json']['checkpoint']['SHA'],
    images=[str(A/'evaluation'/folder/('actual_supermimic_final1940_'+view+'.png'))
        for folder in ('recorded_native','recorded_native_late')for view in ('side','top')],
    observation='All4 selected early spawn descent; late forward lean, extended virtual legs and guide06 touches floor at.72-.86s. No airborne edge clearance or platform landing.',
    all80=dict(terminated=80,controls_min=34,controls_max=52,numerical_resets=0,
        constraint_resets=0,wholeclear=0,toplanding=0,success=0,guide06_terminal_contact=80),
    decision='TEST_BOUNDED_RESIDUAL_WITH_COMPLETE_FINAL1940_RESTORE',
    original_failure_preserved=True,physics_reward_acceptance_changed=False)
with(A/'reports/ACTUAL_NATIVE_REVIEW.json').open('x',encoding='utf8')as stream:json.dump(native,stream,indent=2)
files={'evaluation/'+name:read(B/name)for name in ('RESULT.json','ALL80.json')}
with(B/'LOCAL_TEST_RETURNED.json').open('x',encoding='utf8')as stream:
    json.dump(dict(epoch=time.time(),files=files,original_policy_evaluation=False,
        candidate_residual_scale=.25,SSH=0),stream,indent=2)
rows=files['evaluation/ALL80.json']['first_episodes']
report=dict(epoch=time.time(),source_original_final=f['production/FINAL.json']['checkpoint'],
    original_final_native_review=native,candidate_result=files['evaluation/RESULT.json'],
    candidate_envs=80,candidate_mean_controls=sum(x['controls']for x in rows)/80,
    candidate_timeout_count=sum(x['time_out']for x in rows),
    candidate_control_range=[min(x['controls']for x in rows),max(x['controls']for x in rows)],
    original_mean_controls=sum(x['controls']for x in f['evaluation/ALL80.json']['first_episodes'])/80,
    hardware_comparison='Original formalRTX4090/CUDA12.2 versus bounded-residual local5070Ti/CUDA13.2, bothseed9137/80/400Hz; no samehardware speedup claim',
    candidate_model_unchanged=True,only_residual_output_scale=.25,
    candidate_has_not_learned_jump=True,candidate_native_review_pending=True,
    production_checkpoint_reads=dict(unique_closed_diagnosis=1,separate_candidate_inference=1,archive=0))
with(N/'reports/FINAL1940_AND_RESIDUAL025_CANDIDATE.json').open('x',encoding='utf8')as stream:json.dump(report,stream,indent=2)
print(json.dumps(dict(original_native_saved=True,candidate_controls_mean=report['candidate_mean_controls'],candidate_timeout=report['candidate_timeout_count'])))
