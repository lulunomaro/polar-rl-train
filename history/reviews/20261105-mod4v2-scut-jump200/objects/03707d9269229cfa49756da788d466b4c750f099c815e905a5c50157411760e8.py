"""Actual complete final3786, native review and one sampler integration choice."""
from pathlib import Path
import hashlib,json,statistics,time
N=Path(__file__).resolve().parent;G=Path('C:/Users/lulu/Desktop/claude/mjcf/polar-rl-train')
D=G/'history/reviews/20261105-mod4v2-scut-jump200';S=N.parents[1]
A=N/'supermimic_first1941_reboot_periodic_1h';R=A/'reports'
read=lambda p:json.loads(Path(p).read_bytes())
f=read(R/'POSTROUND_FULL_RETURNED.json')['files'];diag=read(R/'SUPERMIMIC_CLOSED_LEARNER_AND_ALL80.json')
assert read(R/'POSTROUND_COMPLETED.json')['complete']and diag['passed']
assert f['OWNER_EXIT.json']['error']is None and f['OWNER_EXIT.json']['original_leases_released']
ck=f['production/FINAL.json']['checkpoint'];assert ck['iteration']==3786
media=[]
for report in sorted((A/'evaluation').rglob('RENDER_REPORT.json')):
    for path in read(report)['media']:
        p=Path(path);raw=p.read_bytes();media.append(dict(path=str(p),bytes=len(raw),SHA=hashlib.sha256(raw).hexdigest()))
assert len(media)==4
review=dict(epoch=time.time(),all_actual_images_reviewed=True,complete_all80_review=True,
    model_SHA=ck['SHA'],actual_saved_wxyz_poses=True,media=media,NN=0,physics=0,PT_reads=0,
    observations=['All4 early/late side/top current-model native reviewed',
        'Early spawn fall then compression/extension and short upward hops, not spawn success',
        'Late env0/40 backward drift and pitching then nonwheel contact termination; env1 low posture terminates1.04s',
        'Env41 survives7.98s with backward drift; no selected case approaches platform edge',
        'All80 rootxmaximum.491343 <.8; wholeclear/landed/success/topforce all0'],
    all80_success=0,decision='CONTINUE_SUPERMIMIC_AT_SAVED_BOUNDARY',
    next='One measured sampling integration segment fromfullfinal3786. Explicit userrequested performance optimization; no unchanged sampler hour, no skillprogress claim. Retain failure and reevaluate; no stairs.')
with(R/'ACTUAL_NATIVE_REVIEW.json').open('x',encoding='utf8')as stream:json.dump(review,stream,indent=2)
latest=f['production/LATEST_PROGRESS.json'];first=read(R/'FIRST_ACTUAL_RETURNED.json')['files']['production/FIRST_UPDATED.json']
new_samples=latest['sim_steps']-(first['sim_steps']-60000)
rows=f['evaluation/ALL80.json']['first_episodes'];owner=f['OWNER_EXIT.json']
out=dict(epoch=time.time(),checkpoint=ck,passed_complete_state=True,verified_new_H32=1845,
    actual_new_control_samples=new_samples,actual_owner_elapsed_seconds=owner['actual_elapsed_seconds'],
    owner_total_control_steps_per_second=new_samples/owner['actual_elapsed_seconds'],
    last_round_samples=60000,last_round_total_control_steps_per_second=60000/latest['iteration_seconds'],
    last_round_collection_steps_per_second=60000/latest['collection_seconds'],
    last_round_is_not_hour_mean=True,full_diagnosis=diag,native_review=review,
    periodic_full=f['production/PERIODIC_FULL.json'],
    eval_mean_controls=statistics.mean(x['controls']for x in rows),eval_mean_seconds=statistics.mean(x['controls']for x in rows)*.02,
    training_new_numerical_resets=973-361,training_new_constraint_resets=1538-778,
    full_worker_errors=[],all80_success=0,sole79388_completed_and_exited=True,
    cumulative_before=read(A/'PLAN.json')['cumulative_authorized_seconds_before_this_segment'],
    cumulative_upper_after=read(A/'PLAN.json')['cumulative_authorized_seconds_before_this_segment']+owner['actual_elapsed_seconds'],
    cumulative_kind='Preserve prior interruptedwindow upper estimate, append only actualownerelapsed; not inventedactualGPUcost',
    canonical_reads=0,canonical_writes=0,additional_PT_decodes=0)
with(R/'FINAL3786_BOUNDARY_REVIEW.json').open('x',encoding='utf8')as stream:json.dump(out,stream,indent=2)
for path in (D/'WORK_ORDER.json',S/'admin/CURRENT_STATE.json'):
    value=read(path);value['final3786_sampling_boundary']={k:out[k]for k in ('epoch','checkpoint','verified_new_H32',
        'actual_new_control_samples','actual_owner_elapsed_seconds','owner_total_control_steps_per_second',
        'last_round_total_control_steps_per_second','last_round_collection_steps_per_second','all80_success','cumulative_upper_after')}
    value['current_training']='ACTUAL_FINAL3786_SAFECLOSE_80_NATIVE_COMPLETE_SAMPLER_INTEGRATION_NEXT'
    value['next']='Prepare and launch tested sampling optimization fromactualfullfinal3786; originalhour/evalonce consumed. No stairs.'
    path.write_text(json.dumps(value,indent=2,ensure_ascii=False),encoding='utf8')
print(json.dumps({k:v for k,v in out.items()if k not in ('full_diagnosis','native_review','periodic_full')}))
