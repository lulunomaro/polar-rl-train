"""Unused78 saved-only neutral visualization; case selection does not require a clearance success."""
from pathlib import Path
import hashlib,json,time,traceback
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from matplotlib.animation import FuncAnimation,PillowWriter
S=Path(__file__).resolve().parent;R=S/'reports'
def put(n,v):
 with (R/n).open('x',encoding='utf8') as f:json.dump(v,f,ensure_ascii=False,indent=2)
def artifact(p):return dict(path=str(p),bytes=p.stat().st_size,SHA=hashlib.sha256(p.read_bytes()).hexdigest())
try:
 source=json.loads((R/'CLOSED78_RECORDED_MOTION_SOURCE_CPU_ACTUAL.json').read_bytes());kin=json.loads((R/'RECORDED_USD_KINEMATICS_CPU_ACTUAL.json').read_bytes());terms=source['reward_terms'];cases={c['env_id']:c for c in kin['case_summaries']}
 with np.load(S/'SELECTED_RECORDED_MOTION.npz',allow_pickle=False) as z,np.load(S/'RECORDED_KINEMATIC_RECONSTRUCTION.npz',allow_pickle=False) as k:
  ids=z['env_ids'];pos=k['body_pose'][...,:3,3];lo=k['wheel_min'];hi=k['wheel_max'];bottom=lo[:,:,:,2].min(-1);front=hi[:,:,:,0].min(-1);root=z['root_local'];con=z['reward_term_contribution'];tuck=con[:,:,terms.index('h1_scut_fudan_leg_tuck')];same=z['same_episode_transition'];clean=z['continuous_no_reset'];rootdx=np.diff(root[:,:,0],axis=0);frontdx=np.diff(front,axis=0);paid=tuck[1:]>0
  conflict=same&paid&(rootdx>0)&(frontdx<0);qualified=[c for c in kin['case_summaries'] if not c['recorded_done_any'] and c['recorded_takeoff_count']>0 and c['clearance_ge270_rows']>0]
  diagnostic=[]
  for c in sorted(qualified,key=lambda c:c['min_gap_while_clear_m'])[:8]:
   e=c['column'];ap=c['apex_row'];near=int(np.argmin(.35-front[:,e]));diagnostic.append(dict(c,clearance_at_closest_front_m=float(bottom[near,e]),closest_front_frame=near,public_request_at_apex=bool(z['public_request'][ap,e]),body_forward_speed_at_apex_m_s=float(z['root13'][ap,e,7]),actual_tuck_paid_at_apex=float(tuck[ap,e]),root_forward_with_retracting_front_paid_transitions=int(conflict[:,e].sum())))
  candidates=[c for c in kin['case_summaries'] if not c['recorded_done_any']];assert len(candidates)>=3
  fast=max(candidates,key=lambda c:c['root_dx'])['env_id']
  ranked=sorted(candidates,key=lambda c:(0 if c in qualified else 1,c['min_gap_while_clear_m'] if c['min_gap_while_clear_m'] is not None else c['min_two_wheel_leading_edge_gap_to_step_m']))
  pair=[c['env_id'] for c in ranked[:2]];chosen=list(dict.fromkeys(pair+[fast]+[c['env_id'] for c in candidates]))[:3];frames=[0,5,15,25,35,47]
  def draw(ax,e,f,labels=False):
   ax.axhline(0,color='#444',lw=1);ax.add_patch(Rectangle((.35,0),.8,.27,color='#b6bcc6',alpha=.7));ax.scatter(pos[f,e,:,0],pos[f,e,:,2],s=7,color='#567287',alpha=.65)
   for chain in (('chassis','left_thigh','left_rocker','left_shin','left_distal','left_wheel'),('chassis','right_thigh','right_rocker','right_shin','right_distal','right_wheel')):
    p=np.array([pos[f,e,kin['body_names'].index(n)] for n in chain]);ax.plot(p[:,0],p[:,2],lw=1.5,color='#1769a1',alpha=.6)
   for w in range(2):ax.add_patch(Rectangle((lo[f,e,w,0],lo[f,e,w,2]),hi[f,e,w,0]-lo[f,e,w,0],hi[f,e,w,2]-lo[f,e,w,2],fill=False,lw=1.5,edgecolor='#d36532'))
   ax.axvline(.35,color='#777',ls=':',lw=.8);ax.set_xlim(-.2,.7);ax.set_ylim(-.03,1.0);ax.set_aspect('equal',adjustable='box');ax.grid(alpha=.12);ax.set_title(f'{f*10}ms | vx={z["root13"][f,e,7]:.2f}',fontsize=8)
   if labels:ax.set_ylabel(f'env {int(ids[e])}\nz (m)')
  fig,axs=plt.subplots(3,6,figsize=(15,8),constrained_layout=True)
  for row,env in enumerate(chosen):
   e=int(np.where(ids==env)[0][0])
   for col,f in enumerate(frames):draw(axs[row,col],e,f,col==0)
  fig.suptitle('Closed78 saved motion: clearance and forward position must coincide\nOrange: reconstructed wheel collider AABB | Gray: original270mm step',fontsize=12)
  fig.supxlabel('Recorded48 controls/0.48s. Root/q kinematics only; no policy inference or physical reintegration.\nSkeleton lines connect named mechanism points for illustration; they are not a new collision model.',fontsize=9)
  sheet=S/'CLOSED78_RECORDED_STEP_TIMING_CONTACT_SHEET.png';assert not sheet.exists();fig.savefig(sheet,dpi=140);plt.close(fig)
  fig,axs=plt.subplots(4,2,figsize=(12,10),sharex=True,constrained_layout=True);ts=np.arange(48)*.01
  for col,env in enumerate(pair):
   e=int(np.where(ids==env)[0][0]);axs[0,col].plot(ts,bottom[:,e]*1000,label='lower wheel bottom');axs[0,col].axhline(270,color='#c65b32',ls='--',label='step270mm');axs[0,col].set_title(f'env {env}');axs[0,col].set_ylabel('height (mm)');axs[0,col].legend(fontsize=8)
   axs[1,col].plot(ts,(.35-front[:,e])*1000);axs[1,col].axhline(0,color='#c65b32',ls='--');axs[1,col].set_ylabel('front-to-edge gap (mm)')
   axs[2,col].plot(ts,z['root13'][:,e,7],label='recorded world vx');axs[2,col].plot(ts,z['public_request'][:,e]*.8,ls=':',label='public command');axs[2,col].set_ylabel('m/s');axs[2,col].legend(fontsize=8)
   for term in (x for x in ('h1_step270_path_progress','h1_scut_fudan_leg_tuck','h1_step270_airborne_leg_target_overdrive','h1_step270_release_shortfall') if x in terms):axs[3,col].plot(ts,con[:,e,terms.index(term)],label=term.replace('h1_step270_','').replace('h1_scut_fudan_',''))
   axs[3,col].set_ylabel('actual control reward');axs[3,col].legend(fontsize=7);axs[3,col].set_xlabel('recorded clip time (s)')
   for ax in axs[:,col]:ax.grid(alpha=.2)
  fig.suptitle('Closed78 recorded wheel clearance, edge gap, velocity and reward',fontsize=13);timeline=S/'CLOSED78_RECORDED_CLEARANCE_FORWARD_REWARD_TIMELINE.png';assert not timeline.exists();fig.savefig(timeline,dpi=140);plt.close(fig)
  fig,axes=plt.subplots(1,2,figsize=(9,5),constrained_layout=True);cols=[int(np.where(ids==env)[0][0]) for env in pair]
  def animate(f):
   for ax,e in zip(axes,cols):ax.clear();draw(ax,e,f,True)
   fig.suptitle(f'Closed78 recorded kinematics | {f*.01:.2f}s | shown4x slower | no physics replay',fontsize=11)
  ani=FuncAnimation(fig,animate,frames=48,interval=40,repeat=True);gif=S/'CLOSED78_TWO_RECORDED_CASES_4X_SLOW.gif';assert not gif.exists();ani.save(gif,writer=PillowWriter(fps=25));plt.close(fig)
  report=dict(epoch=time.time(),passed_descriptive_analysis=True,scope=source['scope'],recorded_event_increments=source['recorded_event_counter_positive_increments'],all20k_last48_recorded_both_wheel_crossed_envframes=source['recorded_both_wheels_crossed_envframes'],selected_continuous_qualified_launch_clearance_cases=diagnostic,selected_all_paid_tuck_forward_body_backward_front_transitions=int(conflict.sum()),selected_paid_tuck_same_episode_transitions=int((same&paid).sum()),diagnostic_interpretation='Only new76 selected saved samples. Inspect actual apex gap and closest-edge clearance together; recorded crossed/success events remain the source of event truth. No counterfactual, matched-cohort learning-gain or whole-window inference.',not_FINAL_policy_evaluation_or_graduation=True,geometry_reconstruction_not_fresh_callback_truth=True,artifacts=[artifact(sheet),artifact(timeline),artifact(gif)],no_policy_PhysX_GPU_or_training_write=True)
  put('CLOSED78_STEP_TIMING_AND_REWARD_ALIGNMENT_DESCRIPTIVE_ACTUAL.json',report)
  print(json.dumps(dict(qualified_cases=diagnostic[:3],paid_tuck_forward_body_backward_front=int(conflict.sum()),paid_tuck_transitions=int((same&paid).sum()),artifacts=report['artifacts'])))
except BaseException:
 put('CLOSED78_RENDER_ANALYSIS_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),no_same_once_retry=True));raise
