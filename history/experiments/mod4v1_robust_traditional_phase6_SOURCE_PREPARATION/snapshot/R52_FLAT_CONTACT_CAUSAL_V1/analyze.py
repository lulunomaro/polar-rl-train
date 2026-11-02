"""One R52TRAINflat only. Windowed private truth offline, no q reconstruction."""
from pathlib import Path
import hashlib,json,math,traceback
R=Path(__file__).resolve().parent;C=R.parent/'results/r52_early_flat'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def new(p,x):assert not p.exists();p.write_text(json.dumps(x,ensure_ascii=False,allow_nan=False,separators=(',',':'))+'\n',encoding='utf-8')
def main():
 assert not(R/'REPORT.md').exists();v=json.loads((C/'result.json').read_text(encoding='utf-8'));cfg=v['config'];assert cfg['case_id']=='r52_early_flat'and cfg['scene']=='flat'
 with(C/'trace.jsonl').open(encoding='utf-8')as f:trace=[json.loads(x)for x in f]
 assert len(trace)==v['controls']==800
 h=cfg['hop'];threshold=h['trigger_time_s']+h['push_for_s']+h['predicted_air_after_push_s'];obs_threshold=h['trigger_time_s']+h['push_for_s']+h['observer_quarantine_after_push_s']
 capture=next(x for x in trace if x['phase'].get('landing_capture_started_s')is not None);change=next(x for x in trace if x['phase'].get('landing_transition_weight',0)>0.);observer=next(x for x in trace if x['command_time_s']>=h['trigger_time_s']+h['push_for_s']and not x['phase']['wheel_measurement_disabled_predicted']);gravity=next(x['command_time_s']for x in trace if x['command_time_s']>=threshold)
 landing=v['first_landing']['stage_time_s'];guide_count=hard_count=0;guide_first=None;guide_last=None;peak=None;window=[];total=0;episodes=[];run=None
 with(C/'physics.jsonl').open(encoding='utf-8')as f:
  for line in f:
   x=json.loads(line);t=x['stage_time_s'];total+=1;on=x['guide_normal_N']>1.;hard_count+=x['hard_normal_N']>1.
   if on:
    guide_count+=1;guide_first=t if guide_first is None else guide_first;guide_last=t
    if peak is None or x['guide_normal_N']>peak['force']:peak={'time':t,'force':x['guide_normal_N']}
    if run is None:run={'start':t,'ticks':0,'peak_N':0.}
    run['ticks']+=1;run['last_post']=x['root_post_time_s'];run['peak_N']=max(run['peak_N'],x['guide_normal_N'])
   elif run is not None:episodes.append(run);run=None
   if 2.30<=t<=2.75:window.append(x)
 if run:episodes.append(run)
 assert total==v['physics_steps']==16000 and guide_count==v['guide_contact_physics_ticks']==7 and hard_count==v['hard_contact_physics_ticks']==0
 def at(t):return min(window,key=lambda x:abs(x['stage_time_s']-t))
 def snapshot(x):
  stage=x['stage_time_s'];i=int(round(stage/.0005))//20;z=trace[i];p=z['phase'];a=x['private_contact_diagnostic']['root_rotation_world_from_body33_pre'];contacts=[{'robot':q['robot_geom'],'environment':q['environment_geom'],'normal_N':q['normal_N'],'point_world_m':q['position_world_m'],'normal_geom1_to2':q['normal_geom1_to_geom2_world']}for q in x['environment_contacts']if q['normal_N']>0]
  return {'stage_s':stage,'root_PRE_xyz_m':x['drivepoint']['root_xyz_pre_m'],'root_POST_time_s':x['root_post_time_s'],'root_POST_xyz_distinct':x['root_xyz_post_m'],'pitch_roll_STAGE_deg':[math.degrees(math.atan2(-a[2][0],math.hypot(a[0][0],a[1][0]))),math.degrees(math.atan2(a[2][1],a[2][2]))],'main_N2':x['main_normal_N2'],'guide_N':x['guide_normal_N'],'hard_N':x['hard_normal_N'],'contacts':contacts,'bracketing_control_start_s':z['command_time_s'],'bracketing_sensor_time_s':z['sensor_time_s'],'bracketing_encoder4_NOT2kq':z['encoder_q4'],'phase':p.get('phase'),'capture_started':p.get('landing_capture_started_s'),'landing_weight':p.get('landing_transition_weight'),'actual_V3_position_ref4':p.get('landing_position_ref4'),'legacy_phase_target_q4_NOT_current_capture_ref':p.get('target_q4'),'observer_disabled_log':p['wheel_measurement_disabled_predicted'],'stage_velocity6':x['drivepoint']['velocity6_rad_s'],'stage_actual_tau6':x['drivepoint']['actual_tau6_Nm'],'actual_perleg_q4_at2k':'unknown; optional reconstruction not performed'}
 events={k:snapshot(at(t))for k,t in {'first_landing':landing,'first_guide':guide_first,'peak_guide':peak['time'],'last_guide':guide_last,'capture_control':capture['command_time_s'],'first_K_ff_ref_weight_positive':change['command_time_s'],'observer_restore_control':observer['command_time_s']}.items()}
 sources=[{'path':str(C/'result.json'),'SHA':sha(C/'result.json'),'bytes':(C/'result.json').stat().st_size},{'path':str(Path(__file__)),'SHA':sha(Path(__file__))}]
 d={'status':'BOUNDED_R52_FLAT_OFFLINE_CONTACT_TIMING_NOT_NEW_QUALIFICATION','case':cfg['case_id'],'window_read_for_pose':[2.30,2.75],'physics_outside_window_used_only_for_guide_hard_counts':True,'old_original_result_gates':{k:v[k]for k in('complete','proposed_moving_flat_air80_stop_v1','guide_contact_physics_ticks','hard_contact_physics_ticks','end_stable_s','maximum_main_mesh_clearance_during_full_air_m','max_pitch_rad')},'first_landing_s':landing,'guide_episodes':episodes,'guide_first_s':guide_first,'guide_last_s':guide_last,'capture_first_control_s':capture['command_time_s'],'K_ff_ref_first_positive_weight_control_s':change['command_time_s'],'gravity_schedule_first_control_s':gravity,'gravity_state_not_independently_logged':True,'observer_first_enabled_control_s':observer['command_time_s'],'events':events,'all800_control_time_monotonic':all(b['command_time_s']>a['command_time_s']for a,b in zip(trace,trace[1:])),'source_small_SHA':sources,'raw_producer_refs_only':[v['trace_artifact'],v['physical_artifact']],'rawSHA_recomputed':False,'only_this_case_read':True,'no_q_reconstruction_or_target_substitution':True,'newphysics_Git_agents_H5_assets_or_gainfit':False,'old_files_modified':False,'PH6pending':True};new(R/'DETAILS.json',d)
 lines=['# R52 flat contact causal audit — offline TRAIN only','',f"原complete800/16000，flat gate={v['proposed_moving_flat_air80_stop_v1']}；guide={guide_count},hard={hard_count}；peakmesh={v['maximum_main_mesh_clearance_during_full_air_m']!r}m,endstable={v['end_stable_s']!r}s。未改score/gate。",'','|event|same-stage time s|rootPRE z m|stage pitch deg|phase|V3 captureweight|guide N|','|---|---:|---:|---:|---|---:|---:|']
 for k,x in events.items():lines.append('|'+ '|'.join(map(str,[k,x['stage_s'],x['root_PRE_xyz_m'][2],x['pitch_roll_STAGE_deg'][0],x['phase'],x['landing_weight'],x['guide_N']]))+'|')
 lines+=['',f"Guide>1N原7个physicsrows，episode={episodes}。实际接触面/point/normal见DETAILS的first_guide.contacts，不从target姿态推断。",f"capture首control={capture['command_time_s']!r}，K/ff/ref插值weight首次>0={change['command_time_s']!r}；gravity按锁定旧source schedule映射到control={gravity!r}（该flag未独立逐row记录）；observer实际日志首恢复={observer['command_time_s']!r}。",'在capture中legacy phase.target_q4可能保留flight target；正确位置参考是landing_position_ref4，变化weight同时对应K/nominalff/ref，本文不把legacy字段当真实currentref。','2kactual单腿q未知：本次不做可选重建。100Hzencoder仅bracket，rootPRE与cachedR/force同stage；rootPOST另time，不能混搭成同瞬间姿态。','只有一个TRAINflat观察，不选predAir/gain、不过拟合、不推断反事实一定成功；RM准入未通过，与其未启动的父decision一致。','读取仅该case smallresult/trace；physics pose仅[2.30,2.75]，外侧仅原guide/hard计数；不读其他case/H5/资产，无279mesh/新physics/Git/agent/真实IO/rawhash。','[DETAILS](<DETAILS.json>) / [receipt](<RECEIPT.json>)。']
 assert len(lines)+1<=70;(R/'REPORT.md').write_text('\n'.join(lines)+'\n',encoding='utf-8');new(R/'RECEIPT.json',{'status':'R52_SINGLE_FLAT_BOUNDED_OFFLINE_DIAGNOSTIC_COMPLETE','report_SHA':sha(R/'REPORT.md'),'details_SHA':sha(R/'DETAILS.json'),'source_SHA':sha(Path(__file__)),'report_plus_receipt_lines':len(lines)+1,'newphysics_Git_agents_H5_gainfit_rawhash':False,'old_files_modified':False,'PH6pending':True});print(json.dumps({'events':events,'timing':{k:d[k]for k in('first_landing_s','guide_first_s','guide_last_s','capture_first_control_s','K_ff_ref_first_positive_weight_control_s','gravity_schedule_first_control_s','observer_first_enabled_control_s')},'guide':episodes,'REPORT':str(R/'REPORT.md'),'SHA':sha(R/'REPORT.md'),'lines':len(lines)+1},ensure_ascii=False,indent=2))
if __name__=='__main__':
 try:main()
 except BaseException:
  n=1
  while(R/f'ERROR_{n:03d}.txt').exists():n+=1
  (R/f'ERROR_{n:03d}.txt').write_text(traceback.format_exc(),encoding='utf-8');(R/f'SOURCE_ERROR_{n:03d}.py').write_bytes(Path(__file__).read_bytes());raise
