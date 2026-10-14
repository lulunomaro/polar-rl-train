"""Actual residual yaw time history and action-domain supplement, CPU only."""
import os
os.environ['CUDA_VISIBLE_DEVICES']=''
from pathlib import Path
import json,time,hashlib,numpy as np
D=Path(__file__).resolve().parent;R=D/'reports'
I=R/'PAIRED_FULL80_RESIDUAL_ACTUAL_CPU_DIAGNOSIS.json'
P=R/'RESIDUAL_YAW_PHASE_AND_JOINT_DOMAIN_CPU_SUPPLEMENT.json';assert not P.exists()
j=json.loads(I.read_bytes());W=D.parent
def sha(p):
 h=hashlib.sha256()
 with Path(p).open('rb') as f:
  for b in iter(lambda:f.read(2**20),b''):h.update(b)
 return h.hexdigest()
def yaw(q):
 x,y,z,w=np.moveaxis(q,-1,0)
 return np.unwrap(np.arctan2(2*(w*z+x*y),1-2*(y*y+z*z)))
def q(a):return dict(min=float(np.min(a)),mean=float(np.mean(a)),median=float(np.median(a)),max=float(np.max(a)))
extra={}
for label,name,index in [('old','MOD4_3060_FULL80_FROZEN_CURRENT_20261014',j['raw_original_index']),('new','MOD4_3060_LEFT_REPAIR_FULL80_20261014',j['raw_new_index'])]:
 assert sha(index['local_path'])==index['sha256']
 review=json.loads((W/name/'reports/FULL80_ORIGINAL_1N_ROUTE_ALL_PREFIX_COMPLETE_ACTUAL_REVIEW.json').read_bytes())
 report=json.loads(Path(review['original_report']['local_path']).read_bytes())
 with np.load(index['local_path']) as z:
  a=z['action'];pr=z['processed_action'];gt=z['guarded_leg_targets'];be=z['before_root'];ro=z['root'];pos=z['COM_link_pos'];v=z['physical_hardware_cached_pre_actuator_velocity'];t=z['physical_hardware_actual_applied_effort'];groups=z['group_ids'];forc=z['physical_wheel_force_N']
 assert np.array_equal(np.clip(a,-6,6),pr)
 moving=np.flatnonzero(groups!=2);pd=.5*(pr[:,:,0]-pr[:,:,1]);actualdiff=gt[:,:,0]-gt[:,:,1]
 per=[]
 half=report['route_scope']['wave_x_halfspan_m'];centers=np.asarray(report['route_scope']['tile_centers']);wheels=[report['body_names'].index(n) for n in ['left_wheel','right_wheel']]
 loads=np.maximum(forc.reshape(1500,4,80,2,3)[...,2],0).sum(1)*np.float32(.0025)/np.float32(.01)
 for i in j['failed_new']:
  sign=1 if int(groups[i])==0 else -1
  x=(pos[:,i][:,wheels,0]-centers[i,0])*sign
  yy=yaw(be[:,i,3:7]);yy_after=yaw(ro[:,i,3:7]);omega=ro[:,i,12]
  ent=np.flatnonzero(x.max(1)>=-half);entry=int(ent[0]) if len(ent) else None
  full=np.flatnonzero(x.min(1)>half);firstfull=int(full[0]) if len(full) else None
  params=report['initial']['actual_all_physical_parameters']
  assignments=report['initial']['assignments']
  bins=[]
  for st,en in [(0,300),(300,600),(600,900),(900,1200),(1200,1500)]:
   bins.append(dict(seconds=[st*.01,en*.01],yaw_change_deg=float(np.rad2deg(yy_after[en-1]-yy[st])),actual_world_omega_z_mean_rad_s=float(omega[st:en].mean()),actual_world_omega_z_median_rad_s=float(np.median(omega[st:en])),actual_world_omega_z_sign_fraction_positive=float((omega[st:en]>0).mean()),requested_raw_wheel_left_right_mean=a[st:en,i,4:].mean(0).tolist(),cached_pre_actuator_wheel_angular_velocity_mean_rad_s=v[st*4:en*4,i,4:].mean(0).tolist(),actual_applied_wheel_effort_mean_Nm=t[st*4:en*4,i,4:].mean(0).tolist(),double_1N_fraction=float((loads[st:en,i].min(1)>1).mean())))
  per.append(dict(env=i,group=int(groups[i]),first_leading_wheel_enter_actual_wave_control=entry,yaw_at_first_leading_wheel_wave_entry_deg=float(np.rad2deg(yy_after[entry])) if entry is not None else None,first_both_wheel_COM_beyond_wave_end_control=firstfull,last_minwheel_beyond_wave_end_margin_m=float(x[-1].min()-half),max_minwheel_beyond_wave_end_margin_m=float(x.min(1).max()-half),actual_yaw_final_deg=float(np.rad2deg(yy_after[-1])),world_omega_z_1500_mean_rad_s=float(omega.mean()),world_omega_z_end3s_mean_rad_s=float(omega[-300:].mean()),yaw_change_end3s_deg=float(np.rad2deg(yy_after[-1]-yy[-300])),yaw_change_first3s_deg=float(np.rad2deg(yy_after[299]-yy[0])),
    instantaneous_world_omega_z_not_equal_Euler_yaw_rate_by_assumption=True,
    raw_left_clamp_minus6_fraction=float((a[:,i,0]<=-6).mean()),clipped_scaled_requested_crank_minus_hip_rad=q(pd[:,i]),actual_guarded_target_crank_minus_hip_rad=q(actualdiff[:,i]),raw_q_joint_angles_are_not_used_as_CAD_input_difference_limit=True,
    original_static_parameters=dict(mild_friction_mu=params['mild_mu'][i],mild_factor=params['mild_factor'][i],spring=params['spring'][i],gas=params['gas'][i],COM_delta_m=assignments['COM']['delta_m'][i],leg_delay_us=assignments['action']['legs']['delay_us'][i],wheel_delay_us=assignments['action']['wheels']['delay_us'][i],feedback_requested_us=params['feedback_requested_us'][i],wheel_motor_episode_scale=params['motors']['wheels']['episode_scale'][i]),
    three_second_yaw_and_motor_bins=bins))
 extra[label]=dict(moving54_raw_left_lower_clamp_fraction=float((a[:,moving,0]<=-6).mean()),moving54_actual_CAD_lower_projection_fraction=float((pd[:,moving]<-1.0843).mean()),moving54_actual_left_target_lower_guard_fraction=float((np.abs(actualdiff[:,moving]+1.0843)<=2e-6).mean()),perenv_rawclip_fraction_range=[float((a[:,i,0]<=-6).mean()) for i in moving],perenv_original_CAD_lower_projection_fraction_range=[float((pd[:,i]<-1.0843).mean()) for i in moving],residual_perenv=per,
   original_query_contact_COM_hardware_scope_preserved=True,physical_delay_queue_rows_NOT_captured_in_full80=True,requested_raw_wheel_output_diagnostic_only_not_actual_delayed_target=True)
summaries=[]
for group in [0,1]:
 for complete in [True,False]:
  rows=[r['new'] for r in j['all54_paired'] if r['new']['group']==group and r['new']['complete_original_contact']==complete]
  summaries.append(dict(group=group,complete=complete,count=len(rows),mean_actual_signed_world_vx_m_s=float(np.mean([r['signed_world_vx_m_s']['mean'] for r in rows])),mean_actual_signed_body_along_m_s=float(np.mean([r['signed_body_along_v_m_s']['mean'] for r in rows])),yaw_abs_max_deg_range=[min(r['yaw_abs_max_deg'] for r in rows),max(r['yaw_abs_max_deg'] for r in rows)],left_CAD_projection_fraction_range=[min(r['left_CAD_lower_projection_fraction'] for r in rows),max(r['left_CAD_lower_projection_fraction'] for r in rows)]))
out=dict(epoch=time.time(),passed=True,parent_actual_report=dict(path=str(I),sha256=sha(I)),old_new=extra,new_complete_vs_unfinished_summaries=summaries,
  original_thresholds_not_changed=True,new_candidate_checkpoint_created=False,new_GPU_or_PPO=False,new_RNG_draw=False,source_old=j['source_old'],source_new=j['source_new'],Git_archive_pending_root_owner=True,
  interpretation=dict(joint_execution_domain='Raw minus6 clipping decreased from baseline all moving controls100%; actual crank-minus-hip CAD lower projection remains 99.998765percent across newmoving54; all successfulmoving envs also100% projected. This proves persistent joint input-domain collapse but does not classify failure uniquely.',
  motion='Large yaw grows across the entire15s in6/15/21/67/69/70; actual world omega_z retains systematic sign in late bins. Body-along velocity alone hides lack or reversal of prescribed world-x progress.',
  near_boundary='env6 gets both wheelCOMs beyond authored wave end by149.89mm, with actual flat triangle surfaces0m, but original200mm after margin remains short50.11mm; original false retained.',
  low_speed='env72 body-along mean.15793m/s and last3s.05311m/s; world-x mean.15402m/s, relatively limited cross until12s. It is a slowdown with late turn, rather than loss of1N support.',
  causation='Initial DR/queue/parameters matched, but rollout output and plant interactions change with learned actor. Pending flat/world/spin skills preclude claiming terrain-specific or unique causation.',
  proposed_next_single_axis='Before another duration-only block, CPU quantify a deeper-interior one-time left mean initialization with smaller explicitly bound left std on same complete20k2b source; preserve other5heads/critic/fullDRRNG and source counters. Any newcandidate requires independent CPU/fullstate/ownnative/PPO/fresh and frozen behavior admission. Pure coupled-domain CPU math may diagnose legal probability but must not become live coupling or alter production6action/processor/teacher/heading/DRrewardclockhardware without a separate approved scope. No such candidate adopted here.'))
P.write_text(json.dumps(out,indent=2),encoding='utf8')
print(json.dumps(dict(report=str(P),old_rawclip=extra['old']['moving54_raw_left_lower_clamp_fraction'],new_rawclip=extra['new']['moving54_raw_left_lower_clamp_fraction'],new_jointprojection=extra['new']['moving54_actual_CAD_lower_projection_fraction'],yaw_timebins_saved=True,no_new_candidate=True)))
