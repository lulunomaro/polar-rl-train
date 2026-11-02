"""Fixed-chart nominal yaw bias via existing RobustPlant.tmp/full_reduced.
CPU forward/kinematics/mass-matrix math only. ALL step APIs are fail-guarded.
No reset of real plant state or physical rollout, no parent/source modification.
"""
from pathlib import Path
import hashlib,importlib,json,math,sys,traceback
import numpy as np
import mujoco
ROOT=Path(__file__).resolve().parent.parent;OUT=Path(__file__).resolve().parent

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def meta(p):p=Path(p);return {'path':str(p),'bytes':p.stat().st_size,'sha256':sha(p)}
def plain(x):
    if isinstance(x,dict):return {k:plain(v) for k,v in x.items()}
    if isinstance(x,(tuple,list)):return [plain(v) for v in x]
    if isinstance(x,np.ndarray):return x.tolist()
    if isinstance(x,np.generic):return x.item()
    return x

def main():
    target=OUT/'YAW_NOMINAL_BIAS.json';assert not target.exists()
    counts={'mj_forward_calls':0,'physics_step_calls':0}
    original_fwd=mujoco.mj_forward
    def forward(m,d):counts['mj_forward_calls']+=1;return original_fwd(m,d)
    def banned(*args,**kwargs):counts['physics_step_calls']+=1;raise AssertionError('No physics stepping in nominal bias calculation')
    mujoco.mj_forward=forward
    for name in ['mj_step','mj_step1','mj_step2']:setattr(mujoco,name,banned)
    source_paths=[ROOT/'physics_bridge.py',ROOT/'sensor_core.py',ROOT/'nominal_gain_v1.json',ROOT/'MODEL_AUDIT/mod4v1_usd_source_aligned.xml',ROOT.parent/'traditional_control_20261101/full_lqr.py',ROOT.parent/'traditional_control_20261101/control_core.py',ROOT.parent/'traditional_control_20261101/kinematics.py',ROOT.parent/'traditional_control_20261101/dr_components.py',ROOT/'reports/r01_spin_analysis.json',ROOT/'MODEL_AUDIT/MOTOR_PARAMETERS_AUDIT.json']
    sources=[meta(p) for p in source_paths]
    sys.path.insert(0,str(ROOT));bridge=importlib.import_module('physics_bridge');plant=bridge.RobustPlant(step=False)
    gain=json.loads((ROOT/'nominal_gain_v1.json').read_text(encoding='utf-8'))['gain'];q=np.asarray(gain['q'],float);assert q.shape==(7,)
    actual_state_before={'qpos':plant.d.qpos.copy(),'qvel':plant.d.qvel.copy(),'time':float(plant.d.time),'tick_phys':plant.tick_phys}
    speeds=[0.,1.,-1.,.5,-.5,2.,-2.,2.6808081525167085,-2.6808081525167085,4.,-4.,4*math.pi,-4*math.pi]
    rows=[]
    for omega in speeds:
        v=np.zeros(7);v[1]=omega;M,f,B=plant.full_reduced(q.copy(),v)
        tau,residuals,rank,sv=np.linalg.lstsq(B,-f,rcond=None);res=B@tau+f
        vel=plant.tmp.qvel[plant.vids].copy();hi=np.minimum(plant.max_tau,plant.stall*(1-vel/plant.no_load));lo=np.maximum(-plant.max_tau,plant.stall*(-1-vel/plant.no_load))
        bodyR=plant.tmp.xmat[plant.chassis].reshape(3,3);wheel_velocity=[];axes=[]
        for side in ['left','right']:
            wb=plant.m.body(side+'_wheel').id;jp=np.zeros((3,plant.m.nv));jr=jp.copy();mujoco.mj_jacBody(plant.m,plant.tmp,jp,jr,wb)
            world_v=jp@plant.tmp.qvel;body_v=bodyR.T@world_v;wheel_velocity.append(body_v)
            jid=plant.m.joint(side+'_wheel_spin').id;axes.append({'joint':side+'_wheel_spin','axis_local':plant.m.jnt_axis[jid].copy(),'axis_world':plant.tmp.xaxis[jid].copy(),'actuator_gear':plant.m.actuator(side+'_wheel_spin_motor').gear.copy()})
        wheelmid=(np.mean(plant.tmp.xpos[plant.wheels],axis=0)-plant.tmp.xpos[plant.chassis])@bodyR
        rows.append({'yaw_rate_rad_s':omega,'chart_q':q.copy(),'chart_v':v,'tau_lstsq_Nm':tau,'generalized_passive_minus_bias':f,'B':B,'M':M,'lstsq_B_rank':int(rank),'B_singular_values':sv,'generalized_force_residual_Btau_plus_f':res,'mixed_unit_residual_l2_diagnostic_only':float(np.linalg.norm(res)),
                     'residual_x_force_N':float(res[0]),'residual_other_generalized_torques_Nm':res[1:].copy(),'joint_velocity_actuator_order_rad_s':vel,'signed_DC_min_tau_at_current_v_Nm':lo,'signed_DC_max_tau_at_current_v_Nm':hi,'tau_outside_nominal_DC_bounds':(tau<lo)|(tau>hi),
                     'wheel_center_velocity_body_m_s':wheel_velocity,'wheel_joint_axes':axes,'wheelmid_body_m':wheelmid,'tmp_time_s':float(plant.tmp.time)})
        assert plant.tmp.time==0 and plant.tick_phys==0
    by={r['yaw_rate_rad_s']:r for r in rows};zero=by[0.]['tau_lstsq_Nm'];plus=by[1.]['tau_lstsq_Nm'];minus=by[-1.]['tau_lstsq_Nm']
    even=(plus+minus-2*zero)/2;odd=(plus-minus)/2
    fits=[]
    for row in rows:
        w=row['yaw_rate_rad_s'];pred=zero+even*w*w+odd*w;fits.append({'yaw_rate_rad_s':w,'prediction_Nm':pred,'max_abs_fit_error_Nm':float(np.max(abs(pred-row['tau_lstsq_Nm']))),'delta_even_Nm':even*w*w,'delta_odd_Nm':odd*w})
    pzero=by[0.]['generalized_passive_minus_bias'];peven=(by[1.]['generalized_passive_minus_bias']+by[-1.]['generalized_passive_minus_bias']-2*pzero)/2;podd=(by[1.]['generalized_passive_minus_bias']-by[-1.]['generalized_passive_minus_bias'])/2
    motor=json.loads((ROOT/'MODEL_AUDIT/MOTOR_PARAMETERS_AUDIT.json').read_text(encoding='utf-8'));wm=motor['wheel_motor'];lm=motor['leg_motor'];r01=json.loads((ROOT/'reports/r01_spin_analysis.json').read_text(encoding='utf-8'))
    r01rate=r01['tail']['wheel_rates2'];rpmfactor=60/(2*math.pi);ratio=wm['total_gear_ratio'];nl_from_param=wm['no_load_speed_rpm']/rpmfactor;nl_from_slope=wm['envelope_intercept_nm']/wm['envelope_slope_nm_s_rad']
    speed_audit={'wheel_joint_is_output_not_rotor':True,'XML_motor_gear':1.,'rotor_to_wheel_ratio':ratio,'source_controller_no_load_output_rad_s':plant.no_load[[2,5]].copy(),'catalog_scaled_no_load_output_rad_s':nl_from_param,'envelope_metadata_intercept_over_slope_output_rad_s':nl_from_slope,
                 'controller_minus_catalog_noload_relative':float(plant.no_load[2]/nl_from_param-1),'catalog_output_no_load_rpm':wm['no_load_speed_rpm'],'catalog_rotor_no_load_rpm':wm['no_load_speed_rpm']*ratio,
                 'r01_tail_output_rad_s':r01rate,'r01_tail_rotor_rpm':{k:np.asarray(v)*ratio*rpmfactor for k,v in r01rate.items()},'r01_abs_peak_output_fraction_of_controller_noload':float(max(abs(np.array(r01rate['min'])).max(),abs(np.array(r01rate['max'])).max())/plant.no_load[2]),
                 'leg_ratio':lm['gear_ratio_internal'],'leg_output_noload_rad_s':plant.no_load[[0,1,3,4]].copy(),'leg_output_noload_rpm':lm['no_load_speed_rpm'],'leg_rotor_noload_rpm':lm['no_load_speed_rpm']*lm['gear_ratio_internal'],
                 'torque_speed_curve_is_estimated_not_measured':True,'no_load_is_zero_motoring_torque_point_not_absolute_overspeed_hard_limit':True,'R01_wheel_velocity_sign_matches_positive_yaw_geometry':'Both wheel axes +bodyY; +spin implies +bodyX no-slip wheel-center speed. Positive yaw needs left negative/right positive, as observed. This does not prove physical CAN polarity.'}
    assert np.array_equal(plant.d.qpos,actual_state_before['qpos']) and np.array_equal(plant.d.qvel,actual_state_before['qvel']) and plant.d.time==actual_state_before['time'] and plant.tick_phys==actual_state_before['tick_phys']
    assert all(sha(p['path'])==p['sha256'] for p in sources),'A source changed during static calculation'
    unit=by[1.];target4=by[4*math.pi];r01w=float(r01['tail']['true_gyro3']['mean'][2])
    result={'kind':'FIXED_ZERO_YAW_ORIGIN_PIVOT_CHART_NOMINAL_YAW_BIAS_NOT_PHYSICAL_QUALIFICATION','engine':mujoco.__version__,'source_files':sources,'all_source_hashes_unchanged':True,'actuator_order':list(bridge.oldcore.ORDER),'chart_coordinate_order':['root_world_x','yaw','pitch','Lhip','Lcrank_minus_hip','Rhip','Rcrank_minus_hip'],
            'nominal_chart_q':q,'tau0_Nm':zero,'tau_even_per_yawrate_squared_Nm_s2':even,'tau_odd_per_yawrate_Nm_s':odd,'formula':'tau_lstsq(omega)=tau0+tau_even*omega**2+tau_odd*omega; coefficients from omega=0,+1,-1',
            'delta_even_at_R01_actual_yaw_mean_Nm':even*r01w*r01w,'delta_odd_at_R01_actual_yaw_mean_Nm':odd*r01w,'delta_even_at_command_4pi_Nm':even*(4*math.pi)**2,'delta_odd_at_command_4pi_Nm':odd*(4*math.pi),
            'generalized_f0':pzero,'generalized_f_even_per_omega2':peven,'generalized_f_odd_per_omega':podd,'fit_checks':fits,'max_fit_error_Nm':max(x['max_abs_fit_error_Nm'] for x in fits),
            'rows':rows,'speed_and_axis_audit':speed_audit,'physics_steps':0,'physical_rollout_episodes':0,'tmp_only_forward_calls':counts['mj_forward_calls'],'fail_guard_step_calls':counts['physics_step_calls'],'time_advanced_s':0.,'main_plant_state_unchanged':True,
            'application_flags':['FIXED_CHART_APPROX_NOT_NEW_GAIN_OR_STEADY_SPIN_SOLUTION','CHART_ROOT_CHASSIS_ORIGIN_FIXED_XY_NOT_FIXED_WHEELMID_OR_COM','CIRCULAR_SUPPORT_CHART_RADIUS_0637_NOT_EXACT_POLYGON_CONTACT','MASS_MOTION_REDUCTION_EXCLUDES_CONTACT_CONSTRAINT_REACTION_AND_REQUIRES_LATERAL_REFERENCE_CONSISTENCY','LSTSQ_RESIDUAL_REPORTED_NOT_ZERO_ASSUMED','DO_NOT_DOUBLE_COUNT_tau0_IF_GRAVITY_GAS_FF_ALREADY_PRESENT','NO_HARDWARE_ROTOR_MAX_SPEED_OR_THERMAL_QUALIFICATION'],
            'critical_geometry_observation':{'wheelmid_B_at_nominal':unit['wheelmid_body_m'],'wheel_center_velocity_B_per_yaw1':unit['wheel_center_velocity_body_m_s'],'wheel_center_velocity_B_at_command4pi':target4['wheel_center_velocity_body_m_s'],'meaning':'The inherited chart spins the chassis origin at fixed XY. Because wheelmid.x !=0, both wheel centers have nonzero lateral velocity in this chart. This is NOT exact no-lateral-slip rotation about the wheelmid/COM. Bias coefficients are a config experiment template only.'},
            'causal_status_R01_leg_splitting':'Not proven by this static calculation. Fixed-zero-yaw gain/contact/reference mismatch remains a hypothesis supported by observed leg separation, not a closed-loop causal result.',
            'reader_error_preserved':{'operation':'glob','path':str(ROOT/'source_snapshots/r01'),'error':'rg: path does not exist (os error2); no snapshot assumed; actual current source hashes bound above'}}
    target.write_text(json.dumps(plain(result),ensure_ascii=False,indent=2,allow_nan=False),encoding='utf-8')
    print(json.dumps(plain({k:result[k] for k in ['tau0_Nm','tau_even_per_yawrate_squared_Nm_s2','tau_odd_per_yawrate_Nm_s','delta_even_at_R01_actual_yaw_mean_Nm','delta_even_at_command_4pi_Nm','delta_odd_at_command_4pi_Nm','max_fit_error_Nm','critical_geometry_observation','speed_and_axis_audit','physics_steps','tmp_only_forward_calls','main_plant_state_unchanged']}),ensure_ascii=False,indent=2))
if __name__=='__main__':
    try:main()
    except Exception:
        (OUT/'YAW_BIAS_FAILURE_001.txt').write_text(traceback.format_exc(),encoding='utf-8');raise
