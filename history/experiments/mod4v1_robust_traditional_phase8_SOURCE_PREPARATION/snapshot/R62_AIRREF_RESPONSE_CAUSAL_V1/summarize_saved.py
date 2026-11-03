"""Inspect saved EXTRACTED only; never opens a raw trace or physics file."""
from pathlib import Path
import json,math
OUT=Path(__file__).resolve().parent;ROOT=OUT.parent
E=json.loads((OUT/'EXTRACTED.json').read_bytes());COLS=E['control_columns'];D=lambda r:dict(zip(COLS,r))
summary=dict(kind='SAVED_SINGLE_PASS_R62_RESPONSE_SUMMARY_NOT_UNIQUE_CAUSE',raw_rows=E['total_rows'],raw_streams=len(E['raw_opened']),raw_hashes_recomputed=0,paired_prefix=E['paired_prefix'],cases={})
for c,a in E['cases'].items():
    s=a['summary'];rr=[D(r)for r in a['retained_rows']];fl=[r for r in rr if r['phase']=='predicted_flight_retract'];selected=[]
    for off in [0.,.02,.05,.09,.10,.20,.24]:
        r=min(fl,key=lambda r:abs(r['command_s']-s['first_flight_s']-off))
        if r['k']not in {q['k']for q in selected}:selected.append(r)
    selected.append(D(s['first_capture']))
    def slim(r):return{k:r[k]for k in ['command_s','sensor_s','age_s','phase','pitch_est','pitchrate_est','goal_h','h','anchor','flight_target_q4','landing_ref_q4','request_leg4','request_wheel2','flight_unclip_leg4','samepacket_noh_clipped_leg4','landing_weight','observer_disabled','true_pitch_before']}
    fullmask=[r['command_s']for r in fl if s['new_air_ref']and all(abs(r['request_leg4'][i]-r['samepacket_noh_clipped_leg4'][i])<=1e-9 for i in range(4))]
    metric={k:s[k]for k in ['new_air_ref','rows','first_flight_s','last_flight_s','first_capture_s','observer_resume_s','flight_rows','flight_request_reconstruction_max_error_Nm','flight_leg_reconstruction_max_error_Nm','flight_request_validation_failures','flight_goal_h_target_validation_max_error_rad','first_anchor_continuity_error_rad','raw_goal_clipped_low','raw_goal_clipped_high','h_rate_active_rows','h_at_low_rows','h_at_high_rows','effect_nonzero_per_axis','fully_masked_per_axis','partially_masked_per_axis','transmitted_per_axis','flight_unclip_over40_per_axis','phase_requests','masking_interpretation','capture_windows']}
    metric.update(first_flight=slim(D(s['first_flight'])),last_flight=slim(D(s['last_flight'])),first_capture=slim(D(s['first_capture'])),selected_flight_to_anchor=[slim(r)for r in selected],all_four_legs_fully_masked_command_s=fullmask,
        flight_wheel_mean2=[math.fsum(r['request_wheel2'][j]for r in fl)/len(fl)for j in range(2)])
    r=json.loads((ROOT/'results'/c/'result.json').read_bytes());bb=r['final_private_collision_bounds'];bar=r['first_transverse_bar']
    metric['old_result_unchanged_facts']=dict(original_gate=r['proposed_manual_first_bar_clear_stop_v1'],guide_ticks=r['guide_contact_physics_ticks'],hard_ticks=r['hard_contact_physics_ticks'],root_final_xyz=r['final_grade']['xyz'],final_pitch=r['final_grade']['pitch_true'],final_roll=r['final_grade']['roll_true'],final_velocity=r['final_grade']['body_velocity'],conservative_min_x=bb['min_xyz_m'][0],bounds_stage_s=bb['stage_time_s'],bar_back_x=bar['back_x_m'],conservative_margin_m=bb['min_xyz_m'][0]-bar['back_x_m'],actual_main_rear_x=bb['exact_main_rear_x_m'])
    summary['cases'][c]=metric
P=E['new4606_physics'];summary['new4606_physics']=P
summary['pair_request_differences']={}
for seed in[4606,4610]:
    old=E['cases'][f'r60_tall0_fresh_RM_DR_{seed}'];new=E['cases'][f'r62_airref002_paired_RM_DR_{seed}']
    aa={r[1]:D(r)for r in old['retained_rows']};bb={r[1]:D(r)for r in new['retained_rows']};first={}
    for t in sorted(aa.keys()&bb.keys()):
        if aa[t]['phase']!='predicted_flight_retract':continue
        for key in ['pitch_est','pitchrate_est','flight_target_q4','request_leg4','request_wheel2']:
            if key not in first and aa[t][key]!=bb[t][key]:first[key]=dict(command_s=t,old=aa[t][key],new=bb[t][key])
    summary['pair_request_differences'][str(seed)]=dict(first_observed_numeric_difference_within_flight=first,not_same_packet_after_state_divergence=True)
summary['unknowns']=['No2k actual q: do not integrate dq or use nominal recursion under D1/D2.','No same-stage actual torque for old4606/old4610/new4610 from selected traces; new4606 private actual_tau is model bounded d.ctrl not independently measured force.','No separate push +/-32 pre-roll, inversePD target, D4 input, raw driver PD, motorGain or signedDC clipmask stage logs; those clip-event counts UNKNOWN.','Per-request h masking is validated algebraic sensitivity at SAME recorded packet, not a replay of the old trajectory or unique cause of final outcomes.','The final bound is a conservative compiled-rbound envelope; a failed bound gate is not an observed true-shape collision.']
with(OUT/'SUMMARY.json').open('x',encoding='utf-8',newline='\n')as f:json.dump(summary,f,ensure_ascii=False,allow_nan=False,separators=(',',':'));f.write('\n')
print(json.dumps(dict(cases={c:dict(first=m['first_flight'],last=m['last_flight'],capture=m['first_capture'],flight_limits=m['phase_requests']['predicted_flight_retract'],all4masked=m['all_four_legs_fully_masked_command_s'],h_limits=[m['h_at_low_rows'],m['h_at_high_rows']],wheelmeanflight=m['flight_wheel_mean2'],wheelmeancap0p2=m['capture_windows']['first_0p2']['request_wheel_mean2'],old_result=m['old_result_unchanged_facts'])for c,m in summary['cases'].items()},new4606_hard=P['hard_events'],new4606_window=P['first_hard_window'],firstdifferences=summary['pair_request_differences']),indent=2,allow_nan=False))
