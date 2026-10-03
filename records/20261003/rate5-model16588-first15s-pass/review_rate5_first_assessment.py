"""Review the already completed first5 evaluation; never run a simulation."""
import hashlib,json
from pathlib import Path
from datetime import datetime,timedelta,timezone
D=Path(__file__).resolve().parent
reports=D/'intermediate5_actual_reports'
names={k:f'auto_0034_assessment_cap5_white_v2_{k}.json' for k in ('flat','rate','decision')}
raw={k:json.loads((reports/v).read_text()) for k,v in names.items()}
r,dec,flat=raw['rate'],raw['decision'],raw['flat']
assert r['target_rate_rad_s']==dec['cap']==5. and r['profile']==dec['profile']=='white_v2'
assert r['steps']==1500 and r['seconds']==15 and not r['ppo_performed']
assert r['checkpoint']==flat['checkpoint']==dec['checkpoint']['path']
assert r['spin_skill_pass'] and r['spin_skill_pass_legacy_reference'] and r['physical_smoke_pass'] and not r['nonfinite']
assert dec['continue_current_rate'] and dec['current_rate_skill_pass'] and dec['original_rate_skill_pass']
assert dec['original_flat_admission']['eligible_for_mild_dr_trial'] and flat['strict_pass_window'] is False
assert all(g['physical_admission_fraction']==1. for g in dec['original_flat_admission']['groups'])
assert sum(g['count'] for g in dec['original_flat_admission']['groups'])==64
assert r['initial_parameter_audit']['actual_parameters_pass'] and r['final_parameter_audit']['actual_parameters_pass']
assert len(r['alive'])==88 and all(r['alive']) and all(g['spin_skill_fraction']==1. for g in r['groups'])
assert r['geometry_reference_version']=='wheel_link_support_velocity_v2' and not r['geometry_thresholds_changed']
p=r['per_environment'];groups=[]
for g in r['groups']:
 ids=[i for i,gid in enumerate(r['group_ids']) if gid==g['group_id']]
 assert len(ids)==8
 groups.append(dict(group_id=g['group_id'],profile=g['profile'],command_vx=g['vx'],command_yaw=g['wz'],
  count=len(ids),indices=ids,survived=sum(bool(r['alive'][i]) for i in ids),skill_fraction=g['spin_skill_fraction'],
  mean_yaw_rate=g['means']['yaw_rate'],mean_yaw_error=g['means']['yaw_error'],
  maximum={key:max(p[key][i] for i in ids) for key in ('peak_tilt','height_error','delta','d2','left_slip','right_slip','maximum_gap_m','longest_both_low_s','wheel_rating_clip','leg_rating_clip','peak_wheel_speed_rad_s','peak_wheel_applied_torque_nm','stop_yaw_abs')},
  minimum_wheel_mean_fz_N=min(min(p[key][i] for i in ids) for key in ('left_fz','right_fz')),
  guide_base_mean_max_N=max(max(p[key][i] for i in ids) for key in ('guide_force','base_force'))))
pure=[g for g in groups if g['profile']=='spin' and abs(g['command_yaw'])==5.]
assert len(pure)==2 and all(max(g['maximum'][k] for k in ('left_slip','right_slip'))<=.15 for g in pure)
runtime=json.loads((D/'INTERMEDIATE5_RUNTIME_ACTUAL.json').read_text())
z=timezone(timedelta(hours=8))
out=dict(scope='First distinct complete policy single-seed5 pass; not multi-seed, real hardware, or latest checkpoint skill graduation',
 source=dec['checkpoint'],cap=5.,profile='white_v2',rate_seed=r['seed'],flat_seed=flat['seed'],
 different_protocols_not_initial_state_paired=dec['different_protocols_not_a_paired_experiment'],
 report_sha256={names[k]:hashlib.sha256((reports/names[k]).read_bytes()).hexdigest() for k in names},
 original_rate_skill=r['spin_skill_pass'],legacy_rate_skill=r['spin_skill_pass_legacy_reference'],
 original_flat_admission=dec['original_flat_admission'],legacy_strict_pass_window=flat['strict_pass_window'],
 groups=groups,pure5=pure,max_closure_m=r['max_closure_m'],max_mimic_rad=r['max_mimic_rad'],
 latest_runtime=runtime,local_time=datetime.fromtimestamp(runtime['epoch'],z).isoformat(),
 next_training_deadline_local=datetime.fromtimestamp(runtime['status']['trainer_deadline_epoch'],z).isoformat(),
 next_action='Continue current5/white2 until second distinct policy assessment and same-policy two-seed nominal/white2 pairs. Retain rejected6; no production changes or duplicate probes.')
(D/'RATE5_MODEL16588_FIRST_ASSESSMENT_REVIEW.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps(dict(first5_pass=True,pure5=pure,closure_mm=r['max_closure_m']*1000,mimic_rad=r['max_mimic_rad'],runtime_checkpoint=runtime['full_checkpoint'],time=out['local_time'],next_deadline=out['next_training_deadline_local']),ensure_ascii=False,indent=2))
