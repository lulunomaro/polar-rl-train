"""Offline actual446 diagnosis. Recorded measurements only; no NN/SDK/new physics."""
from pathlib import Path
import csv
import hashlib
import io
import json
import time
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

N=Path(__file__).resolve().parent;T=N.parent;R=N/'reports';R.mkdir(exist_ok=True)
E=T/'RL445_FINAL_INDEPENDENT_EVAL_V446_20261102'
C=T/'RL445_ACTUAL446_REPLAY_RECOVERY_V451_20261102'
S=T/'RL_SATURATION_ACTUAL_PPO_PRODUCTION_V445_20261102'
read=lambda p:json.loads(p.read_bytes())
def put(p,v):
    with p.open('x',encoding='utf8')as f:json.dump(v,f,indent=2,ensure_ascii=False,allow_nan=False)
def ident(p):return dict(path=str(p),bytes=p.stat().st_size,SHA=hashlib.sha256(p.read_bytes()).hexdigest())
def quatrot(q):
    x,y,z,w=np.moveaxis(q,-1,0)
    return np.stack((1-2*(y*y+z*z),2*(x*y-z*w),2*(x*z+y*w),2*(x*y+z*w),1-2*(x*x+z*z),2*(y*z-x*w),2*(x*z-y*w),2*(y*z+x*w),1-2*(x*x+y*y)),-1).reshape(q.shape[:-1]+(3,3))
def euler(rot):
    return np.stack((np.arctan2(rot[...,2,1],rot[...,2,2]),np.arcsin(np.clip(-rot[...,2,0],-1,1)),np.arctan2(rot[...,1,0],rot[...,0,0])),-1)
def first(mask,dt=.02):
    a=np.flatnonzero(mask);return float((a[0]+1)*dt)if len(a)else None
def corr(x,y):
    return float(np.corrcoef(x,y)[0,1])if min(np.std(x),np.std(y))>1e-9 else None
def savefig(fig,name):
    p=N/name;fig.savefig(p,dpi=150,bbox_inches='tight');plt.close(fig);return ident(p)

full=read(E/'reports/ROOT446_EVALUATION_FULL_RETURNED.json');assert full['result']['strict_successes']==0
embedded={Path(row['path']).name:row for row in full['full_UTF8']}
get=lambda name:json.loads(embedded[name]['UTF8'])
memory=get('ACTUAL446_NAMED_ACTUATOR_AND_RESET_PARAMETER_MEMORY.json')
trace=get('ACTUAL446_NAMED_ACTUATOR_INPUT_EFFORT_TRACE.json')
manifold=get('ACTUAL446_CONTACT_MANIFOLD_LATCHED_LANDING_TRACE.json')
receipt=read(C/'reports/ROOT451_ACTUAL446_SELECTED_REPLAY_TRANSFERS.json')
assert receipt['model_SHA']==full['result']['model_SHA']
with np.load(S/'reference389.npz',allow_pickle=False)as z:ref={k:z[k].copy()for k in z.files}
commands=np.asarray(read(S/'feedforward389.json')['commands'])
motor_names=['left_hip','left_crank','left_wheel_spin','right_hip','right_crank','right_wheel_spin']
policy_names=memory['policy_order'];effort_names=memory['applied_effort_order']
leg_names=['left_crank','left_hip','right_crank','right_hip']
leg_motor=[motor_names.index(n)for n in leg_names];ref_leg=[ref['joint_names'].tolist().index(n)for n in leg_names]
contract=read(T/'MODEL2050_LITERAL_JUMP_400N50_ADAPT_V240_20261101/package/payload/job0/assets/import_contract.json')
hips=np.asarray([contract['joints'][side+'_hip']['local_pos0']for side in('left','right')])
weights=dict(position=1.,rotation=.5,velocity=.5,omega=.1,joint_pose=1.,joint_velocity=.1,wheel_leg_length=.5,wheel_leg_angle=.5,support=.2,action_rate=1.,overflow=1.)
colors=['#2364aa','#b43c39','#279063','#8c55a5']
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'axes.grid':True,'grid.alpha':.22})
fig_route,ar=plt.subplots(2,2,figsize=(14,10));fig_motion,am=plt.subplots(3,2,figsize=(14,11))
fig_commands,ac=plt.subplots(3,2,figsize=(15,11));fig_reward,aw=plt.subplots(2,2,figsize=(14,10))
datasets={};cases=[];artifacts=[]
mfrows=manifold['rows'];mft=np.arange(1,len(mfrows)+1)*.0025
for color,row in zip(colors,receipt['cases']):
    raw=Path(row['local_path']).read_bytes();assert hashlib.sha256(raw).hexdigest()==row['SHA']
    with np.load(io.BytesIO(raw),allow_pickle=False)as z:p={k:z[k].copy()for k in z.files}
    n=row['controls'];tt=np.arange(1,n+1)*.02;phase=np.minimum(np.arange(n),249)
    rv=ref['state78'][phase].copy();rv[:,:3]+=[.8,0,0];rv[np.arange(n)>249,12:18]=0;rv[np.arange(n)>249,48:78]=0
    rR=rv[:,3:12].reshape(-1,3,3);rp=rv[:,:3];rrpy=euler(rR)
    root=p['root13'];pos=root[:,:3]-row['origin'];rot=quatrot(root[:,3:7]);rpy=euler(rot)
    bodies=p['body_position_w']-np.asarray(row['origin']);wheelids=[row['body_names'].index(side+'_wheel')for side in('left','right')]
    wheel=bodies[:,wheelids];wheelref=ref['wheel_world'][phase]+[.8,0,0]
    vb=np.einsum('nji,nkj->nki',rot,wheel-pos[:,None])-hips
    vr=np.einsum('nji,nkj->nki',rR,wheelref-rp[:,None])-hips
    lens=lambda x:np.sqrt(x[...,0]**2+x[...,2]**2)
    angle=lambda x:np.arctan2(-x[...,2],x[...,0])-np.pi/2
    base=commands[phase][:,[1,0,4,3,2,5]]/np.asarray([.5,.5,.5,.5,10,10]);base[np.arange(n)>249,4:]=0
    residual=p['action6']-np.clip(base,-6,6)
    costterms=dict(position=np.mean(((pos-rp)/.2)**2,-1),rotation=np.mean((rot-rR)**2,(-1,-2)),
        velocity=np.mean((root[:,7:10]-rv[:,12:15])**2,-1),omega=np.mean(((root[:,10:13]-rv[:,15:18])/3)**2,-1),
        joint_pose=np.mean(((p['motor_q'][:,leg_motor]-rv[:,18:48][:,ref_leg])/.5)**2,-1),
        joint_velocity=np.mean(((p['motor_dq'][:,leg_motor]-rv[:,48:78][:,ref_leg])/5)**2,-1),
        wheel_leg_length=np.mean(((lens(vb)-lens(vr))/.1)**2,-1),wheel_leg_angle=np.mean(((angle(vb)-angle(vr))/.5)**2,-1))
    support=1/(1+np.exp(-np.clip((p['wheel_contact_xyz'][:,:,2]/400-.025)*20,-80,80)))
    costterms['support']=((support.sum(-1)-ref['support'][phase].sum(-1))/2)**2
    prev=np.vstack((np.zeros((1,6)),p['action6'][:-1]));costterms['action_rate']=.001*np.mean((p['action6']-prev)**2,-1)
    costterms['overflow']=.001*np.mean(np.maximum(np.abs(p['action6'])-6,0)**2,-1)
    cost=sum(weights[k]*v for k,v in costterms.items());reward=np.exp(-cost/5)
    result=full['result']['results'][row['env']]
    deltas={k:float(np.mean(v)-result['tracking_components'][k])for k,v in costterms.items()}
    assert max(abs(v)for v in deltas.values())<1e-3,(row['env'],deltas)
    assert abs(np.mean(cost)-result['tracking_cost_mean'])<1e-3
    ground=np.asarray([r['ground_force_N'][row['env']]for r in mfrows]);top=np.asarray([r['top_force_N'][row['env']]for r in mfrows]);fid=np.asarray([r['current_flight_id'][row['env']]for r in mfrows])
    # Sagittal circle lower bound is a clearance diagnostic only, never solver support.
    wheelbottom=wheel[:,:,2]-.0637
    forward=(wheel[:,:,0]-.8).max(-1)
    wheelgap=np.max(wheelbottom-.27,axis=-1)
    yawrate=root[:,12];reqdiff=p['motor_vel_target'][:,5]-p['motor_vel_target'][:,2];actdiff=p['motor_dq'][:,5]-p['motor_dq'][:,2]
    metric=dict(env=row['env'],controls=n,seconds=row['seconds'],first_yaw_abs_gt_02_s=first(np.abs(rpy[:,2])>.2),first_pitch_abs_gt_02_s=first(np.abs(rpy[:,1])>.2),
        first_y_abs_gt_005_s=first(np.abs(pos[:,1])>.05),root_height_max=float(pos[:,2].max()),root_height_max_time=float(tt[pos[:,2].argmax()]),
        wheel_center_height_max2=wheel[:,:,2].max(0).tolist(),wheel_bottom_height_max2=wheelbottom.max(0).tolist(),
        first_flight_time_s=first(fid>0,.0025),top_force_peak_N=top.max(0).tolist(),first_solver_vertical_front_contact_s=None,
        first20_residual_mean6=residual[:20].mean(0).tolist(),first20_wheel_correction_rad_s=(residual[:20,4:].mean(0)*10).tolist(),
        first20_motor_target_wheel_rad_s_mean=p['motor_vel_target'][:20][:,[2,5]].mean(0).tolist(),
        first20_motor_actual_wheel_rad_s_mean=p['motor_dq'][:20][:,[2,5]].mean(0).tolist(),
        first20_wheel_target_difference_right_minus_left=float(reqdiff[:20].mean()),first20_actual_speed_difference_right_minus_left=float(actdiff[:20].mean()),
        early_yaw_rate_speed_difference_correlation=corr(actdiff[:30],yawrate[:30]),
        nearbound_counts6=(np.abs(residual)>.95).sum(0).tolist(),component_mean_reconstruction_error=deltas,
        mean_reward=float(reward.mean()),return_gamma99=float(np.sum(reward*.99**np.arange(n))),samples=[])
    for sample in manifold['selected_solver_contact_points']:
        found=False
        for contact in sample['contacts']:
            if contact['env']!=row['env']:continue
            pts=np.asarray(contact['position_relative']);normals=np.asarray(contact['normal_w'])
            if np.any((np.abs(pts[:,0]-.8)<.025)&(pts[:,2]>.02)&(pts[:,2]<.267)&(np.abs(normals[:,0])>.8)):
                metric['first_solver_vertical_front_contact_s']=sample['tick']*.0025;found=True;break
        if found:break
    for targettime in(.02,.1,.2,.4,.6,.8,1.,1.2,1.5,2.,4.,8.):
        j=min(n-1,round(targettime/.02)-1)
        metric['samples'].append(dict(seconds=float(tt[j]),position=pos[j].tolist(),reference_position=rp[j].tolist(),rpy_rad=rpy[j].tolist(),reference_rpy_rad=rrpy[j].tolist(),
            wheel_center_positions=wheel[j].tolist(),wheel_base_minus_top_m=(wheelbottom[j]-.27).tolist(),reference_wheel_center_positions=wheelref[j].tolist(),
            wheel_velocity_target=p['motor_vel_target'][j,[2,5]].tolist(),wheel_velocity_actual=p['motor_dq'][j,[2,5]].tolist(),
            weighted_costs={k:float(v[j]*weights[k])for k,v in costterms.items()},cost=float(cost[j]),reward=float(reward[j])))
    cases.append(metric)
    datasets[row['env']]=dict(p=p,row=row,t=tt,pos=pos,rot=rot,rpy=rpy,rp=rp,rrpy=rrpy,ref=rv,residual=residual,base=base,cost=cost,reward=reward,terms=costterms,wheel=wheel,wheelref=wheelref,ground=ground,top=top)
    label=f"env{row['env']}"
    ar[0,0].plot(pos[:,0],pos[:,1],c=color,label=label);ar[0,0].scatter(pos[::25,0],pos[::25,1],c=color,s=9)
    ar[0,1].plot(pos[:,0],pos[:,2],c=color,label=label)
    ar[1,0].plot(tt,pos[:,0]-rp[:,0],c=color,label=label);ar[1,1].plot(tt,pos[:,1]-rp[:,1],c=color,label=label)
    am[0,0].plot(tt,pos[:,2],c=color,label=label);am[0,1].plot(tt,np.rad2deg(rpy[:,1]),c=color,label=label)
    am[1,0].plot(tt,np.rad2deg(rpy[:,2]),c=color,label=label);am[1,1].plot(tt,root[:,7],c=color,label=label)
    am[2,0].plot(tt,wheelbottom.min(-1),c=color,label=label);am[2,1].plot(tt,root[:,8],c=color,label=label)
    aw[0,0].plot(tt,reward,c=color,label=label);aw[0,1].plot(tt,costterms['position'],c=color,label=label)
    aw[1,0].plot(tt,np.cumsum(reward*.99**np.arange(n)),c=color,label=label)
    if row['env']==0:
        for k,v in costterms.items():
            if k in('position','joint_pose','rotation','wheel_leg_length','velocity','support'):
                aw[1,1].plot(tt,v*weights[k],label=k)
        for side,j,col in(('L',2,'#2364aa'),('R',5,'#b43c39')):
            ac[0,0].plot(tt,p['motor_vel_target'][:,j],c=col,label=side+' requested')
            ac[0,0].plot(tt,p['motor_dq'][:,j],c=col,ls=':',label=side+' measured')
            ac[0,1].plot(tt,residual[:,4 if side=='L' else 5]*10,c=col,label=side+' RL correction')
            ac[0,1].plot(tt,commands[phase,j],c=col,ls='--',label=side+' saved feedforward')
        for j,lab in((0,'hip L'),(3,'hip R'),(1,'crank L'),(4,'crank R')):
            ac[1,0].plot(tt,p['motor_pos_target'][:,j],label=lab+' target')
            ac[1,0].plot(tt,p['motor_q'][:,j],ls=':',alpha=.7)
        ar[0,0].plot(rp[:,0],rp[:,1],'k--',lw=2,label='planned reference');ar[0,1].plot(rp[:,0],rp[:,2],'k--',lw=2,label='planned reference')
        am[0,0].plot(tt,rp[:,2],'k--',lw=2,label='reference');am[0,1].plot(tt,np.rad2deg(rrpy[:,1]),'k--',label='reference')
        am[1,0].plot(tt,np.rad2deg(rrpy[:,2]),'k--',label='reference');am[1,1].plot(tt,rv[:,12],'k--',label='reference');am[2,0].plot(tt,wheelref[:,:,2].min(-1)-.0637,'k--',label='reference');am[2,1].plot(tt,rv[:,13],'k--',label='reference')
    csvpath=N/f'env{row["env"]}_aligned_control_curves.csv'
    columns={'time_s':tt,'root_x':pos[:,0],'root_y':pos[:,1],'root_z':pos[:,2],'ref_x':rp[:,0],'ref_y':rp[:,1],'ref_z':rp[:,2],
        'roll_rad':rpy[:,0],'pitch_rad':rpy[:,1],'yaw_rad':rpy[:,2],'vx':root[:,7],'vy':root[:,8],'vz':root[:,9],
        'wheel_L_requested_rad_s':p['motor_vel_target'][:,2],'wheel_R_requested_rad_s':p['motor_vel_target'][:,5],
        'wheel_L_measured_rad_s':p['motor_dq'][:,2],'wheel_R_measured_rad_s':p['motor_dq'][:,5],'tracking_cost':cost,'tracking_reward':reward}
    columns.update({f'residual_{name}':residual[:,i]for i,name in enumerate(policy_names)})
    columns.update({f'cost_{k}':v for k,v in costterms.items()})
    with csvpath.open('x',newline='',encoding='utf8')as f:
        writer=csv.writer(f);writer.writerow(columns);writer.writerows(zip(*columns.values()))
    artifacts.append(ident(csvpath))

# Actual actuator trace is explicitly named, before compute and after original compute.
actstats={}
for group,ax,targetax in(('wheels',ac[1,1],ac[2,0]),('legs',ac[2,1],None)):
    rows=[r for r in trace['rows']if r['group']==group];names=rows[0]['joint_names'];ticks=np.asarray([r['tick']for r in rows]);timeaxis=ticks*.0025
    comp=np.asarray([r['computed_effort'][0]for r in rows]);applied=np.asarray([r['applied_effort'][0]for r in rows]);dq=np.asarray([r['dq'][0]for r in rows]);target=np.asarray([r['velocity_target'][0]for r in rows])
    for j,name in enumerate(names):
        ax.plot(timeaxis,applied[:,j],label=name+' applied',lw=1)
        if group=='wheels':
            ax.plot(timeaxis,comp[:,j],ls=':',alpha=.65,label=name+' computed')
            targetax.plot(timeaxis,target[:,j],label=name+' heldtarget');targetax.plot(timeaxis,dq[:,j],ls=':',label=name+' speed')
    actstats[group]=dict(names=names,seconds=float(timeaxis[-1]),computed_abs_peak=np.abs(comp).max(0).tolist(),applied_abs_peak=np.abs(applied).max(0).tolist(),
        computed_applied_difference_fraction_gt01=(np.abs(comp-applied)>.1).mean(0).tolist(),early04_applied_signed_mean=applied[timeaxis<=.4].mean(0).tolist(),
        warning='computed/applied mismatch combines original DC limit, episode scaling and physical lag; not all mismatches prove torque clipping')
    path=N/f'env0_{group}_400Hz_actuator_trace.csv'
    with path.open('x',newline='',encoding='utf8')as f:
        writer=csv.writer(f);writer.writerow(['time_s']+[n+'_'+kind for kind in('computed_Nm','applied_Nm','dq_rad_s','velocity_target_rad_s')for n in names]);writer.writerows(np.column_stack((timeaxis,comp,applied,dq,target)))
    artifacts.append(ident(path))

ar[0,0].axvline(.8,c='#008ac3',lw=2,label='platform front x=.8');ar[0,0].axhspan(-1,1,xmin=.62,alpha=.03)
ar[0,0].set(xlabel='forward x (m)',ylabel='lateral y (m)',title='Actual route bends before takeoff; dots every .5s');ar[0,0].axis('equal')
ar[0,1].axvline(.8,c='#008ac3');ar[0,1].set(xlabel='forward x (m)',ylabel='root height z (m)',title='Root path; not wheel-clearance evidence')
ar[1,0].set(xlabel='time (s)',ylabel='x-reference (m)',title='Forward tracking deficit');ar[1,1].set(xlabel='time (s)',ylabel='y-reference (m)',title='Lateral tracking error')
for ax in ar.flat:ax.legend(fontsize=8)
fig_route.suptitle('Final RL445 / actual independent446 | 0/80 success; 4 recorded cases',fontsize=16)
artifacts.append(savefig(fig_route,'01_actual_route_vs_planned_reference.png'))
titles=[('Root height','z (m)'),('Pitch','degrees'),('Yaw','degrees'),('Forward velocity','m/s'),('Lowest wheel bottom estimate','m'),('Lateral velocity','m/s')]
for ax,(title,ylabel)in zip(am.flat,titles):ax.set(title=title,xlabel='time (s)',ylabel=ylabel,xlim=(0,1.6));ax.legend(fontsize=8)
am[2,0].axhline(.27,c='#008ac3',label='platform top');am[1,0].axhline(0,c='grey',lw=.5)
fig_motion.suptitle('First1.6s: yaw/pitch deviation precedes lift; wheel clearance matters',fontsize=16)
artifacts.append(savefig(fig_motion,'02_takeoff_attitude_velocity_clearance.png'))
ctitles=[('Wheel speeds: requested vs measured','rad/s'),('Saved feedforward and learned wheel correction','rad/s'),('Leg position targets vs measured (dotted)','rad'),('Original wheel efforts, computed vs applied','Nm'),('400Hz held wheel targets and measured speeds','rad/s'),('Original leg efforts applied','Nm')]
for ax,(title,ylabel)in zip(ac.flat,ctitles):ax.set(title=title,xlabel='time (s)',ylabel=ylabel,xlim=(0,1.6));ax.legend(fontsize=7,ncol=2)
fig_commands.suptitle('Env0: actions cause a differential wheel request before takeoff',fontsize=16)
artifacts.append(savefig(fig_commands,'03_motor_targets_speeds_and_actual_efforts.png'))
for ax,title in zip(aw.flat,('Actual reconstructed training reward','Position cost grows despite survival','Discounted accumulated reward gamma=.99','Env0 weighted cost terms')):ax.set(title=title,xlabel='time (s)');ax.legend(fontsize=8)
fig_reward.suptitle('Reward reconstructed from saved measurements; component means match evaluation',fontsize=16)
artifacts.append(savefig(fig_reward,'04_reward_and_tracking_cost_components.png'))

fig,axs=plt.subplots(2,2,figsize=(14,9))
for color,row in zip(colors,receipt['cases']):
    data=datasets[row['env']];tt=data['t'];ground=data['ground'];top=data['top'];label=f'env{row["env"]}'
    axs[0,0].plot(mft,ground.sum(-1),c=color,label=label);axs[0,1].plot(mft,top.sum(-1),c=color,label=label)
    axs[1,0].plot(tt,data['wheel'][:,:,0].max(-1),c=color,label=label)
    axs[1,1].plot(tt,data['wheel'][:,:,2].min(-1)-.0637,c=color,label=label)
axs[0,0].set(title='Actual solver ground forces',ylabel='N',xlim=(0,2.));axs[0,1].set(title='Actual solver platform-top forces: all zero',ylabel='N',xlim=(0,2.))
axs[1,0].axhline(.8,c='k',ls='--');axs[1,0].set(title='Most forward wheel center; edge=.8m',ylabel='x (m)',xlim=(0,2.))
axs[1,1].axhline(.27,c='k',ls='--');axs[1,1].set(title='Lowest of two wheel bottom estimates',ylabel='z (m)',xlim=(0,2.))
for ax in axs.flat:ax.set_xlabel('time (s)');ax.legend(fontsize=8)
fig.suptitle('400Hz solver contacts and recorded wheel geometry; no top landing',fontsize=16)
artifacts.append(savefig(fig,'05_solver_contacts_and_wheel_approach.png'))

# Transparent all80 result aggregate; route details exist only for four recovered cases.
allresults=full['result']['results'];whole=sum(r['first_flight_whole_footprint_clear']for r in allresults);top=max(r['top_contact_longest_seconds']for r in allresults)
source_identity={name:dict(path=embedded[name]['path'],bytes=embedded[name]['bytes'],SHA=embedded[name]['SHA'])for name in ('ACTUAL446_NAMED_ACTUATOR_INPUT_EFFORT_TRACE.json','ACTUAL446_CONTACT_MANIFOLD_LATCHED_LANDING_TRACE.json','ACTUAL446_NAMED_ACTUATOR_AND_RESET_PARAMETER_MEMORY.json','RESULT446.json')}
report=dict(epoch=time.time(),passed=True,scope='offline recorded actual446 video/curve diagnosis requested by human',model_SHA=receipt['model_SHA'],
    actual_all80=dict(strict_successes=0,whole_footprint_clear=whole,top_contact_longest_seconds=top,orientation=22,full8s=58,mean_lifetime=6.15125),
    detailed_cases=cases,named_actuator_analysis=actstats,cost_weights=weights,
    cost_reconstruction='Full measured reward formula reconstructed from root13, motor q/dq, bodyposes/contract hip anchors and saved world wheel net forces; all per-term means verified against original evaluation to1e-3',
    time_alignment='Replay frame i is endpoint of control i+1 at(i+1)*.02; reference label phase i, planned times=.02..5s. Actual actuator precompute tick t is t*.0025. No interpolation of contact manifold.',
    wheel_clearance_scope='Wheel center minus .0637 is a geometric diagnostic, not exact rolled authored footprint or solver-contact support; no success inferred from it.',
    causal_status=dict(measured='Strong early asymmetric requested and measured wheel speeds precede yaw/lateral deviation. Wheel centers never clear platform height in the selected trajectories; no actual platform top manifold in all80.',
        architecture='No explicit route planner: actor conditioned on current proprio/depth and planned reference maps to6 motor targets at50Hz; learned residual modifies saved feedforward.',
        reward='All reward terms nonnegative cost, exp(-cost/5)>0; no explicit wholewheel/topmanifold success term. Wrong route is penalized by position cost, not rewarded as correct route. Long unsuccessful survival still earns positive return.',
        hypothesis='Short32-control(.64s) GAE.95 and inherited saturated asymmetric policy can support a local survival/bracing attractor. No saved training-Q/advantage evidence here proves this is the unique cause.',
        next='Use completed455 final independent456 results and aligned curves before another algorithm/reward/physics change; preserve current455 save/exit and sole456. No blind hour or onlineMPC experiment.'),
    source_embedded=source_identity,source_replay_receipt=str(C/'reports/ROOT451_ACTUAL446_SELECTED_REPLAY_TRANSFERS.json'),
    artifacts=artifacts,model_reads=0,NN_inference=0,SDK=0,physics_steps=0,network=0)
put(R/'ANALYSIS457_ACTUAL446_ROUTE_ACTION_CONTACT_REWARD.json',report)
print(json.dumps(dict(passed=True,cases=[{k:r[k]for k in('env','first_yaw_abs_gt_02_s','root_height_max','wheel_center_height_max2','first_solver_vertical_front_contact_s','first20_wheel_correction_rad_s','return_gamma99')}for r in cases],actstats=actstats,artifacts=len(artifacts)),indent=2),flush=True)
