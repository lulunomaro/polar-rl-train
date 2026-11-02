"""Follow-up quantitative explanation after native pose/curve review, no model IO."""
from pathlib import Path
import csv,hashlib,json,time
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
N=Path(__file__).resolve().parent;T=N.parent;R=N/'reports'
read=lambda p:json.loads(p.read_bytes())
def put(p,v):
    with p.open('x',encoding='utf8')as f:json.dump(v,f,indent=2,ensure_ascii=False,allow_nan=False)
def ident(p):return dict(path=str(p),bytes=p.stat().st_size,SHA=hashlib.sha256(p.read_bytes()).hexdigest())
analysis=read(R/'ANALYSIS457_ACTUAL446_ROUTE_ACTION_CONTACT_REWARD.json')
receipt=read(T/'RL445_ACTUAL446_REPLAY_RECOVERY_V451_20261102/reports/ROOT451_ACTUAL446_SELECTED_REPLAY_TRANSFERS.json')
S=T/'RL_SATURATION_ACTUAL_PPO_PRODUCTION_V445_20261102';cmd=np.asarray(read(S/'feedforward389.json')['commands'])
full=read(T/'RL445_FINAL_INDEPENDENT_EVAL_V446_20261102/reports/ROOT446_EVALUATION_FULL_RETURNED.json')
manifold=json.loads(next(r['UTF8']for r in full['full_UTF8']if r['path'].endswith('CONTACT_MANIFOLD_LATCHED_LANDING_TRACE.json')))
alltop=np.asarray([r['top_force_N']for r in manifold['rows']]);assert alltop.max()==0
cases=[];colors=['#2364aa','#b43c39','#279063','#8c55a5'];artifacts=[]
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':11,'axes.grid':True,'grid.alpha':.22})
fig,axes=plt.subplots(2,3,figsize=(17,10),layout='constrained')
for color,row in zip(colors,receipt['cases']):
    with np.load(row['local_path'],allow_pickle=False)as z:p={k:z[k].copy()for k in z.files}
    n=row['controls'];t=np.arange(1,n+1)*.02;root=p['root13'];x,y,z,w=root[:,3:7].T
    yaw=np.arctan2(2*(w*z+x*y),1-2*(y*y+z*z));track=np.linalg.norm(p['body_position_w'][0,row['body_names'].index('left_wheel'),:2]-p['body_position_w'][0,row['body_names'].index('right_wheel'),:2])
    d=p['motor_dq'][:,5]-p['motor_dq'][:,2]
    kinematic=np.cumsum((np.r_[0,d[:-1]]+d)*.5)*.02*.0637/track
    ground=np.asarray([r['ground_force_N'][row['env']]for r in manifold['rows']]);air=np.all(ground<1,axis=-1)
    # First continuous flight interval that lasts at least20ms (exclude unloading chatter).
    starts=np.flatnonzero(air&~np.r_[False,air[:-1]]);ends=np.flatnonzero(air&~np.r_[air[1:],False]);flights=[]
    for start,end in zip(starts,ends):
        if end-start+1>=8:
            flights.append(dict(takeoff_s=float((start+1)*.0025),first_ground_return_s=float((end+2)*.0025),duration_s=float((end-start+1)*.0025)))
    firstflight=next((f for f in flights if f['takeoff_s']>.5),None)
    front=[]
    for sample in manifold['selected_solver_contact_points']:
        for contact in sample['contacts']:
            if contact['env']!=row['env']:continue
            for force,pos,normal in zip(contact['force_N'],contact['position_relative'],contact['normal_w']):
                if abs(pos[0]-.8)<.025 and pos[2]>.02 and pos[2]<.267 and abs(normal[0])>.8:
                    front.append(dict(time_s=sample['tick']*.0025,force_N=force,position=pos,normal=normal))
    earliest_invalid=np.flatnonzero(p['depth9'][:,8]==0)
    checks=[]
    for sec in(.2,.4,.6):
        i=round(sec/.02)-1;checks.append(dict(time_s=sec,measured_yaw_rad=float(yaw[i]),differential_drive_integral_rad=float(kinematic[i])))
    native=dict(env=row['env'],first20_depth_valid_fraction=float(p['depth9'][:20,8].mean()),first_depth=p['depth9'][0].tolist(),
        first_invalid_depth_control_start_s=float(earliest_invalid[0]*.02)if len(earliest_invalid)else None,
        first20_feedforward_wheel_mean_rad_s=cmd[:20][:,[2,5]].mean(0).tolist(),
        first20_requested_wheel_mean_rad_s=p['motor_vel_target'][:20][:,[2,5]].mean(0).tolist(),
        first20_measured_wheel_mean_rad_s=p['motor_dq'][:20][:,[2,5]].mean(0).tolist(),wheel_track_initial_m=float(track),
        yaw_integral_checks=checks,first_continuous_flight=firstflight,first_front_contact=front[0]if front else None,
        differential_yaw_scope='Simple rolling kinematic consistency using recorded actual wheel speeds/radius/track, not a new dynamics rollout. Agreement at.4s supports wheel-differential explanation; later slip/leg geometry cause mismatch.')
    cases.append(native)
    axes[0,0].plot(t,np.rad2deg(yaw),c=color,label=f'env{row["env"]} actual')
    axes[0,0].plot(t,np.rad2deg(kinematic),c=color,ls=':',alpha=.7)
    axes[0,1].plot(t,p['depth9'][:,8],c=color,label=f'env{row["env"]}')
    with(N/f'env{row["env"]}_aligned_control_curves.csv').open(encoding='utf8')as f:
        table=list(csv.DictReader(f));num=lambda k:np.asarray([float(r[k])for r in table])
    axes[0,2].plot(t,num('tracking_reward'),c=color,label=f'env{row["env"]}')
    axes[1,0].plot(t,num('yaw_rad')*180/np.pi,c=color,label=f'env{row["env"]}')
    axes[1,1].plot(t,p['body_position_w'][:,[row['body_names'].index('left_wheel'),row['body_names'].index('right_wheel')],2].min(-1)-row['origin'][2]-.0637,c=color,label=f'env{row["env"]}')
    axes[1,2].plot(t,num('root_x'),c=color,label=f'env{row["env"]} root')
axes[0,0].set(xlim=(0,.6),title='Yaw agrees with integrated wheel difference',ylabel='degrees');axes[0,0].text(.01,42,'Solid: measured yaw\nDotted: r/b integral(wR-wL)dt',fontsize=9)
axes[0,1].set(xlim=(0,1.3),ylim=(-.1,1.1),title='Depth target valid at onset of route deviation',ylabel='valid=1 / missing=0')
axes[0,2].set(xlim=(0,1.6),title='Wrong initial posture still earns high reward',ylabel='exp(-tracking cost/5)')
axes[1,0].set(xlim=(0,1.6),title='Yaw error persists into takeoff',ylabel='degrees')
axes[1,1].axhline(.27,c='k',ls='--',label='270mm platform top');axes[1,1].set(xlim=(0,1.6),title='Both wheels must lift above the top',ylabel='lower wheel bottom estimate (m)')
axes[1,2].axhline(.8,c='k',ls='--',label='platform front');axes[1,2].set(xlim=(0,1.6),title='Jump ends before reaching the platform',ylabel='forward x (m)')
for ax in axes.flat:ax.set_xlabel('recorded endpoint time (s)');ax.legend(fontsize=8)
fig.suptitle('Why this route: learned wheel difference starts early; target initially visible; leap falls short',fontsize=17)
path=N/'06_early_route_depth_and_reward_evidence.png';fig.savefig(path,dpi=150);plt.close(fig);artifacts.append(ident(path))
# Compact readable publication figure for the human reply.
fig,axes=plt.subplots(1,3,figsize=(16,4.8),layout='constrained')
for color,row in zip(colors,receipt['cases']):
    with(N/f'env{row["env"]}_aligned_control_curves.csv').open(encoding='utf8')as f:table=list(csv.DictReader(f));num=lambda k:np.asarray([float(r[k])for r in table])
    axes[0].plot(num('root_x'),num('root_y'),c=color,label=f'env{row["env"]}')
    axes[1].plot(num('time_s'),num('yaw_rad')*180/np.pi,c=color,label=f'env{row["env"]}')
    with np.load(row['local_path'],allow_pickle=False)as p:
        wi=[row['body_names'].index(n)for n in('left_wheel','right_wheel')];bottom=p['body_position_w'][:,wi,2].min(-1)-row['origin'][2]-.0637
    axes[2].plot(num('time_s'),bottom,c=color,label=f'env{row["env"]}')
    if row['env']==0:
        axes[0].plot(num('ref_x'),num('ref_y'),'k--',lw=2,label='planned route')
axes[0].axvline(.8,c='#008ac3',label='platform edge');axes[0].set(title='Actual route vs planned straight approach',xlabel='forward x (m)',ylabel='lateral y (m)',xlim=(-.05,1.45),ylim=(-.2,.7))
axes[1].set(title='Yaw before/through takeoff',xlabel='time (s)',ylabel='degrees',xlim=(0,1.6))
axes[2].axhline(.27,c='k',ls='--',label='platform top');axes[2].set(title='Lowest wheel bottom vs platform top',xlabel='time (s)',ylabel='height (m)',xlim=(0,1.6))
for ax in axes:ax.legend(fontsize=8)
fig.suptitle('Actual final445 / independent446: turns early, lifts too little, lands before edge',fontsize=16)
path=N/'07_human_route_yaw_wheel_clearance_summary.png';fig.savefig(path,dpi=150);plt.close(fig);artifacts.append(ident(path))

native_review=dict(current_model_native_review=True,body_pose_frames=400,cases=[0,40,1,41],visualized_saved_PhysX_bodyposes_only=True,
    viewed_images=[str(N/'DENSE457_NATIVE_RECORDED_POSES'/name)for name in('env0_side_dense_0_to_8s.png','env0_top_dense_0_to_8s.png','env40_top_dense_0_to_8s.png','env1_side_dense_0_to_8s.png','env41_side_dense_0_to_8s.png','frames/frame_0054.png','frames/frame_0122.png')],
    observation='All4 early yaw/lean before airborne. First jump rises and descends in front of platform; recorded ground manifold resumes around1.1s before xedge. Env0/1/41 later reach the front vertical wall on ground and brace; env40 turns away on ground. None is an attempted first-flight landing on top.',
    old_copied446_replay_not_used=True,not_all80_video=True)
report=dict(epoch=time.time(),passed=True,cases=cases,native_review=native_review,all80_top_force_absolute_max_N=float(alltop.max()),
    evidence_priority=['Actual445model SHA and actual446 acceptance','Recovered451 verified saved poses','Actual400Hz solver contacts and named actuator trace','Reward reconstruction matches original per-term means','Rolling-kinematic consistency as supporting calculation'],
    measured_conclusions=[
        'Policy wheel residual creates ~12rad/s early differential target against nearly symmetric saved feedforward; measured wheel differential explains early yaw to within ~0.005rad env0 at.4s.',
        'Initial depth target is detected270mm, valid all first20controls in allfour; early turn cannot be attributed simply to initial blindness. Later depth losses follow yaw/pitch growth; policy sensitivity to those inputs not causally isolated.',
        'At.4s env0 has yaw31.08deg and pitch22.05deg but reward.9637. Rotation matrix mean cost contributes.0383 before exponential/divide5; large attitude error is weak relative to this early reward scale.',
        'Four cases have wheel center maxima below.287m and wheel bottom maxima below.223m. Required top clearance approx.334m center for upright radius.0637. Initial jump lacks vertical and forward reach.',
        'Actualfirst flight ends on ground before frontwall. First saved verticalwall contacts are2.12/2.30/2.46s atz.05-.06, not1.0s topedgecollision. Never all80topforce>0.',
        'No route planner chooses a bypass. A reference-conditioned actor adds motor residuals; learned differential and leg asymmetry make an emergent curved trajectory.',
        'Failedbracing reward~.22/frame and no explicit topmanifold success term permit positive survival return; wrong route still gets large positioncost. Survival localoptimum is a plausible learning failure, not proved unique cause.'
    ],
    decision='Finish alreadyrunning455 and sole456 fullsave/eval; compare early asymmetric commands, yaw, wheelheight and landing. Do not call lifetime/loss progress a skill improvement, do not start another unchangedhour or alter physics/reward during455.',
    untested=['Counterfactual fulltrajectory with wheel residual removed','Critic advantage causality for early yaw','Depth input causal sensitivity','Stable successful RL top landing'],
    artifacts=artifacts,modelreads=0,NNinference=0,SDK=0,physics_steps=0,network=0)
put(R/'NATIVE457_ROUTE_CAUSAL_EVIDENCE_AND_LIMITS.json',report)
print(json.dumps(dict(passed=True,cases=cases,all80_top_force_max=float(alltop.max()),artifacts=artifacts),indent=2),flush=True)
