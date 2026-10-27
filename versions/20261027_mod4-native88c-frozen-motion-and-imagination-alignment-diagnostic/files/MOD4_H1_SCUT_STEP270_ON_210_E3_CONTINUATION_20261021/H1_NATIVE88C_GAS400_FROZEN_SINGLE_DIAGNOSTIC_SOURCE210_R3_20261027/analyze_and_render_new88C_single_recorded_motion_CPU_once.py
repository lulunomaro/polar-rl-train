"""One read of this NEW recorded case. No model/actor/WM/SDK/physics."""
from pathlib import Path
import json,hashlib,time,traceback,importlib.util,math
import numpy as np
S=Path(__file__).resolve().parent;R=S/'reports';T=S.parent
def put(n,x):
 with (R/n).open('x',encoding='utf8') as f:json.dump(x,f,indent=2,allow_nan=False)
def artifact(p):return dict(path=str(p),bytes=p.stat().st_size,SHA=hashlib.sha256(p.read_bytes()).hexdigest())
def main():
 put('NEW88C_SINGLE_MOTION_CPU_ANALYSIS_CONSUMED_BEFORE_RAW_READ_ACTUAL.json',dict(epoch=time.time(),scope='one new current400N qualified native88C fixed single case',no_old_raw_or_model_or_GPU_or_forward=True))
 receipt=json.loads((R/'FROZEN_NATIVE88C_SOURCE210_SINGLE_FINITE_RETURNED_ACTUAL.json').read_bytes());assert receipt['actual_finite_transport_returned'] and receipt['all_own_children_actual_out'] and receipt['parent_original_error'] is None and receipt['canonical_bytes_unchanged']
 root=S/'actual210/seed_20260928';status=json.loads((root/'episode/FROZEN_SINGLE_CASE_STATUS_ACTUAL.json').read_bytes());assert status['seed']==20260928 and status['policy_parameters_and_saved_normalizers_literal_unchanged']
 files={r['relative']:r for r in receipt['local_files']}
 records=[];controls=[]
 for name,container in [('ACTUAL_400HZ_31BODY_FRAMES.jsonl',records),('ACTUAL_100HZ_CONTROLS.jsonl',controls)]:
  p=root/'episode'/name;row=files['seed_20260928/episode/'+name];assert p.stat().st_size==row['bytes']
  with p.open('r',encoding='utf8') as stream:
   for line in stream:
    if line.strip():container.append(json.loads(line))
 assert len(records)==status['physics_callbacks']+1 and len(controls)==status['controls']
 assert [x['physics_callback'] for x in records]==list(range(len(records)))
 arrays={}
 def a(name,values):arrays[name]=np.asarray(values,dtype=np.float32)
 a('time',[x['physics_callback']*.0025 for x in records])
 for key,name in [('root','root13_sdk_xyzw'),('body_position','body_position31_world'),('body_quaternion','body_quaternion31_sdk_xyzw'),('projected_gravity','projected_gravity_b'),('contact_force','body_contact_force31'),('contact_history','contact_history18'),('executed','executed6'),('physical_applied','physical_applied_processed6'),('q','q30'),('dq','qd30'),('torque','applied_torque30'),('age','public_age'),('request','public_request')]:a(key,[x['state'][name] for x in records])
 for key,name in [('wheel_min','step_wheel_min'),('wheel_max','step_wheel_max')]:a(key,[x['state']['actual_original_success_caches'].get(name,[[np.nan]*3]*2) for x in records])
 for key,name in [('packed127','packed127_for_action'),('terminal127','terminal_packed127_same_point'),('xi31','xi31_for_action'),('mean6','mean6'),('raw6','raw_native_clamp20_6')]:a(key,[x[name] for x in controls])
 objective_names=list(controls[0]['actual_ownwheel_V2_objective'])
 for name in objective_names:a('objective_'+name,[x['actual_ownwheel_V2_objective'][name] for x in controls])
 # Origin X/Z is recovered from the SAME recorded original cached wheel metrics.
 last=status['last_original_state'];minimum=np.asarray(last['actual_original_success_caches']['step_wheel_min']);maximum=np.asarray(last['actual_original_success_caches']['step_wheel_max']);metrics=last['metrics']
 origin_z=float(minimum[0,2]-metrics['wheel_bottom_above_floor_m'][0]);origin_x=float(metrics['wheel_front_edge_gap_m'][0]+maximum[0,0]-.35)
 origin=np.asarray([origin_x,0.,origin_z]);a('render_origin_x0z',origin)
 bottom=np.nanmin(arrays['wheel_min'][:,:,2]-origin_z,axis=1);gap=.35+origin_x-np.nanmin(arrays['wheel_max'][:,:,0],axis=1)
 tilt=np.arccos(np.clip(-arrays['projected_gravity'][:,2],-1,1));history=arrays['contact_history'].reshape(-1,3,2,3)
 npz=S/'NEW88C_SINGLE_RECORDED_DERIVED_SMALL.npz';assert not npz.exists();np.savez_compressed(npz,**arrays)
 summary=dict(epoch=time.time(),passed_actual_single_recording=True,source_SHA=receipt['source_SHA'],fixed_seed=20260928,physical_callbacks=status['physics_callbacks'],complete_controls=status['controls'],simulated_seconds=status['physics_callbacks']*.0025,original_termination_terms=status['last_termination_terms']['values'],original_events=dict(takeoff=last['takeoff_count'],landing=last['landing_count'],recovery=last['recovery_count'],crossed=last['crossed2'],success=last['success'],stable_ticks=last['stable_callback_ticks']),request_physics_frames=int(arrays['request'].sum()),final_public_age=last['public_age'],final_public_request=last['public_request'],max_both_wheel_bottom_m=float(np.nanmax(bottom)),nearest_both_front_gap_m=float(np.nanmin(gap)),final_tilt_rad=float(tilt[-1]),final_tilt_deg=float(np.degrees(tilt[-1])),peak_tilt_deg=float(np.degrees(tilt).max()),root_velocity_x_range=[float(arrays['root'][:,7].min()),float(arrays['root'][:,7].max())],raw6_clip_hit_fraction=float((np.abs(arrays['raw6'])>=6).mean()),mean6_minmax=[[float(arrays['mean6'][:,i].min()),float(arrays['mean6'][:,i].max())] for i in range(6)],contact_history_worldZ_range=[float(history[...,2].min()),float(history[...,2].max())],contact_history_norm_range=[float(np.linalg.norm(history,axis=-1).min()),float(np.linalg.norm(history,axis=-1).max())],actual_objective_term_last={k:controls[-1]['actual_ownwheel_V2_objective'][k] for k in objective_names},derived=artifact(npz),original_new_raw_existing_producer_index=[files['seed_20260928/episode/'+n] for n in ('ACTUAL_400HZ_31BODY_FRAMES.jsonl','ACTUAL_100HZ_CONTROLS.jsonl')],policy_and_normalizers_literal_unchanged=True,no_learning_or_account_write=True,not_whole_window_or_frozen_success_rate=True,no_unique_rootcause_claim=True)
 put('NEW88C_SINGLE_REAL_MOTION_AND_ORIGINAL_TERMINATION_CPU_ACTUAL.json',summary)
 # Reuse only pure original collider math from the old renderer; never its main/raw.
 old=T/'H1_STEP270_NATIVE86_FULL_SINGLE_ATTEMPT_REPLAY_20261027/render_actual_single_native_attempt_CPU_unused_once.py'
 sp=importlib.util.spec_from_file_location('old_collider_pure_math_only_for_NEW88C_motion',old);m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m)
 import matplotlib
 matplotlib.use('Agg')
 import matplotlib.pyplot as plt
 from matplotlib.patches import Polygon,Rectangle
 from PIL import Image
 geometry=json.loads((root/'ACTUAL_RENDER_GEOMETRY.json').read_bytes());shapes=[(x,m.local_points(x)) for x in geometry['shapes']]
 selected=list(range(4,len(records),4));assert selected[-1]==len(records)-1
 fig,ax=plt.subplots(figsize=(10,6),dpi=100);images=[]
 def draw(i):
  ax.clear();state=records[i]['state'];pos=np.asarray(state['body_position31_world'])-origin;quat=state['body_quaternion31_sdk_xyzw']
  ax.add_patch(Rectangle((-.45,-.06),1.85,.06,color='#e6e9ed'));ax.add_patch(Rectangle((.35,0),.8,.27,facecolor='#bbc7d1',edgecolor='#64748b'))
  world=[]
  for shape,points in shapes:
   j=shape['body_index'];v=points@m.rotation(quat[j]).T+pos[j];world.append((float(v[:,1].mean()),shape,v))
  for _,shape,v in sorted(world,reverse=True,key=lambda x:x[0]):
   points=m.hull(v[:,[0,2]]);body=shape['body'];col='#263c50' if 'wheel' in body else '#aebfd0' if body=='chassis' else '#da955a' if any(k in body for k in ('crank','rocker')) else '#738ca4'
   if len(points)>=3:ax.add_patch(Polygon(points,facecolor=col,edgecolor='#34495e',linewidth=.65))
  ax.set_xlim(-.38,1.25);ax.set_ylim(-.065,.82);ax.set_aspect('equal');ax.grid(alpha=.12);ax.set_xlabel('Forward X (m)');ax.set_ylabel('Height Z (m)')
  ax.set_title('MOD4 | qualified native88C / nominal 400N | one fixed frozen attempt\n'+f"actual t={i*.0025:.3f}s   age={state['public_age']}   request={state['public_request']}")
  ax.text(.015,.98,'270mm step | deterministic native mean\n'+f"tilt={np.degrees(tilt[i]):.1f} deg | cross / landing / stable = 0",transform=ax.transAxes,va='top',fontsize=10,bbox=dict(facecolor='white',alpha=.88,edgecolor='#cbd5e1'))
  fig.tight_layout();fig.canvas.draw();return Image.fromarray(np.asarray(fig.canvas.buffer_rgba())[...,:3].copy())
 draw(0).save(S/'NATIVE88C_SINGLE_START.png')
 for i in selected:images.append(draw(i))
 images[-1].save(S/'NATIVE88C_SINGLE_END.png');plt.close(fig)
 gif=S/'NATIVE88C_SINGLE_4X_SLOW.gif';images[0].save(gif,save_all=True,append_images=images[1:],duration=40,optimize=False)
 import imageio_ffmpeg,subprocess
 frames=S/'render_frames';frames.mkdir()
 for i,im in enumerate(images):im.save(frames/('frame_'+str(i).zfill(5)+'.png'))
 mp4=S/'NATIVE88C_SINGLE_1X.mp4';subprocess.run([imageio_ffmpeg.get_ffmpeg_exe(),'-framerate','100','-i',str(frames/'frame_%05d.png'),'-c:v','libx264','-movflags','+faststart','-pix_fmt','yuv420p',str(mp4)],check=True,capture_output=True)
 fig,axs=plt.subplots(3,1,figsize=(9,7),sharex=True)
 axs[0].plot(arrays['time'],bottom*1000);axs[0].axhline(270,c='r',ls='--');axs[0].set_ylabel('both bottom (mm)')
 axs[1].plot(arrays['time'],gap*1000);axs[1].axhline(0,c='r',ls='--');axs[1].set_ylabel('both-front gap (mm)')
 axs[2].plot(arrays['time'],np.degrees(tilt),label='actual tilt');axs[2].axhline(np.degrees(.75),c='r',ls='--',label='actual hard limit');axs[2].axhline(np.degrees(math.acos(.3)),c='orange',ls=':',label='current imagined tilt 50% boundary')
 axs[2].legend();axs[2].set_ylabel('tilt (deg)');axs[2].set_xlabel('actual recorded time (s)')
 for axis in axs:axis.grid(alpha=.2)
 fig.suptitle('One NEW400N frozen case | measured motion; source soft boundary is diagnostic only');fig.tight_layout();plot=S/'NATIVE88C_SINGLE_HEIGHT_GAP_TILT.png';fig.savefig(plot,dpi=140);plt.close(fig)
 artifacts=[artifact(p) for p in (mp4,gif,S/'NATIVE88C_SINGLE_START.png',S/'NATIVE88C_SINGLE_END.png',plot)]
 put('NEW88C_SINGLE_VIDEO_AND_PLOT_PRODUCER_ACTUAL.json',dict(passed=True,source_derived=summary['derived'],artifacts=artifacts,full_one_actual_case_no_case_selection=True,frames=len(images),video_fps=100,GIF_fps=25,actual_duration_seconds=.61,original_colliders_and_actual31body_poses=True,no_new_actor_physics_model_or_old_raw=True,not_photoreal_camera_or_exact_training_replay=True))
 print(json.dumps(dict(summary={k:summary[k] for k in ('complete_controls','simulated_seconds','original_termination_terms','max_both_wheel_bottom_m','nearest_both_front_gap_m','final_tilt_deg','actual_objective_term_last')},artifacts=artifacts)))
if __name__=='__main__':
 try:main()
 except BaseException:put('NEW88C_MOTION_ANALYSIS_OR_RENDER_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),no_raw_model_or_case_retry=True));raise
