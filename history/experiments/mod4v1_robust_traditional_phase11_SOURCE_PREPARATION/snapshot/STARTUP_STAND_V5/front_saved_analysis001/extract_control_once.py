"""One exact188-row max V5 control stream read; no project imports/physics/raw SHA. Minimum first, no prose."""
from pathlib import Path
import json,math,hashlib,collections,traceback
O=Path(__file__).resolve().parent;R=O.parents[1];T=R/'results/startup_front065_lift_pose_v5_nominal1/trace.jsonl'
V4=R/'STARTUP_STAND_V4/front_saved_analysis001';COUNTS=O/'READCOUNTS_001.json';MIN=O/'MINIMUM_001.json'
def rec(p):
 b=p.read_bytes();return dict(path=str(p),bytes=len(b),SHA=hashlib.sha256(b).hexdigest())
def save(p,x,mode='w'):
 with p.open(mode,encoding='utf-8',newline='\n')as f:json.dump(x,f,ensure_ascii=False,indent=2,allow_nan=False);f.write('\n')
def vec(x,n,name):
 if not isinstance(x,list)or len(x)!=n or any(type(v)not in(int,float)or not math.isfinite(v)for v in x):raise ValueError('nonfinite/shape '+name)
 return x
def scalar(x,name):
 if type(x)not in(int,float)or not math.isfinite(x):raise ValueError('nonfinite/type '+name)
 return x
def norm(x):return math.sqrt(math.fsum(v*v for v in x))
def clip(x,lo,hi):return min(hi,max(lo,x))
def reject(s):raise ValueError('nonfinite JSON constant '+s)
def main():
 c=json.loads(COUNTS.read_bytes());assert c['trace_opens']==c['trace_rows_read']==0 and not MIN.exists()
 refs=[rec(p)for p in [O/'PARENT_SCOPE.json',O/'METHOD.json',Path(__file__).resolve(),T.parent/'result.json',V4/'RESULT_MIN.json',V4/'REPORT.md']]
 result=json.loads((T.parent/'result.json').read_bytes());old=json.loads((V4/'RESULT_MIN.json').read_bytes());assert result['controls']==188 and result['physics_steps']==3760
 assert Path(result['trace_artifact']['path']).resolve()==T.resolve()
 st=T.stat();assert st.st_size==result['trace_artifact']['bytes'];rows=[];counts=collections.Counter();slots={};intervals=[];error=None;last_state=None;maxerr=0.;maxclock=0.;consistency=0
 minobj=dict(status='MINIMUM_RESERVED_BEFORE_TRACE_OPEN',read_counts=c,source_small_before=refs,source_trace=dict(path=str(T),bytes=st.st_size,mtime_ns=st.st_mtime_ns,producer_SHA_NOT_RECOMPUTED=result['trace_artifact']['SHA']),events=[],counts={})
 save(MIN,minobj,'x');c.update(status='OPEN_RESERVED',trace_opens=1,trace_bytes_read=0,valid_rows=0);save(COUNTS,c)
 def first(name,i,yes):
  if yes and name not in slots:slots[name]=i
 try:
  with T.open('rb')as f:
   for i in range(188):
    b=f.readline()
    if not b:break
    c['trace_rows_read']+=1;c['trace_bytes_read']+=len(b)
    r=json.loads(b,parse_constant=reject);p=r['phase'];t=scalar(r['command_time_s'],'PREtime');post=scalar(r['root_post_s'],'POSTtime')
    maxclock=max(maxclock,abs(t-i*.01),abs(post-t-.01));assert maxclock<1e-7
    x=vec(r['estimated14'],14,'x14');roll=scalar(r['estimated_roll'],'estimatedroll');q=vec(r['encoder_q4'],4,'q');qd=vec(r['encoder_qd4'],4,'qd');w=vec(r['wheel_rate_mean2'],2,'wheelmean');proper=vec(r['raw_proper'],3,'proper');gyro=vec(r['raw_gyro'],3,'gyro');tau=vec(r['requested_tau6'],6,'REQUEST');age=scalar(r['sensor_age_s'],'sourceage');stamp=scalar(r['sensor_time_s'],'sourceepoch')
    assert age>=0 and stamp<=t+1e-7
    g=r['grade_after'];gb=r['grade_before'];truep=scalar(g['pitch_true'],'truePOSTpitch');xyz=vec(g['xyz'],3,'rootPOSTxyz');truepre=scalar(gb['pitch_true'],'truePREpitch')
    assert abs(scalar(g['root_pose_velocity_time_s'],'truePOSTepoch')-post)<1e-7
    gate=p['support_capture_gate_this_command'];active=p['support_capture_active_this_command'];pose=p['lift_pose_branch_on_this_command'];latch=p['support_capture_latched'];current=type(gate)is bool and 'time_s'in p
    phase=p['phase'];is_lift=phase=='LIFT_WORLD_SUPPORT';counts['rows']+=1;counts['phase:'+phase]+=1;counts['feature_timing_flag_TRUE']+=p.get('lift_pose_timing_active')is True;counts['current_published']+=current;counts['source_age_zero']+=age==0
    ref=vec(p['last_published_reference_q4'],4,'lastpubq')if p['last_published_reference_q4']is not None else None
    vr=vec(p['last_published_reference_qd4'],4,'lastpubqd')if p['last_published_reference_qd4']is not None else None
    pub=p['last_published_reference_time_s'];qerr=max(abs(a-b)for a,b in zip(q,ref))if current and ref is not None else None;qdmax=max(map(abs,qd));pnorm=norm(proper)
    measured=dict(qerror_max_rad=qerr,qd_max_rad_s=qdmax,proper_norm_m_s2=pnorm)
    fails=[];fresh_inference='NOT_INDEPENDENTLY_LOGGED'
    if is_lift and current:
     counts['valid_LIFT']+=1;assert ref is not None and vr is not None and abs(pub-t)<1e-8
     if qerr>.08:fails.append('qerror>.08')
     if qdmax>.40:fails.append('qd>.40')
     if not .8*9.81<=pnorm<=1.2*9.81:fails.append('proper_outside_[.8,1.2]g')
     for reason in fails:counts['LIFT_exclusion_component:'+reason]+=1
     if qdmax>.4 and qerr<=.08 and .8*9.81<=pnorm<=1.2*9.81:counts['LIFT_qd_only_failed_among_measured_terms']+=1
     counts['LIFT_gate_TRUE']+=gate is True;counts['LIFT_gate_FALSE']+=gate is False;counts['LIFT_latch_TRUE']+=latch is True;counts['LIFT_pose_request_branch_TRUE']+=pose is True
     if gate is True:
      if fails:raise ValueError('loggedgateTrue conflicts with measured sufficient exclusion')
      fresh_inference='TRUE_FROM_LOGGED_AND_GATE';counts['LIFT_fresh_proven_TRUE_by_gate']+=1
     elif not fails:
      # Three other exact AND terms pass: falsegate implies falsefresh, except near numeric boundary.
      near=min(abs(qerr-.08),abs(qdmax-.40),abs(pnorm-.8*9.81),abs(pnorm-1.2*9.81))<1e-9
      fresh_inference='UNKNOWN_NUMERIC_BOUNDARY'if near else'FALSE_FROM_AND_GATE_WHEN_OTHER_TERMS_PASS'
      counts['LIFT_other_measured_terms_pass_but_gate_FALSE']+=1
     else:counts['LIFT_fresh_unidentified_when_other_term_fails']+=1
     assert type(active)is bool and type(pose)is bool and type(latch)is bool and active==bool(latch and gate)and pose==active
     common=scalar(p['alignment_pose_common_before_damping_Nm'],'posecommon');quiet=[clip(-.30*z,-2.,2.)for z in w];expected=list(quiet);soft=[False,False]
     if pose:
      expected=[clip(common-.30*z,-3.,3.)for z in w]
      for j,z in enumerate(w):
       if abs(z)>12. and expected[j]*z>0:soft[j]=True;expected[j]=clip(-.30*math.copysign(1.,z)*(abs(z)-12.),-3.,3.)
      counts['LIFT_pose_nonzero_common']+=common!=0;counts['LIFT_pose_REQUEST_differs_quiet']+=any(abs(a-b)>1e-12 for a,b in zip([tau[2],tau[5]],quiet))
     er=max(abs(expected[j]-tau[k])for j,k in enumerate([2,5]));maxerr=max(maxerr,er);assert er<=1e-9 and p['alignment_soft_overspeed_limited2']==soft
     counts['LIFT_REQUEST_formula_verified']+=1;counts['LIFT_logged_softspeed_guard_rows']+=any(soft);counts['LIFT_abs_wheel_above12_rows']+=max(map(abs,w))>12.;consistency+=1
    reasons=fails[:]
    if is_lift and current and not gate and not fails:reasons.append(fresh_inference)
    if is_lift and current and gate and not latch:reasons.append('not_latched_initial_wheelquiet')
    if not current:reasons=['NO_CURRENT_PUBLICATION_OR_FAULT']
    if not is_lift and current:reasons=['OUTSIDE_LIFT']
    softlog=p['alignment_soft_overspeed_limited2'];travel=scalar(p['recovery_encoder_travel_m'],'wheelrotationproxy');gamma=p['support_reference_rate_gamma'];h0=p['support_common_unclipped_rad'];h=p['support_common_clipped_rad']
    goalclip=current and h0 is not None and h is not None and abs(h0-h)>1e-12
    counts['current_goal_clipped']+=goalclip;counts['current_gamma_limited']+=current and gamma is not None and gamma<1.-1e-12
    counts['bins_both_main_all20']+=r['both_support_every_2k_sample']is True;counts['bins_no_other_all20']+=r['no_other_contact_in_control']is True
    counts['bins_both_and_no_other_all20']+=r['both_support_every_2k_sample']is True and r['no_other_contact_in_control']is True
    out=dict(row=i,PRE_command_s=t,POST_root_s=post,phase=phase,current_publication=current,fault=p.get('fault_reason'),feature_timing_flag=p.get('lift_pose_timing_active'),logged_gate=gate,logged_latch=latch,logged_pose_active=active,logged_pose_branch_request=pose,gate_component_metrics=measured,measured_exclusion_terms=reasons,fresh_condition_inference=fresh_inference,sensor_source_s=stamp,sensor_age_s=age,estimated_PRE_pitch_rad=x[2],estimated_PRE_pitch_rate_sourceheld_rad_s=x[9],estimated_PRE_roll_rad=roll,raw_mean_gyro3=gyro,encoder_q4=q,encoder_qd4=qd,source_wheel_mean2=w,published_reference_q4=ref,published_reference_qd4=vr,published_reference_time_s=pub,reference_current_not_lastvalid_stale=current,goal_unclipped_h=h0,goal_clipped_h=h,reference_gamma=gamma,wheel_pose_common_before_damping_Nm=p['alignment_pose_common_before_damping_Nm'],softspeed_logged2=softlog,wheel_rotation_proxy_m=travel,preclip_REQUEST6=p['recovery_preclip_tau6_Nm'],actual_REQUEST6=tau,true_PRE_pitch_rad=truepre,true_POST_pitch_rad=truep,true_POST_roll_rad=g['roll_true'],true_POST_rootXYZ_m=xyz,private_bin_both_main_all20=r['both_support_every_2k_sample'],private_bin_no_other_all20=r['no_other_contact_in_control'],private_main_min_N2=r['main_contact_min_N2'],actual_applied_DC_motor_tau=None,contact_identity_or_clipping_stage=None)
    rows.append(out);c['valid_rows']+=1
    first('boot',i,i==0);first('first_LIFT',i,is_lift);first('first_logged_gate_TRUE',i,is_lift and current and gate is True);first('first_latched',i,latch is True);first('first_pose_REQUEST',i,is_lift and current and pose is True)
    first('first_current_gate_FALSE_after_pose',i,is_lift and current and not gate and 'first_pose_REQUEST'in slots)
    first('first_LIFT_qd_above_point4',i,is_lift and current and qdmax>.4);first('first_goal_clip',i,goalclip);first('first_gamma_limit',i,current and gamma is not None and gamma<1.-1e-12)
    first('first_logged_softspeed_guard',i,current and isinstance(softlog,list)and any(softlog));first('first_proxy_ge_point1',i,travel>=.1);first('first_proxy_ge_point25',i,travel>=.25)
    if current:slots['last_valid']=i
    if not current:slots['last_guard_or_no_current']=i
    state=(phase,pose,gate,tuple(reasons))
    if state!=last_state:intervals.append(dict(first_row=i,last_row=i,PRE_begin=t,PRE_end=t,phase=phase,pose=pose,gate=gate,reason_terms=reasons))
    else:intervals[-1].update(last_row=i,PRE_end=t)
    last_state=state
   assert c['trace_rows_read']==c['valid_rows']==188 and c['trace_bytes_read']==st.st_size
 except Exception:
  error=traceback.format_exc();(O/'EXTRACTION_ERROR_001.txt').write_text(error,encoding='utf-8')
 finally:
  c.update(status='ERROR_PREFIX_SAVED'if error else'ONE_TRACE_COMPLETE',current_rows_in_memory=len(rows),raw_hashes_recomputed=0,physics_raw_opens=0,old_V4_trace_opens=0,other_raw_opens=0);save(COUNTS,c)
 priority=['last_guard_or_no_current','last_valid','first_pose_REQUEST','first_logged_gate_TRUE','first_latched','first_current_gate_FALSE_after_pose','first_LIFT_qd_above_point4','first_goal_clip','first_gamma_limit','first_logged_softspeed_guard','first_proxy_ge_point1','first_proxy_ge_point25','first_LIFT','boot']
 selected={}
 for label in priority:
  if label in slots and (slots[label]in selected or len(selected)<12):selected.setdefault(slots[label],[]).append(label)
 for i in [0,31,50,75,100,125,150,175,186,187]:
  if len(selected)>=8:break
  if i<len(rows):selected.setdefault(i,[]).append('deterministic_context_not_new_trigger')
 events=[dict(tags=selected[i],**rows[i])for i in sorted(selected)]
 post=T.stat();refafter=[rec(Path(x['path']))for x in refs];assert refafter==refs
 minobj.update(status='ERROR_VALID_PREFIX_ONLY'if error else'SAVED_ONE_V5_CONTROL_TRACE_MINIMUM_BEFORE_PROSE',read_counts=c,source_small_after=refafter,source_small_SHA_unchanged=True,source_trace_post_stat=dict(bytes=post.st_size,mtime_ns=post.st_mtime_ns),trace_stat_unchanged=(post.st_size,post.st_mtime_ns)==(st.st_size,st.st_mtime_ns),counts=dict(counts),first_and_last_event_rows=slots,events=events,event_count=len(events),control_phase_gate_reason_intervals=intervals,max_REQUEST_formula_error_Nm=maxerr,LIFT_formula_verified_rows=consistency,max_clock_residual_s=maxclock,error=error,
  ranges=dict(sensor_age_s=[min([x['sensor_age_s']for x in rows],default=None),max([x['sensor_age_s']for x in rows],default=None)],max_abs_REQUEST6=[max([abs(x['actual_REQUEST6'][j])for x in rows],default=None)for j in range(6)],max_abs_source_wheel2=[max([abs(x['source_wheel_mean2'][j])for x in rows],default=None)for j in range(2)],max_wheel_rotation_proxy_m=max([x['wheel_rotation_proxy_m']for x in rows],default=None),max_true_abs_pitch_POST_rad=max([abs(x['true_POST_pitch_rad'])for x in rows],default=None)),
  original_result_selected={k:result[k]for k in ['complete','stop','controls','physics_steps','controller_fault_reason','first_BALANCE_command_s','end_stable_s','body_height_gain_m','max_root_xy_displacement_m','startup_stand_original_v1_gate','guide_contact_ticks_whole_episode','hard_contact_ticks_whole_episode']},
  old_V4_saved_only_selected={k:old[k]for k in ['controls','physics_steps','phase_counts','original_gate','capture_eligible_ever','max_requested_tau6_Nm','max_wheel_rate2_rad_s','body_height_gain_m','max_root_xy_displacement_m','final_true_pitch_POST_rad','bins_both_main_all20','bins_no_guide_or_hard_all20']},
  unknowns=['Fresh subcondition not independently logged except Boolean AND inference; failures overlap, not unique causes.','Actual2k applied/current/DC masks/torque/speedbox/contact identity/impact not in this selected control stream.','Actual leg trajectory changed with feedback; same algorithm is not same realized qref or isolated wheel direct causality.','Time: sensor PRE vs source-window rates, root POST+10ms, private20sample interval; no contact/torque instantaneous reconstruction.'])
 save(MIN,minobj)
 print(json.dumps(dict(status=minobj['status'],rows=len(rows),event_count=len(events),counts=dict(counts),slots=slots,formula_max_error=maxerr,minimum=rec(MIN)),ensure_ascii=False))
 if error:raise SystemExit(1)
if __name__=='__main__':main()
