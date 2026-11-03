"""Review returned actual first80 and native-viewed poses; no model/physics."""
from pathlib import Path
import collections,json,time
import numpy as np

N=Path(__file__).resolve().parent;Q=N/'env20000_1h/action_clip_eval1'
read=lambda p:json.loads(Path(p).read_bytes())
f=read(Q/'reports/FULL_RETURNED.json')['files'];rows=f['evaluation/ALL80.json']['first_episodes']
curves=f['evaluation/CONTROL_CURVES.json']['curves'];controls=np.array([r['controls']for r in rows])
act=np.array([c['action']for c in curves]);ap=np.array([c['applied_action']for c in curves]);active=np.array([c['active']for c in curves]);targets=np.array([c['joint_target']for c in curves])
t=np.load(Q/'evaluation/actual400hz.npz');p=np.load(Q/'evaluation/selected_actual_poses.npz')
assert t['top_force'].shape==(3192,80,2)
assert not np.any(t['top_force'][t['active']]>1)
assert all(r['observation_debug_step']==0 and not r['observation_debug_enabled']for r in rows)
assert np.max(np.abs(ap[active]))<=6
report=dict(epoch=time.time(),kind='ACTUAL_REPAIRED_SAMEFINAL_NATIVE_REVIEW',result=f['evaluation/RESULT.json'],
    counts={key:sum(bool(r[key])for r in rows)for key in ('terminated','time_out','observation_outlier','closure_reset','mimic_reset','numerical_reset')},
    controls=dict(min=int(controls.min()),max=int(controls.max()),mean=float(controls.mean()),mean_seconds=float(controls.mean()*.02),
        hist=dict(collections.Counter(controls.tolist()))),
    terminated_duration_counts=sorted(set(r['termination_duration_counter']for r in rows if r['terminated'])),
    raw_action_min=act[active].min(0).tolist(),raw_action_max=act[active].max(0).tolist(),
    applied_max=float(np.abs(ap[active]).max()),saturation_fraction=np.mean(np.abs(act[active])>6,0).tolist(),
    target_min=targets[active].min(0).tolist(),target_max=targets[active].max(0).tolist(),
    debug_clock_all_zero=True,selected={str(i):dict(controls=rows[i]['controls'],termination=rows[i]['terminated'],timeout=rows[i]['time_out'])for i in (0,1,40,41)},
    poses=dict(samples=p['tick'].shape[0],actual_saved_poses=True),
    actual_manifold_ticks=int(len(t['tick'])),native_visual_review=dict(reviewed_by='current model native view_image',
        reports=[str(Q/'evaluation'/x/'RENDER_REPORT.json')for x in ('recorded_native','recorded_native_late')],
        images=4,selected=[0,1,40,41],observation='Early roots descend by .2s; selected robots remain inside central low area. Env0 and41 end near1.56/1.54s, late repeats are terminalclamp. Env1/40 persist to7.98s near ground, no actual tabletop support. Projection alone does not classify all nonwheel collisions.'),
    original_mean_controls=11.775,comparison_caveat='Samefinal/seed but corrected execution/lifecycle changes DR sampling history; not independent proof of each fix isolated',
    runtime_fixes_actual_verified=['applied action bounded6','source debug clock remains disabled0','no raw-outlier reset','pre-reset diagnostic targets/reasons returned','finite ownwait/release'],
    checkpoint_optimizer_operations=0,physics_started_by_analysis=0,model_reads=0,
    release=f['RELEASE.json'],decision='Do not continue the degraded305f final unchanged. Reinitialize from original mature enhancedMOD4v1 E06cdac1… with SCUT weights-only/freshAdam under repaired source;20000x3600+300, same originalcanonical, unchangedPPO/reward/spawn/physics.')
with(Q/'reports/ACTUAL_REPAIRED_NATIVE_REVIEW.json').open('x',encoding='utf8',newline='\n')as stream:json.dump(report,stream,ensure_ascii=False,indent=2)
print(json.dumps(dict(controls=report['controls'],counts=report['counts'],applied_max=report['applied_max'],first_axis_saturation=report['saturation_fraction'][0],strict=0,decision=report['decision'])))
