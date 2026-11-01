"""User-authorized DR0: all D0-D7 perturbations off;PPO/task sampling retained."""
KIND='E0_ALL_D0_D7_OFF_NOMINAL_DR0_V1'
PROFILE='all_off_nominal_v1'
ENV=dict(RM_ALL_RANDOMIZATION_OFF='1',RM_DR_OFF='1',RM_MILD_DR_PROFILE=PROFILE,
 RM_SENSOR_PROFILE='off',RM_FEEDBACK_DELAY_PROFILE='off',RM_PHYSICS_ACTION_DELAY_PROFILE='off',
 RM_SPRING_PRESSURE_PROFILE='off',RM_GAS_DAMPING_PROFILE='off',RM_CHASSIS_COM_PROFILE='off',RM_EXPLICIT_PD_PROFILE='off',
 RM_OBS_DELAY_MIN_LAG='0',RM_OBS_DELAY_MAX_LAG='0',RM_ACTION_DELAY_MIN_LAG='0',RM_ACTION_DELAY_MAX_LAG='0',
 RM_EFFORT_NOISE='0',RM_EFFORT_NOISE_WHEEL='0',RM_ENCODER_BIAS='0')
NOMINAL=dict(mass_inertia_factor=1.,episode_motor_gain=1.,step_motor_gain=1.,wheel_static_mu=.9,wheel_dynamic_mu=.9,wheel_restitution=0.,
 encoder_bias_rad=0.,feedback_added_delay_us=0,action_added_delay_us=0,gas_stiffness_N_m=[2000.,2000.],gas_damping_Ns_m=[3.,3.],
 chassis_COM_delta_m=[0.,0.,0.],leg_kp=60.,leg_kd=2.,wheel_kp=0.,wheel_kd=.6)

def apply_env(environ):environ.update(ENV)
def validate_snapshot(v,synthetic=False):
 assert v['kind']==KIND and (v['actual_SDK_readback'] is True or synthetic and v.get('synthetic_only') is True)
 for k in ('mass_inertia_authored_baseline','motor_gains_one','wheel_mu_original_nominal09','nonwheel_material_authored_baseline','ground_cfg_unchanged_from_source',
  'sensor_noise_and_bias_off','feedback_added_delay_zero','physical_target_added_delay_zero','gas_stiffness_nominal2000',
  'gas_damping_nominal3','COM_delta_zero_AUTHORED_absolute_preserved','PD_nominal','new_DR0_streams_not_old_DR_restore'):
  assert v[k] is True,k
 assert v['closure_m']==.002 and v['mimic_rad']==.01
 return True

