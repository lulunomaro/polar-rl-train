"""One existing R49case, offline derived grade, no physics/SDK/GTcontrol/Git."""
from pathlib import Path
import hashlib,json,math,sys,collections
import numpy as np
R=Path(__file__).resolve().parent;ROOT=R.parent;CASE=ROOT/'results/r49_long_rm_t210';sys.path.insert(0,str(ROOT))
from CONTACT_PROXY_NOMINAL_V1.nominal_model import NominalModel

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def load(p):return json.loads(p.read_text(encoding='utf-8'))
def new(p,x):assert not p.exists();p.write_text(json.dumps(x,ensure_ascii=False,allow_nan=False,separators=(',',':'))+'\n',encoding='utf-8')
def pose(row,q,model,trace):
 stage=row['stage_time_s'];rot=np.asarray(row['private_contact_diagnostic']['root_rotation_world_from_body33_pre'],float);root=np.asarray(row['drivepoint']['root_xyz_pre_m'],float);i=min(len(trace)-1,int(round(stage/.0005))//20);tr=trace[i];phase=tr['phase'];out={'stage_s':stage,'root_pre_m':root.tolist(),'root_post_time_s':row['root_post_time_s'],'root_post_xyz_distinct':row['root_xyz_post_m'],'pitch_roll_deg':[math.degrees(math.atan2(-rot[2,0],math.hypot(rot[0,0],rot[1,0]))),math.degrees(math.atan2(rot[2,1],rot[2,2]))],'main_N2':row['main_normal_N2'],'guide_N':row['guide_normal_N'],'hard_N':row['hard_normal_N'],'phase_of_bracketing_control':phase,'bracketing_sensor_time_s':tr['sensor_time_s'],'bracketing_encoder4_not_stageq':tr['encoder_q4'],'stage_drive_velocity6':row['drivepoint']['velocity6_rad_s'],'stage_actual_tau6':row['drivepoint']['actual_tau6_Nm'],'derived_stage_active_q4':None if q is None else q.tolist(),'q_derivation_not_original_measurement':True}
 if q is not None:
  fk=model.fk(q,check_limits=False);w=fk['wheel_B'];out['nominal_FK_body_drop_m']=np.mean(-w[:,2]).item();out['nominal_FK_world_drop_m']=np.mean(-(w@rot.T)[:,2]).item();out['nominal_FK_world_wheel_centers_m']=(root+w@rot.T).tolist();out['nominal_FK_guide6_bodycenter_world_m']=(root+rot@fk['body_B'][model.body_index['guide_roller_06']]).tolist();out['nominal_FK_passive_joint_closure_not_actual_complete2kpose']=True
 return out

def main():
 assert not(R/'REPORT.md').exists();cfg=load(CASE/'config.json');res=load(CASE/'result.json');assert cfg['nominal']is True and cfg['case_id']=='r49_long_rm_t210'
 with(CASE/'trace.jsonl').open(encoding='utf-8')as f:trace=[json.loads(x)for x in f]
 assert len(trace)==res['controls']==800;assert all(abs(t['sensor_time_s']-t['command_time_s'])<1e-7 for t in trace)
 dt=.0005;indices=[0,1,3,4];q=np.array(trace[0]['encoder_q4'],float);q_old=q.copy();previous_v=None;anchors={round(t['sensor_time_s']/dt):t for t in trace};checks=[];wrong=[];ticks=0;firstbar=res['first_transverse_bar']['name'];nextbar=res['next_transverse_bar']['name'];landing=res['first_landing']['stage_time_s'];cross=res['clean_air_both_main_rear_crossing_bar_back_s'];events={};selected=[];win3=collections.deque(maxlen=21);next_t=None;guideticks=nextticks=0;firstbar_sides=collections.Counter();guide_sides=collections.Counter();inair_rebound=None
 with(CASE/'physics.jsonl').open(encoding='utf-8')as f:
  for line in f:
   row=json.loads(line);k=ticks;stage=row['stage_time_s'];assert row['sample_index']==k and abs(stage-k*dt)<1e-8
   v=np.asarray(row['drivepoint']['velocity6_rad_s'])[indices]
   if k:q=q+dt*v;q_old=q_old+dt*previous_v
   previous_v=v.copy()
   if k in anchors:checks.append(np.array(anchors[k]['encoder_q4'])-q);wrong.append(np.array(anchors[k]['encoder_q4'])-q_old)
   contacts=row['environment_contacts'];mainbar=[c for c in contacts if c['environment_geom']==firstbar and c['kind']=='main_wheel' and c['normal_N']>0]
   nextforce=math.fsum(c['normal_N']for c in contacts if c['environment_geom']==nextbar);guide=row['guide_normal_N']>1.
   if mainbar and'first_main_firstbar'not in events:events['first_main_firstbar']=(row,q.copy())
   if abs(stage-landing)<1e-8:events['first_landing']=(row,q.copy())
   if guide:
    guideticks+=1
    if'first_guide'not in events:events['first_guide']=(row,q.copy())
    events['last_guide']=(row,q.copy())
    for c in contacts:
     if c['kind']=='guide_roller'and c['normal_N']>0:guide_sides[c['robot_geom']+'->'+c['environment_geom']]+=1
   if nextforce>1.:
    nextticks+=1
    if next_t is None:next_t=stage;events['first_nextbar']=(row,q.copy());selected.extend(win3)
   if cross is not None and abs(stage-cross)<1e-8:events['rear_cross_in_later_air']=(row,q.copy());inair_rebound={'air_qualified':row['air_qualified'],'all_world_normal_N':row['all_world_normal_N'],'air_run_s':row['air_run_s'],'after_first_landing_s':stage-landing}
   if mainbar and 2.1<=stage<=2.515:
    for c in mainbar:
     n=np.asarray(c['normal_geom1_to_geom2_world']);tag='top_up_normal'if abs(n[2])>.9 else 'side_or_edge_normal';firstbar_sides[tag]+=1
   active=2.10<=stage<=2.515 or 2.58<=stage<=2.755 or(next_t is not None and next_t-.01<=stage<=next_t+.02)
   if active:selected.append((row,q.copy()))
   win3.append((row,q.copy()));ticks+=1
 assert ticks==res['physics_steps']==16000 and guideticks==res['guide_contact_physics_ticks']==7
 a=np.asarray(checks);b=np.asarray(wrong);maxerr=float(abs(a).max());accepted=len(a)==800 and maxerr<=1e-9
 model=NominalModel();derived={};contact_surface={}
 for name,(row,qq)in events.items():
  derived[name]=pose(row,qq if accepted else None,model,trace);cs=[c for c in row['environment_contacts']if c['normal_N']>0];contact_surface[name]=[{'robot':c['robot_geom'],'environment':c['environment_geom'],'kind':c['kind'],'normal_N':c['normal_N'],'point_world':c['position_world_m'],'normal_geom1_to2':c['normal_geom1_to_geom2_world']}for c in cs]
 switches=[];prior=None
 for t in trace:
  n=t['command_time_s'];phase=t['phase'];key=(phase.get('phase'),)
  if key!=prior:switches.append({'command_time_s':n,'phase':phase});prior=key
 trigger=cfg['hop']['trigger_time_s'];push=cfg['hop']['push_for_s'];air=cfg['hop']['predicted_air_after_push_s'];quar=cfg['hop']['observer_quarantine_after_push_s']
 gravity_restore=next(t['command_time_s']for t in trace if t['command_time_s']>=trigger+push+air);wheel_restore=next(t['command_time_s']for t in trace if t['command_time_s']>=trigger+push+quar)
 bodywin=[]
 for low,high in[(2.10,2.515),(2.58,2.755),(next_t-.01,next_t+.02)]:
  rr=[x for x,qq in selected if low-1e-10<=x['stage_time_s']<=high+1e-10];bodywin.append({'stage_interval_s':[low,high],'saved_rows':len(rr),'main_N2_peak':np.max([x['main_normal_N2']for x in rr],axis=0).tolist()if rr else None,'guide_ticks_gt1':sum(x['guide_normal_N']>1 for x in rr),'hard_ticks_gt1':sum(x['hard_normal_N']>1 for x in rr),'not_deduplicated_contactpoint_count':False})
 source=[ROOT/'run_manual_first_bar_v1.py',ROOT/'MINIHOP_AUDIT_V2/physics_bridge_minihop_rm_v2.py',ROOT/'MINIHOP_AUDIT_V2/contact_grade_v2.py',ROOT/'MANUAL_FIRST_BAR_V1/grade_rows.py',CASE/'config.json',CASE/'result.json',CASE/'SOURCE_MANIFEST.json',ROOT/'reports/R49_FIRST_BAR_CONTACT_FACTS.json',R/'METHOD_PREDECLARED.md',Path(__file__)]
 d={'kind':'NEW_OFFLINE_SINGLE_CASE_R49_CONTACT_CAUSAL_DERIVEDGRADE_NOT_RAW_MEASUREMENT','case':cfg['case_id'],'q_reconstruction':{'configured_integrator':'implicitfast scalar semiimplicit velocity-before-position','application_source_no_runtime_hinge_qwrites_seen':True,'formula':'qstage[k]=qstage[k-1]+dt*drive_vstage[k]','anchors':len(a),'max_abs_error_rad':maxerr,'axis_max_abs_error_rad':abs(a).max(axis=0).tolist(),'predeclared_limit_rad':1e-9,'accepted_as_conditional_NEW_derived_grade':accepted,'wrong_previous_velocity_scheme_error_rad':float(abs(b).max()),'no_postfit_or_anchor_reset':True,'old_R45_q_unknown_unchanged':True},'event_poses':derived,'event_contact_points':contact_surface,'three_windows_only':bodywin,'phase_switches':switches,'gravity_restore_first_control_s':gravity_restore,'wheel_ground_observer_restore_first_control_s':wheel_restore,'guide_relation':'guide before capture/gravity and observer restore; temporal ordering not a general causal proof','guide_identity_point_counts_not_ticks':dict(guide_sides),'firstbar_main_contact_normal_classes_point_counts':dict(firstbar_sides),'guide_physics_ticks':guideticks,'nextbar_physics_ticks_gt1':nextticks,'rebound_rear_cross':inair_rebound,'original_gates':{k:res[k]for k in('complete','proposed_manual_first_bar_clear_stop_v1','guide_contact_physics_ticks','hard_contact_physics_ticks','end_stable_s','conservative_final_robot_all_collision_behind_bar','conservative_front_never_reached_next_bar')},'raw_artifacts_producer_only':[res['trace_artifact'],res['physical_artifact']],'source_small_metadata':[{'path':str(p),'SHA':sha(p),'bytes':p.stat().st_size}for p in source],'newphysics_Git_agents_H5_read_assetsrawhash':False,'GT_offline_only':True,'PH6pending':True}
 new(R/'DETAILS.json',d)
 lines=['# R49 moving-contact causal diagnostic (singleTRAINcase, PH6pending)','',f"可选2k activehinge推导验证：{len(a)}个100Hz同sensor epoch ×4轴，maxerror={maxerr:.17g}rad，预声明1e-9，accepted={accepted}。负对照前一stage速度积分error={abs(b).max():.9g}rad。",'仅条件NEWderived-grade，非原始2kq测量；nominalTrue无D1/D2，source implicitfast/无runtime hinge写；旧R45unknown与所有旧分数不变。','',f"实际trace phase switches见DETAILS；gravity首恢复control={gravity_restore!r}s，wheel/ground首恢复={wheel_restore!r}s。",'|event|stage s|pitch deg|rootPRE z m|FK BODYdrop m|FK worlddrop m|guide N|','|---|---:|---:|---:|---:|---:|---:|']
 for key,v in derived.items():lines.append('|'+ '|'.join(map(str,[key,v['stage_s'],v['pitch_roll_deg'][0],v['root_pre_m'][2],v.get('nominal_FK_body_drop_m'),v.get('nominal_FK_world_drop_m'),v['guide_N']]))+'|')
 lines+=['',f"guide共{guideticks}个physics rows（不是point数），nextbar总法向>1N {nextticks}rows。guide6→ground，firstlanding右轮→firstbar上表面，而非同一个接触/主轮支撑。",'首次guide早于capture/gravity与observer恢复；因此该初次guide不由这些重启触发。仍是观察到的时序，不证明唯一机理。',f"rear-cross={cross}s在firstlanding={landing}s后，rebound而非firstflight：{inair_rebound}。",'phase/target与实际stageq区分；姿态R与rootPRE同stage，postroot另有time不混用。FK passive约束是public名义闭链，不是全部实际2k关节测量，几何不能取代实测contactforce。',f"原localgate={res['proposed_manual_first_bar_clear_stop_v1']}，不改分数、不以guide支持充主轮支持，不以rebound rear-cross冒cleanfirstflight。",'','仅3个关键时间窗口，无279mesh重建/无新gain/无H5数据/无新physics/Git/agent/真实IO；producerSHA引用，无为归档raw重hash。','[DETAILS](<DETAILS.json>) / [预声明](<METHOD_PREDECLARED.md>) / [收据](<RECEIPT.json>)。']
 text='\n'.join(lines)+'\n';assert text.count('\n')<150;(R/'REPORT.md').write_text(text,encoding='utf-8');new(R/'RECEIPT.json',{'status':'BOUNDED_R49_OFFLINE_DERIVEDGRADE_COMPLETE_NOT_NEW_QUALIFICATION','source_script_SHA':sha(Path(__file__)),'details_SHA':sha(R/'DETAILS.json'),'report_SHA':sha(R/'REPORT.md'),'q_reconstruction_accepted':accepted,'anchors':len(a),'max_error_rad':maxerr,'literal_report_plus_receipt_lines':text.count('\n')+1,'newphysics_Git_agents_realIO_H5_assetsrawhash':False,'old_files_modified':False,'PH6pending':True});print(json.dumps({'q':d['q_reconstruction'],'events':{k:{z:x.get(z) for z in('stage_s','root_pre_m','pitch_roll_deg','nominal_FK_body_drop_m','nominal_FK_world_drop_m','guide_N')}for k,x in derived.items()},'originalgates':d['original_gates'],'restores':[gravity_restore,wheel_restore],'report_lines':text.count('\n')+1,'REPORT':str(R/'REPORT.md')},ensure_ascii=False,indent=2,allow_nan=False))
if __name__=='__main__':main()
