import argparse,copy,json,sys
from pathlib import Path
def main():
 p=argparse.ArgumentParser();p.add_argument('--reports',required=True);a=p.parse_args()
 from scut_curriculum_gate_v4 import assess,assess_flat,evidence,fullscale,target_evidence,VERSION
 folder=Path(a.reports);checks=[]
 def check(name,ok):
  assert ok,name
  checks.append(name)
 def load(stem):return json.loads((folder/stem).read_text())
 r=load('auto_0087_scut_style_v2_assessment_cap7_white_v2_rate.json')
 f=load('auto_0087_scut_style_v2_assessment_cap7_white_v2_flat.json')
 s=load('auto_0090_rate7_transition_short_cap8_white_v2.json')
 big=load('auto_0091_rate7_transition_physics_cap8_white_v2_20k.json')
 before=copy.deepcopy(r)
 check('existing7: actual hard evidence passes',assess(r)['pass_'])
 check('existing flat evidence passes',assess_flat(f)['pass_'])
 check('original raw and failure booleans unchanged',r==before and r['spin_skill_pass'] is False)
 for key,value in [('yaw_error',100),('speed_error',1),('tilt',20),('peak_tilt',35),('height_error',.1),('delta',1),('d2',2),('maximum_gap_m',.05),('longest_both_low_s',.04),('left_fz',2),('right_fz',2),('guide_force',2),('base_force',2),('wheel_rating_clip',.8),('leg_rating_clip',.8),('spin_translation_speed',.5),('stop_yaw_abs',2),('left_slip',1),('right_slip',1)]:
  x=copy.deepcopy(r);x['per_environment'][key]=[value]*len(r['alive'])
  if key in ('left_fz','right_fz'):
   w=int(key=='right_fz')
   for row in x['substep_contact_readback']['per_environment']['mean_normal_force_N']:row[w]=value
  check('finite quality diagnostic: '+key,assess(x)['pass_'])
 for key in ('loaded_time_mean_tangent_speed','loaded_impulse_weighted_tangent_speed','longest_loaded_over015_s'):
  x=copy.deepcopy(r);x['substep_contact_readback']['per_environment'][key][0][0]=10
  check('loaded numeric diagnostic: '+key,assess(x)['pass_'])
 for key in ('yaw_error','speed_error','peak_tilt','left_slip','delta'):
  for bad in (float('nan'),float('inf')):
   x=copy.deepcopy(r);x['per_environment'][key][0]=bad
   check('nonfinite rejects: '+key+str(bad),not assess(x)['pass_'])
 x=copy.deepcopy(r);x['alive'][0]=False
 check('actual task failure rejects',not assess(x)['pass_'])
 x=copy.deepcopy(r);x['first_failure_step'][0]=100
 check('censored failure rejects',not assess(x)['pass_'])
 for key in ('max_closure_m','max_mimic_rad'):
  x=copy.deepcopy(r);x[key]=.1;check('model integrity rejects '+key,not assess(x)['pass_'])
 for key in ('callbacks','sampling_s'):
  x=copy.deepcopy(r);x['substep_contact_readback'][key]=0;check('capture rejects '+key,not assess(x)['pass_'])
 for key,value in [('valid_ticks',1),('loaded_samples',0),('max_normal_z_error',.011),('max_com_link_point_velocity_error',.002),('mean_normal_force_N',100000)]:
  x=copy.deepcopy(r);x['substep_contact_readback']['per_environment'][key][0][0]=value
  check('contact evidence rejects '+key,not assess(x)['pass_'])
 x=copy.deepcopy(r);x['initial_parameter_audit']['actual_parameters_pass']=False
 check('parameter rejects',not assess(x)['pass_'])
 x=copy.deepcopy(r);del x['per_environment']['yaw_rate']
 check('missing observation rejects',not assess(x)['pass_'])
 x=copy.deepcopy(r);x['per_environment']['left_fz']=[]
 check('malformed observation fails closed',not assess(x)['pass_'])
 for key in ('vel_error','tilt','max_tilt','height_error','delta','d2','guide_force','base_force','left_support_slip_control','longest_both_low_force_s_substep','left_gap_max_control_m','stop_abs_speed'):
  x=copy.deepcopy(f);x['per_environment'][key]=[2.]*len(x['per_environment']['alive'])
  check('flat finite quality diagnostic '+key,assess_flat(x)['pass_'])
 x=copy.deepcopy(f);x['resets']=1;check('flat actual reset rejects',not assess_flat(x)['pass_'])
 x=copy.deepcopy(f);x['per_environment']['alive'][0]=False;check('flat actual failure rejects',not assess_flat(x)['pass_'])
 x=copy.deepcopy(f);x['per_environment']['vel_error'][0]=float('nan');check('flat NaN rejects',not assess_flat(x)['pass_'])
 check('short8 integrity passes',evidence(s,'spin',3)['pass_'])
 check('short is not15s proof',not assess(s)['pass_'])
 check('fullscale short-height original false retained',not big['pass'] and fullscale(big)['pass_'])
 x=copy.deepcopy(big);x['max_tilt_deg']=35;x['max_height_error_m']=.15
 check('fullscale quality is diagnostic',fullscale(x)['pass_'])
 x=copy.deepcopy(big);x['terminations']=1;check('fullscale actual failure rejects',not fullscale(x)['pass_'])
 x=copy.deepcopy(big);x['max_closure_m']=.003;check('fullscale closure rejects',not fullscale(x)['pass_'])
 x=copy.deepcopy(big);x['mild_final_parameters']['actual_parameters_pass']=False;check('fullscale material rejects',not fullscale(x)['pass_'])
 check('target cap registration alone does not confirm2rps',not target_evidence(r,4*__import__('math').pi)['pass_'])
 check('actual7 signed tracking separate from learning gate',target_evidence(r,7)['pass_'])
 print(json.dumps(dict(pass_=True,count=len(checks),checks=checks,acceptance_version=VERSION)))
if __name__=='__main__':main()
