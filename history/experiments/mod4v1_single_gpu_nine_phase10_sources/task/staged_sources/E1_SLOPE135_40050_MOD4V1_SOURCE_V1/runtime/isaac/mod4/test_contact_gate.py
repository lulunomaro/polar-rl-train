"""Exercise missing load, individual outliers and original retained constraints."""
import copy
from contact_gate import assess
base=dict(seconds=15,steps=1500,nonfinite=False,max_closure_m=.0001,max_mimic_rad=.002,
          spin_skill_pass=False,spin_skill_pass_legacy_reference=False,group_ids=[0]*8,
          groups=[dict(group_id=0,vx=0,wz=6,profile='spin')],alive=[True]*8,first_failure_step=[1500]*8,
          initial_parameter_audit=dict(actual_parameters_pass=True),final_parameter_audit=dict(actual_parameters_pass=True))
values=dict(peak_tilt=2,tilt=1,height_error=.001,delta=.05,d2=.05,maximum_gap_m=.001,longest_both_low_s=.01,
            guide_force=0,base_force=0,wheel_rating_clip=0,leg_rating_clip=0,left_fz=70,right_fz=70,
            yaw_error=.1,speed_error=.01,spin_translation_speed=.05,stop_yaw_abs=0,left_slip=.21,right_slip=.21)
base['per_environment']={k:[v]*8 for k,v in values.items()}
cp={k:[[v,v] for _ in range(8)] for k,v in dict(loaded_samples=10000,valid_ticks=29000,loaded_time_mean_tangent_speed=.1,loaded_impulse_weighted_tangent_speed=.1,longest_loaded_over015_s=.01,mean_normal_force_N=70,max_normal_z_error=0,max_com_link_point_velocity_error=0).items()}
base['substep_contact_readback']=dict(per_environment=cp,callbacks=30000,sampling_s=.0005)
x=assess(base);assert x['pass_'] and not x['original_spin_skill_pass'] and base['spin_skill_pass'] is False
r=copy.deepcopy(base);r['substep_contact_readback']['per_environment']['loaded_samples'][0]=[0,0];r['substep_contact_readback']['per_environment']['loaded_samples'][1]=[0,0];assert not assess(r)['pass_']
r=copy.deepcopy(base);r['substep_contact_readback']['per_environment']['longest_loaded_over015_s'][0][1]=.016;assert not assess(r)['pass_'] and assess(r)['groups'][0]['passing']==7
r=copy.deepcopy(base);r['per_environment']['spin_translation_speed']=[.13]*8;assert not assess(r)['pass_']
r=copy.deepcopy(base);r['substep_contact_readback']['per_environment']['loaded_impulse_weighted_tangent_speed'][0][1]=float('nan');r['substep_contact_readback']['per_environment']['loaded_impulse_weighted_tangent_speed'][1][1]=.2;assert not assess(r)['pass_']
r=copy.deepcopy(base);r['substep_contact_readback']['per_environment']['valid_ticks'][0][0]=28999;r['substep_contact_readback']['per_environment']['valid_ticks'][1][0]=28999;assert not assess(r)['pass_']
r=copy.deepcopy(base);r['per_environment']['yaw_error'][0]=float('nan');assert not assess(r)['pass_'] and assess(r)['groups'][0]['passing']==7
r=copy.deepcopy(base);r['substep_contact_readback']['per_environment']['mean_normal_force_N'][0][0]=1;assert not assess(r)['pass_'] and assess(r)['groups'][0]['passing']==7
print('Eight acceptance contract checks passed: old booleans preserved, missing load fails, sustained single-env veto, XY constraint, NaN/mean limit, incomplete prefix, one nonfinite sample veto, force-readback mismatch veto.')
