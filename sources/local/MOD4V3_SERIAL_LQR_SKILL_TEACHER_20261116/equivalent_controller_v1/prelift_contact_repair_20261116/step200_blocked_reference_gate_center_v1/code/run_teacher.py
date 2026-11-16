"""Teacher-only acceptance and actuation audit; zero actor inference."""
from pathlib import Path
import argparse,json,time,traceback
import numpy as np
from native_runtime import NativeTeacher,ROOT,PPO_TO_NATIVE

def run(case,out):
 start=time.perf_counter();teacher=NativeTeacher(out,height=case.get('height',0.),start_x=case.get('start_x',0.),yaw=np.deg2rad(case.get('yaw_deg',0.)),length=case.get('length',.25),reset_pitch=np.deg2rad(case.get('pitch_deg',0.)),actuation=case.get('actuation','native_action'))
 teacher.controller.args.jump_target_height=case.get('target_height')
 teacher.controller.native_contact_history=case.get('native_contact_history',False)
 teacher.surface_observer.contact_hysteresis=case.get('contact_geometry_hysteresis',False)
 teacher.controller.native_encoder_rates=case.get('native_encoder_rates',False)
 teacher.controller.native_blocked_wheel_reference=case.get('blocked_wheel_reference',False)
 teacher.controller.step_climb.native_prelift_geometry_gate=case.get('prelift_geometry_gate',False)
 step_diagnostics=[]
 frames=[];qs=[];vs=[];requests=[];actions=[];actual=[];errors=[];feasible_errors=[];projected=[];empty=0;phases=[];stop=False;top_hold=0.;best_hold=0.;airtime=0.;best_air=0.;air=False;landhold=0.;best_land=0.;height0=float(teacher.d.qpos[2]);peak=height0;com0=float(teacher.m.body_mass@teacher.d.xipos[:,2]/teacher.m.body_mass.sum());com_peak=com0;entry=None;error=None
 try:
  for k in range(int(round(case.get('duration',8.)/.02))):
   age=k*.02;v=case.get('speed',0.)if age>=case.get('approach_time',1.) and not stop else 0.
   pre_speed=float(np.linalg.norm(teacher.d.qvel[:2]))
   jump=case.get('kind')=='jump'and abs(age-1.)<.001
   diag=teacher.step((v/teacher.controller.reference_governor.max_speed,0.,0.,jump))
   RPY=teacher.euler();ground,top,edge,guide=teacher.contacts();wheel=teacher.d.geom_xpos[teacher.tire].copy();vel=float(np.linalg.norm(teacher.d.qvel[:2]));peak=max(peak,float(teacher.d.qpos[2]));phase=teacher.controller.step_climb.phase;jphase=teacher.controller.jump_state;com_peak=max(com_peak,float(teacher.m.body_mass@teacher.d.xipos[:,2]/teacher.m.body_mass.sum()))
   if case.get('height',0.)>0 and (edge.any() or guide>5.) and entry is None:entry=dict(time=age+.02,speed=pre_speed,pre_100ms_speed=float(np.mean([x[7]for x in frames[-5:]]))if frames else pre_speed,post_contact_speed=vel,odom_speed=float(teacher.controller.body_odom.velocity),yaw_deg=float(np.rad2deg(RPY[2])),root_x=float(teacher.d.qpos[0]))
   # World geometry is used only for scoring and the evaluator's stop request.
   crossing=bool(top.all()and teacher.d.qpos[0]>1.2+.03)
   if crossing and phase=='idle':stop=True
   stable=bool(crossing and abs(RPY[0])<.35 and abs(RPY[1])<.35 and vel<.60)
   top_hold=top_hold+.02 if stable else 0.;best_hold=max(best_hold,top_hold)
   airborne=bool(not ground.any()and min(wheel[:,2]-.0625)>.015)
   airtime=airtime+.02 if airborne else 0.;best_air=max(best_air,airtime);air|=airborne
   landed=bool(air and ground.all()and abs(RPY[0])<.25 and abs(RPY[1])<.25 and vel<.4 and jphase=='idle')
   landhold=landhold+.02 if landed else 0.;best_land=max(best_land,landhold)
   contact_control=dict(blocked_reference=teacher.controller.last_state.get('_native_blocked_reference'),encoder_rates=teacher.controller.last_state.get('_native_encoder_rates'),raw=teacher.controller.last_state.get('_wheel_contacts_raw'),used=teacher.controller.last_state.get('_wheel_contacts'),confirmed=teacher.controller._wheel_support_confirmed.tolist(),scale=teacher.controller._wheel_torque_scale.tolist(),history=teacher.controller.last_state.get('_native_prelift_contact_history',False),double_support=teacher.controller._has_double_support(teacher.controller.last_state))
   step_diagnostics.append(dict(time=age,phase=phase,contact_control=contact_control,trigger=getattr(teacher.controller.step_climb,'diagnostic',{}),contact=teacher.controller.last_state.get('_native_contacts')))
   frames.append([age+.02,*teacher.d.qpos[:3],*RPY,vel,*wheel.reshape(-1),*ground,*top,*edge,guide,best_hold,teacher.closure_peak,teacher.controller.body_odom.velocity,*teacher.controller.step_climb.wheel_load,teacher.controller.step_climb.support,*teacher.controller.last_x_lqr[:,0]])
   qs.append(teacher.d.qpos.copy());vs.append(teacher.d.qvel.copy());requests.append(diag['requested']);actions.append(diag['action']);actual.append(diag['actual']);errors.append(diag['first_error']);feasible_errors.append(diag['feasible_first_error']);projected.append(diag['feasible_requested']);empty+=int(diag['empty_feasible_set']);phases.append((phase,jphase))
   if abs(RPY[0])>1.2 or abs(RPY[1])>1.2 or teacher.d.qpos[2]<.11:break
 except Exception:
  error=traceback.format_exc()
 out=Path(out);(out/'STEP_DIAGNOSTICS.json').write_text(json.dumps(step_diagnostics,ensure_ascii=False,indent=2)+chr(10),encoding='utf8');fr=np.asarray(frames);err=np.asarray(errors);req=np.asarray(requests);act=np.asarray(actual)
 result=dict(case=case,frames=len(frames),sim_seconds=float(teacher.d.time),wall_seconds=time.perf_counter()-start,teacher_only=True,actor_calls=0,optimizer_steps=0,pass_stair=best_hold>=.4,pass_jump=bool(best_air>=.04 and best_land>=.4),max_continuous_top_hold_s=best_hold,max_double_air_s=best_air,max_landed_hold_s=best_land,root_rise_m=peak-height0,com_rise_m=com_peak-com0,entry=entry,closure_peak_m=teacher.closure_peak,final_position=teacher.d.qpos[:3].tolist(),final_rpy_deg=np.rad2deg(teacher.euler()).tolist(),phase_counts={p:phases.count(p)for p in sorted(set(phases))},error=error)
 result['pass_jump']=bool(case.get('kind')=='jump' and result['pass_jump'])
 result['empty_feasible_frames']=empty
 result['protocol']='NATIVE_EQUIVALENT_TEACHER_V1_20261116'
 if len(fr):
  post=fr[fr[:,0]>=2.]
  heading=float(np.rad2deg(abs(post[:,6])).max()) if len(post) else None
  result['post_2s_heading_peak_deg']=heading
  result['heading_qualified']=bool(heading is not None and heading<=5.)
  result['entry_speed_qualified']=bool(entry is not None and .28<=entry['pre_100ms_speed']<=.52)
  result['pass_teacher_stair']=bool(result['pass_stair']and result['heading_qualified']and result['entry_speed_qualified'])
  target=case.get('target_height')
  result['jump_target_error_m']=None if target is None else result['com_rise_m']-target
  result['pass_teacher_jump']=bool(result['pass_jump']and result['heading_qualified']and (target is None or abs(result['jump_target_error_m'])<=.02))
 result['phase_counts']={str(k):v for k,v in result['phase_counts'].items()}
 if len(fr):
  result.update(pitch_peak_deg=float(np.rad2deg(abs(fr[:,5])).max()),yaw_peak_deg=float(np.rad2deg(abs(fr[:,6])).max()),last_1s_yaw_peak_deg=float(np.rad2deg(abs(fr[-50:,6])).max()),first_inverse_max_error_nm=np.max(abs(err),axis=0).tolist(),first_inverse_rms_error_nm=np.sqrt(np.mean(err**2,axis=0)).tolist(),interval_rms_error_nm=np.sqrt(np.mean((act-req[:,None,:])**2,axis=(0,1))).tolist(),feasible_first_max_error_nm=np.max(np.abs(feasible_errors),axis=0).tolist(),projection_rms_nm=np.sqrt(np.mean((np.asarray(projected)-req)**2,axis=0)).tolist(),motor_peak_nm=np.max(abs(act),axis=(0,1)).tolist(),phase_transitions=[dict(t=float(fr[i,0]),stair=phases[i][0],jump=phases[i][1])for i in range(len(phases))if i==0 or phases[i]!=phases[i-1]])
 np.savez_compressed(out/'trace.npz',trace=fr,qpos=np.asarray(qs),qvel=np.asarray(vs),requested=req,feasible_requested=np.asarray(projected),feasible_error=np.asarray(feasible_errors),actions=np.asarray(actions).reshape(-1,6)[:,PPO_TO_NATIVE],actual=act,first_error=err,phases=np.asarray(phases),columns=np.asarray(['time','x','y','z','roll','pitch','yaw','speed','wheel_lx','wheel_ly','wheel_lz','wheel_rx','wheel_ry','wheel_rz','contact_l','contact_r','top_l','top_r','edge_l','edge_r','guide_force','best_top_hold','closure_peak','odom_v','load_l','load_r','support']+['lqr_'+str(i)for i in range(10)]))
 (out/'RESULT.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+chr(10),encoding='utf8');print(json.dumps(result,ensure_ascii=False),flush=True);return result
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--case',default='{}');ap.add_argument('--out',required=True);args=ap.parse_args();run(json.loads(args.case),Path(args.out))
