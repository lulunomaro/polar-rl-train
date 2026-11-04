"""Review returned published-recipe trajectories; no model read or new physics."""
from pathlib import Path
import collections
import json
import time
import numpy as np

N=Path(__file__).resolve().parent
A=N/'env20000_published_recipe_1h_20261104/attempt02'
R=A/'reports'
read=lambda p:json.loads(Path(p).read_bytes())
returned=read(R/'POSTROUND_FULL_RETURNED.json');f=returned['files']
rows=f['evaluation/ALL80.json']['first_episodes'];curves=f['evaluation/CONTROL_CURVES.json']['curves']
controls=np.array([r['controls']for r in rows])
active=np.array([r['active']for r in curves]);actions=np.array([r['action']for r in curves])
applied=np.array([r['applied_action']for r in curves]);targets=np.array([r['joint_target']for r in curves])
contacts=np.array([r['reset_body_contact_force']for r in curves]);rp=np.array([r['roll_pitch_rad']for r in curves])
raw=np.array([r['termination_raw']for r in curves]);counter=np.array([r['termination_duration_counter']for r in curves])
t=np.load(A/'evaluation/actual400hz.npz');mask=t['active'];top=t['top_force'];names=f['evaluation/RESULT.json']['reset_contact_body_names']
assert len(rows)==80 and top.shape==(3200,80,2)
assert all(r['controls']*8==r['physics_ticks']for r in rows)
assert f['OWNER_EXIT.json']['all_own_waited']and f['OWNER_EXIT.json']['original_cost_settled']and f['OWNER_EXIT.json']['original_leases_released']
assert all(v is None for v in returned['exact_original_identities'].values())
assert abs(applied[active]).max()<=6
terminal=[]
for row in rows:
    if not row['terminated']:continue
    eid=row['env'];end=row['controls'];window=slice(end-20,end)
    contact=(contacts[window,eid]>1).any(-1)
    orientation=(abs(rp[window,eid])>np.deg2rad(40)).any(-1)
    assert raw[window,eid].all()and contact.all()and not orientation.any()
    assert counter[window,eid].tolist()==list(range(1,21))
    terminal.append(dict(env=eid,controls=end,
        consecutive_last20_contacts_over1={name:int((contacts[window,eid,i]>1).sum())for i,name in enumerate(names)},
        any_reset_body_over1_all20=True,orientation_over40_any=False,
        max_roll_pitch_deg=np.rad2deg(abs(rp[window,eid]).max(0)).tolist()))
assert len(terminal)==32
assert not(top[mask]>1).any()
lower=np.array([-1.2,-.5,-1.2,-.5]);upper=np.array([.9,.5,.9,.5])
xy=t['root_pos'][:,:,:2]-t['root_pos'][0,:,:2]
report=dict(epoch=time.time(),kind='PUBLISHED_RECIPE_FINAL_ACTUAL_NATIVE_REVIEW',
    final=f['production/FINAL.json'],latest_progress=f['production/LATEST_PROGRESS.json'],
    actual_samples=f['production/FINAL.json']['PPO_updates']*24*20000,
    train_closed=f['TRAIN_CLOSED.json'],owner_exit=f['OWNER_EXIT.json'],
    exact_original_identities_at_return=returned['exact_original_identities'],
    independent80=dict(result=f['evaluation/RESULT.json'],
        counts={key:sum(bool(r[key])for r in rows)for key in ('terminated','time_out','observation_outlier','closure_reset','mimic_reset','numerical_reset')},
        cap8s_without_task_done=sum(not r['terminated']and not r['time_out']for r in rows),
        controls=dict(min=int(controls.min()),mean=float(controls.mean()),max=int(controls.max()),mean_seconds=float(controls.mean()*.02)),
        all_3200_actual_callbacks_checked=True,anytop_envs=0,bothtop_envs=0,max_top_force=float(top[mask].max()),
        terminal_contact_path=terminal,
        actions=dict(raw_min=actions[active].min(0).tolist(),raw_max=actions[active].max(0).tolist(),
            raw_mean=actions[active].mean(0).tolist(),saturation_fraction=(abs(actions[active])>6).mean(0).tolist(),
            applied_max=float(abs(applied[active]).max())),
        targets=dict(lower=lower.tolist(),upper=upper.tolist(),first20_mean=targets[:20].mean((0,1)).tolist(),
            first20_above_upper_fraction=(targets[:20]>upper).mean((0,1)).tolist(),
            min=targets[active].min(0).tolist(),max=targets[active].max(0).tolist()),
        active_max_horizontal_displacement_from_first_callback_m=float(np.linalg.norm(xy,axis=-1)[mask].max()),
        selected={str(i):dict(controls=rows[i]['controls'],seconds=rows[i]['controls']*.02,
            terminated=rows[i]['terminated'],time_out=rows[i]['time_out'])for i in (0,1,40,41)}),
    native_visual_review=dict(current_model_view_image=True,images=4,quaternion='saved wxyz',
        render_reports=[str(A/'evaluation'/p/'RENDER_REPORT.json')for p in ('recorded_native','recorded_native_late')],
        findings='All selected robots descend into central low area in .2s. Env0 ends1.10s and env41 ends2.70s; later repeats are terminal clamp. Env1 and40 last8s below the platform; no actual tabletop support. Geometry alone does not classify contacts; all32 termination paths above use saved force/counter data.'),
    confirmed_gap=dict(upstream='Pinned base_env.py _apply_action lines2868-2878 clamps processed leg positions before target application',
        mod4='Shared DelayedJointPositionAction only scaled/default-offset and projected crank-hip difference; target hips exceeded actual±.5rad',
        repair='Four named contract motor limits and original CAD difference before existing D4 queue; PD/DC, physical constraints, rewards and termination unchanged',
        interface='FULL_V4 with explicit --repair-target-limits for old V3',
        causal_limit='Proven implementation gap, not proof it alone caused0jump. Same-final finite actual diagnostic required; original E0 also already saturated.'),
    decision='Run one bounded80 same-final target-limit diagnostic before any next20000x1h. No unchanged failed hour.',
    model_reads=0,optimizer_operations=0,new_physics=0)
with(R/'ACTUAL_PUBLISHED_RECIPE_FINAL_REVIEW.json').open('x',encoding='utf8')as stream:json.dump(report,stream,ensure_ascii=False,indent=2)
print(json.dumps(dict(samples=report['actual_samples'],counts=report['independent80']['counts'],
    cap8s=report['independent80']['cap8s_without_task_done'],termination_contact_verified=len(terminal),
    first20_hip_aboveupper=report['independent80']['targets']['first20_above_upper_fraction'])))
