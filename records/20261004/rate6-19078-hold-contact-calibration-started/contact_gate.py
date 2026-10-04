"""Prospective project contact gate. Original report booleans remain unchanged.

No SCUT graduation or real-hardware claim. The 0.15m/s speed is retained but
measured on loaded reported contact points, with explicit sustained-excess veto.
"""
import math
VERSION='loaded_report_point015_duration15ms_v1'
LIMIT=.15
MAX_SUSTAINED_S=.01501
def assess(report):
    pe=report['per_environment'];sub=report.get('substep_contact_readback')
    if not sub:
        return dict(version=VERSION,pass_=False,reasons=['Missing substep contact evidence'],original_spin_skill_pass=report.get('spin_skill_pass'))
    cp=sub['per_environment'];groups=[];individual=[];severe=[]
    complete=(report['seconds']>=15 and not report['nonfinite'] and report['max_closure_m']<=.002 and report['max_mimic_rad']<=.01
              and sub['callbacks']==report['steps']*20 and sub['sampling_s']==.0005)
    for g in report['groups']:
        ids=[i for i,v in enumerate(report['group_ids']) if v==g['group_id']];passing=[]
        for i in ids:
            reasons=[]
            limits=dict(peak_tilt=12,tilt=8,height_error=.03,delta=.18,d2=.25,maximum_gap_m=.002,
                        longest_both_low_s=.01501,guide_force=1,base_force=1,wheel_rating_clip=.2,leg_rating_clip=.2)
            for key,limit in limits.items():
                if not math.isfinite(pe[key][i]) or pe[key][i]>limit:reasons.append(key)
            if not report['alive'][i] or report['first_failure_step'][i]<report['steps']:reasons.append('survival')
            if pe['left_fz'][i]<10 or pe['right_fz'][i]<10:reasons.append('mean_wheel_load')
            if pe['yaw_error'][i]>max(.2,.2*abs(g['wz'])):reasons.append('yaw_error')
            if pe['speed_error'][i]>max(.12,.25*abs(g['vx'])):reasons.append('speed_error')
            if g['wz']!=0 and pe['spin_translation_speed'][i]>.12:reasons.append('spin_translation_speed')
            if g['profile']=='spin_ramp_stop_reverse' and pe['stop_yaw_abs'][i]>.2:reasons.append('stop_yaw_abs')
            for w in (0,1):
                if cp['loaded_samples'][i][w]<=0 or cp['valid_ticks'][i][w]!=(report['steps']-50)*20:reasons.append(f'wheel{w}_missing_contact')
                for key in ('loaded_time_mean_tangent_speed','loaded_impulse_weighted_tangent_speed'):
                    value=cp[key][i][w]
                    if not math.isfinite(value) or value>LIMIT:reasons.append(f'wheel{w}_{key}')
                value=cp['longest_loaded_over015_s'][i][w]
                if not math.isfinite(value) or value>MAX_SUSTAINED_S:
                    reasons.append(f'wheel{w}_sustained_loaded_excess');severe.append(dict(env=i,wheel=w,reason='sustained_loaded_excess',value_s=value))
            if not report['alive'][i] or pe['peak_tilt'][i]>15 or pe['longest_both_low_s'][i]>.02001:severe.append(dict(env=i,reason='original_severe_individual_veto'))
            accepted=not reasons;passing.append(accepted)
            individual.append(dict(env=i,group_id=g['group_id'],pass_=accepted,reasons=reasons,
                                   original_left_mesh_proxy=pe['left_slip'][i],original_right_mesh_proxy=pe['right_slip'][i]))
        groups.append(dict(group_id=g['group_id'],count=len(ids),passing=sum(passing),fraction=sum(passing)/len(ids)))
    audits=all((report.get(k) or {}).get('actual_parameters_pass',False) for k in ('initial_parameter_audit','final_parameter_audit'))
    passed=complete and audits and not severe and all(g['fraction']>=.8 for g in groups)
    return dict(version=VERSION,pass_=bool(passed),complete_evidence=complete,actual_parameters_pass=audits,
                original_spin_skill_pass=report['spin_skill_pass'],legacy_spin_skill_pass=report.get('spin_skill_pass_legacy_reference'),
                original_mesh015_replaced_only_in_new_version=True,groups=groups,individual=individual,severe_individual_veto=severe,
                mean_tangent_speed_limit_m_s=LIMIT,sustained_loaded_excess_limit_s=MAX_SUSTAINED_S,
                scope='Prospective project gate using post-step report-point velocities. Not material-patch tracking or real-robot certification; raw peaks/RMS retained.')
