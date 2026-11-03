"""One-open R63 4610 TRAIN contact audit. No model/SDK/QA/Git/raw SHA."""
from pathlib import Path
import datetime,hashlib,json,math,traceback
R=Path(__file__).resolve().parent;T=R.parent;CASE='r63_spring_release_DR4610';B=T/'results'/CASE;OLD=T/'results/r60_tall0_fresh_RM_DR_4610/result.json';DT=.0005;MAX_LINES=17600;OPENS={};LINES={}
def load(p):return json.loads(p.read_text(encoding='utf-8'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def new(p,x):
 assert not p.exists(),str(p);p.write_text(json.dumps(x,ensure_ascii=False,indent=2,allow_nan=False)+'\n',encoding='utf-8')
def finite(x):
 assert type(x)in(int,float)and math.isfinite(x),'nonfinite or invalid numeric';return float(x)
def main():
 assert not(R/'SOURCE_PREEXEC.json').exists()and not(R/'EVENTS.json').exists(),'Once-only: inspect partial evidence instead of replay'
 v=load(B/'result.json');old=load(OLD);sm=load(B/'SOURCE_MANIFEST.json');cfg=v['config'];assert cfg['case_id']==CASE and cfg['seed']==4610 and cfg['nominal']is False and v['controls']==800 and v['physics_steps']==16000
 assert v['complete']is True and v['guide_contact_physics_ticks']==3
 cache_path=T/'R63_SPRING_PUSH_ADMISSION_V1/PRE_EXEC_REVIEW.json';cache=load(cache_path);locked={str(Path(x['path']).resolve()).lower():x['SHA']for x in cache['checked_sources']};prod={str(Path(x['path']).resolve()).lower():x['SHA']for x in sm['files']}
 names=['SPRING_PUSH_RELEASE_V1/run_manual_spring_push_v1.py','SPRING_PUSH_RELEASE_V1/controller.py','MINIHOP_AUDIT_V2/contact_grade_v2.py','MANUAL_FIRST_BAR_V1/grade_rows.py','MANUAL_FIRST_BAR_V1/grade_rows_v2.py','MINIHOP_LANDING_V3/controller.py','MINIHOP_OBSERVER_V2/controller.py'];semantic=[]
 for n in names:
  p=T/n;k=str(p.resolve()).lower();assert prod[k]==locked[k];semantic.append({'path':str(p),'producer_SHA':prod[k],'cache_SHA':locked[k],'mode':'producer_record_matches_prior_read_review_cache_no_body_rehash'})
 small=[Path(__file__),R/'METHOD_PREDECLARED.md',B/'result.json',B/'SOURCE_MANIFEST.json',OLD,cache_path];before=[{'path':str(p),'bytes':p.stat().st_size,'SHA':sha(p)}for p in small]
 refs=[]
 for key,name in(('trace_artifact','trace.jsonl'),('physical_artifact','physics.jsonl')):
  x=v[key];p=B/name;assert Path(x['path']).resolve()==p.resolve()and x['producer_streamed_once']is True and p.stat().st_size==x['bytes'];refs.append({**x,'path':str(p),'SHA_status':'existing_producer_only_not_rehashed','raw_content_SHA_recomputed':False})
 new(R/'SOURCE_PREEXEC.json',{'status':'METHOD_SCRIPT_AND_SMALL_SOURCE_LOCKED_BEFORE_EXACT_TWO_RAW_OPENS','at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'sources':before,'cached_semantics':semantic,'raw_refs':refs,'allowed_raw_paths':[x['path']for x in refs],'raw_open_limit_each':1,'total_line_limit':MAX_LINES,'PH9pending':True})
 def readrows(p):
  assert str(p)in[x['path']for x in refs]and OPENS.get(str(p),0)==0;OPENS[str(p)]=1;LINES[str(p)]=0
  with p.open('rb')as f:
   for raw in f:
    LINES[str(p)]+=1;assert sum(LINES.values())<=MAX_LINES,'Read budget exceeded';yield json.loads(raw)
 trace=list(readrows(B/'trace.jsonl'));assert len(trace)==800
 for i,z in enumerate(trace):assert abs(finite(z['command_time_s'])-i*.01)<1e-8
 def first_control(pred):return next((x for x in trace if pred(x)),None)
 def clock(z):
  if z is None:return None
  h=z['phase'];return {'command_time_s':z['command_time_s'],'sensor_time_s':z['sensor_time_s'],'sensor_age_s':z['sensor_age_s'],'root_post_time_s':z['time_s'],'phase':h.get('phase'),'landing_capture_started_s':h.get('landing_capture_started_s'),'landing_transition_weight':h.get('landing_transition_weight'),'landing_position_ref4':h.get('landing_position_ref4'),'legacy_target_q4_NOT_current_capture_ref':h.get('target_q4'),'observer_disabled':h.get('wheel_measurement_disabled_predicted'),'spring_release_applied':h.get('spring_release_applied_this_command'),'requested_tau6':z['requested_tau6'],'forward_command_m_s':z.get('forward_command_m_s'),'position_decision_time_s':h.get('position_decision_time_s'),'position_latched_push_time_s':h.get('position_latched_push_time_s')}
 push=first_control(lambda z:z['phase'].get('phase')=='timed_push');assert push
 afterpush=push['command_time_s']+cfg['hop']['push_for_s'];capture=first_control(lambda z:z['phase'].get('landing_capture_started_s')is not None);weight=first_control(lambda z:z['phase'].get('landing_transition_weight',0.)>0.);obs_off=first_control(lambda z:z['command_time_s']>=afterpush and z['phase'].get('wheel_measurement_disabled_predicted')is True);obs_on=first_control(lambda z:z['command_time_s']>=afterpush and z['phase'].get('wheel_measurement_disabled_predicted')is False);brake=first_control(lambda z:z['command_time_s']>=cfg['brake_at_s'])
 schedule={'first_push':clock(push),'capture_first_control':clock(capture),'first_positive_K_ff_ref_interpolation_weight':clock(weight),'postpush_observer_first_disabled':clock(obs_off),'postpush_observer_actual_first_enabled':clock(obs_on),'brake_first_control_config_plus_logged_forward':clock(brake),'gravity_correction_not_independently_logged':'inherited timer schedule only; not used to claim actual sensor flag'}
 def snapshot(x):
  idx=x['sample_index'];stage=finite(x['stage_time_s']);dp=x['drivepoint'];assert abs(finite(dp['time_s'])-stage)<1e-8
  z=trace[idx//20];assert z['command_time_s']-1e-8<=stage<=z['time_s']+1e-8
  a=x['private_contact_diagnostic']['root_rotation_world_from_body33_pre'];pitch=math.degrees(math.atan2(-finite(a[2][0]),math.hypot(finite(a[0][0]),finite(a[1][0]))));roll=math.degrees(math.atan2(finite(a[2][1]),finite(a[2][2])))
  cs=[]
  for c in x['environment_contacts']:
   if finite(c['normal_N'])>0:
    sign=1. if c['robot_is_geom2']else-1.;n=[sign*finite(y)for y in c['normal_geom1_to_geom2_world']];face='top_up'if n[2]>.9 else('bottom_down'if n[2]<-.9 else'edge_or_inclined_not_top')
    cs.append({'robot_geom':c['robot_geom'],'robot_body':c['robot_body'],'environment_geom':c['environment_geom'],'kind':c['kind'],'normal_N':c['normal_N'],'position_world_m':c['position_world_m'],'normal_toward_robot_world':n,'surface_orientation_description_not_exact_shape_certificate':face,'force_on_robot_world_N3':c['force_on_robot_world_N3']})
  return {'sample_index':idx,'stage_time_s':stage,'drivepoint_time_s':dp['time_s'],'root_POST_time_s':x['root_post_time_s'],'root_PRE_xyz_m':dp['root_xyz_pre_m'],'root_POST_xyz_m':x['root_xyz_post_m'],'pitch_roll_deg_same_PRE_stage':[pitch,roll],'main_N2':x['main_normal_N2'],'guide_N':x['guide_normal_N'],'hard_N':x['hard_normal_N'],'all_world_N':x['all_world_normal_N'],'positive_contacts':cs,'actual_drive_velocity6_rad_s':dp['velocity6_rad_s'],'actual_drive_tau6_Nm':dp['actual_tau6_Nm'],'adjacent_current_control':clock(z),'command_to_drive_stage_time_s':stage-z['command_time_s'],'sensor_to_drive_stage_time_s':stage-z['sensor_time_s'],'actual_perleg_q4_at_2k':'UNKNOWN_NOT_PERSISTED_NOT_INTEGRATED_FROM_D1D2_ENCODERS','request_vs_drive_semantics':'request at control.command_time; drive at this stage; D4/PD/gain/clip may differ. Delta time recorded, not a same-snapshot command tracking certificate.','original_cache_stages':x.get('cache_stages'),'private_before_first_landing':x.get('private_before_first_landing')}
 air_run=0;air_start=None;firstair=None;confirmation=None;landing=None;crossing=None;guide=[];segments=[];guide_n=0;hard_n=0;last_on=-2;total=0;mtick=round(v['first_flight_main_rear_crossing_bar_back_s']/DT)
 for x in readrows(B/'physics.jsonl'):
  k=x['sample_index'];assert k==total and abs(finite(x['stage_time_s'])-k*DT)<1e-8;total+=1
  force=finite(x['all_world_normal_N']);g=finite(x['guide_normal_N']);h=finite(x['hard_normal_N']);hard_n+=int(h>1.)
  if force<=1.:
   if air_run==0:air_start=x
   air_run+=1
  else:air_run=0
  if firstair is None and air_run*DT>=.02:firstair=snapshot(air_start);confirmation=snapshot(x)
  if firstair is not None and landing is None and force>1.:landing=snapshot(x)
  if k==mtick:crossing=snapshot(x)
  if g>1.:
   q=snapshot(x);guide.append(q);guide_n+=1
   if k!=last_on+1:segments.append({'first':q,'peak':q,'last':q,'ticks':0})
   s=segments[-1];s['last']=q;s['ticks']+=1
   if g>s['peak']['guide_N']:s['peak']=q
   last_on=k
 assert total==16000 and sum(LINES.values())==16800 and guide_n==v['guide_contact_physics_ticks']==3 and hard_n==v['hard_contact_physics_ticks']==0
 assert abs(firstair['stage_time_s']-v['first_all_world_air_s'])<1e-8 and abs(landing['stage_time_s']-v['first_landing']['stage_time_s'])<1e-8 and crossing is not None
 for s in segments:s.update(duration_s=s['ticks']*DT,last_POST_time_s=s['last']['root_POST_time_s'])
 original_keys=['complete','stop','controls','physics_steps','proposed_manual_first_bar_clear_stop_v1','guide_contact_physics_ticks','hard_contact_physics_ticks','end_stable_s','maximum_main_mesh_clearance_during_full_air_m','first_flight_main_rear_crossing_bar_back_s','conservative_final_robot_all_collision_behind_bar','conservative_front_never_reached_next_bar']
 events={'status':'R63_SINGLE_SEED4610_BOUNDED_ONCE_READ_CONTACT_AUDIT_NO_NEW_ACCEPTANCE','case':CASE,'original_result':{k:v[k]for k in original_keys},'baseline_R60_same_seed_small_result_only':{k:old[k]for k in original_keys},'source_small_SHA':before,'raw_producer_refs':refs,'schedule':schedule,'first_air_onset':firstair,'air_confirmed_POST_time_s':confirmation['root_POST_time_s'],'air_confirmation_stage':confirmation,'mainrear_firstflight_original_result_time_join_not_new_geometry':crossing,'first_operational_landing':landing,'all_guide_above1N_physics_rows':guide,'guide_segments':segments,'raw_open_counts':OPENS,'raw_line_counts':LINES,'old_raw_or_other_seed_or_H5_mesh_read':False,'q_reconstruction_or_FK_or_dynamic_model_or_score_changes':False,'contact_truth_offline_only':True,'temporal_order_not_unique_cause_or_new_gain_selection':True,'PH9pending':True}
 new(R/'EVENTS.json',events)
 def brief(q):
  ids='; '.join(c['robot_geom']+'→'+c['environment_geom']+'/'+c['surface_orientation_description_not_exact_shape_certificate']+':'+format(c['normal_N'],'.6g')+'N'for c in q['positive_contacts']);c=q['adjacent_current_control']
  return f"{q['stage_time_s']:.9f} | {ids} | z={q['root_PRE_xyz_m'][2]:.9f},pitch/roll={q['pitch_roll_deg_same_PRE_stage']} | phase={c['phase']},w={c['landing_transition_weight']},obsDisabled={c['observer_disabled']}"
 lines=['# R63 seed4610：原pass→新guide3，single-TRAIN只读事实审计','',f"- 原R60 smallresult local={old['proposed_manual_first_bar_clear_stop_v1']} guide/hard={old['guide_contact_physics_ticks']}/{old['hard_contact_physics_ticks']}；新local={v['proposed_manual_first_bar_clear_stop_v1']} guide/hard={guide_n}/{hard_n}，complete800/16000，endstable={v['end_stable_s']!r}。旧raw未读，score不改。",f"- push/decision：{schedule['first_push']}。",f"- operational air onset={firstair['stage_time_s']!r}，确认POST={confirmation['root_POST_time_s']!r}；mainrear-firstflight原result={v['first_flight_main_rear_crossing_bar_back_s']!r}只join原row，不冒whole-robot净跨。",'- 事件表：stage | positive接触/朝机器人normal描述 | same-PRE pose | adjacent100Hz实际状态','- landing：'+brief(landing)]
 for i,q in enumerate(guide,1):lines.append(f'- guide tick{i}：'+brief(q))
 lines +=[f"- capture实际首control={None if capture is None else capture['command_time_s']!r}，首正K/ff/ref weight={None if weight is None else weight['command_time_s']!r}，observer实际恢复={None if obs_on is None else obs_on['command_time_s']!r}；brake配置={cfg['brake_at_s']!r}/首control={None if brake is None else brake['command_time_s']!r}。",'- 各guide control bracket的实际landing_position_ref4/weight/requestedτ6、same-stage driveτ6/velocity6以及command/sensor→drive时间差见EVENTS；legacytarget另标，不当当前capture参考。','- 2k根PRE旋转/XYZ与force同stage，rootPOST另时刻；2k实际各腿q未知，不从有D1D2 encoder推导。3ticks不是3contact points，positive点即使<1N也完整保存。','- 单案只给landing/支撑域/phase仲裁事实；先后不证明capture/observer/brake或弹簧FF为唯一原因，不选新target/gain，不添资格门或自动PHY。',f'- 仅2new raw各1open/总16800行<=17600；小源先后SHA核对；producerSHA引用未重hash；no旧raw/其他seed/H5/ZIP/mesh/新PHY/FK/模型/QA/Git/agent。PH9pending。','', '证据：[EVENTS](<EVENTS.json>) · [预声明](<METHOD_PREDECLARED.md>) · [SOURCE_PREEXEC](<SOURCE_PREEXEC.json>) · [RECEIPT](<RECEIPT.json>)']
 assert len(lines)<=45
 report=R/'REPORT.md';assert not report.exists();report.write_text('\n'.join(lines)+'\n',encoding='utf-8')
 assert all(sha(Path(x['path']))==x['SHA']for x in before),'Small source changed'
 receipt={'status':'COMPLETE_ONCE_READ_R63_4610_CONTACT_REGRESSION_AUDIT','at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'source_preexec_SHA':sha(R/'SOURCE_PREEXEC.json'),'event_SHA':sha(R/'EVENTS.json'),'event_bytes':(R/'EVENTS.json').stat().st_size,'report_SHA':sha(report),'report_lines':len(lines),'raw_open_counts':OPENS,'raw_line_counts':LINES,'raw_SHA_recomputed':False,'small_sources_before_after_equal':True,'only_R60_small_result_no_old_raw':True,'scores_sources_thresholds_changed':False,'q_reconstruction_model_FK_PHY_QA_Git_agents_calls':0,'PH9pending':True}
 new(R/'RECEIPT.json',receipt)
 print(json.dumps({'status':receipt['status'],'report_SHA':receipt['report_SHA'],'report_lines':len(lines),'guide_ticks':guide_n,'guide_segments':len(segments),'firstair':firstair['stage_time_s'],'confirmed_POST':confirmation['root_POST_time_s'],'mainrear_firstflight':v['first_flight_main_rear_crossing_bar_back_s'],'landing':brief(landing),'guide':[brief(q)for q in guide],'capture':None if capture is None else capture['command_time_s'],'positive_weight':None if weight is None else weight['command_time_s'],'observer_restore':None if obs_on is None else obs_on['command_time_s'],'brake':None if brake is None else brake['command_time_s'],'raw_open_counts':OPENS},ensure_ascii=True,indent=2))
if __name__=='__main__':
 try:main()
 except BaseException:
  n=1
  while(R/f'FAILURE_{n:03d}.txt').exists():n+=1
  (R/f'FAILURE_{n:03d}.txt').write_text(traceback.format_exc(),encoding='utf-8');(R/f'FAILURE_SOURCE_{n:03d}.py').write_bytes(Path(__file__).read_bytes());new(R/f'FAILURE_RECEIPT_{n:03d}.json',{'raw_open_counts':OPENS,'lines':LINES,'stop_no_automatic_raw_reopen':True,'no_physics_or_score_change':True});raise
