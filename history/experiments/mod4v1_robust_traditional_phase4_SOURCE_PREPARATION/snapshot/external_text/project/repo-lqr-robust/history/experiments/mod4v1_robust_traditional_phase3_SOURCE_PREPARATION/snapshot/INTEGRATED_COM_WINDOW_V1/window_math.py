"""Finite COM window identity, no alpha/qdd input and no physics/SDK.
Exact for specified continuous signals; box-model integral exact ONLY for its
piecewise-constant omega/f model. Missing capture transport is budgeted outside.
"""
from dataclasses import dataclass
import math
import numpy as np

def v3(x):
    a=np.asarray(x,float)
    if a.shape!=(3,) or not np.isfinite(a).all():raise ValueError('finite3vector')
    return a

def skew(x):
    x,y,z=v3(x);return np.array([[0,-z,y],[z,0,-x],[-y,x,0.]])

def exp_rotation(omega,dt):
    w=v3(omega);K=skew(w);n=float(np.linalg.norm(w));theta=n*dt
    if not math.isfinite(dt) or dt<0:raise ValueError('finite positive duration')
    if abs(theta)<1e-7:return np.eye(3)+dt*K+.5*dt*dt*(K@K)+(dt**3/6)*(K@K@K)
    return np.eye(3)+math.sin(theta)/n*K+(1-math.cos(theta))/(n*n)*(K@K)

def integrated_rotation(omega,dt):
    w=v3(omega);K=skew(w);n=float(np.linalg.norm(w));theta=n*dt
    if not math.isfinite(dt) or dt<=0:raise ValueError('duration')
    if abs(theta)<1e-4:
        return dt*np.eye(3)+.5*dt*dt*K+(dt**3/6)*(K@K)+(dt**4/24)*(K@K@K)+(dt**5/120)*(K@K@K@K)
    return dt*np.eye(3)+(1-math.cos(theta))/(n*n)*K+(theta-math.sin(theta))/(n**3)*(K@K)

def relative_velocity(omega,r_COM,rDot_COM,lever):return np.cross(v3(omega),v3(r_COM)-v3(lever))+v3(rDot_COM)

def piecewise_constant_window(omega_bins,fIMU_bins,durations,u_start,u_end):
    """BODY vectors perbin; relative R0=I. Output is average in window-start B.
    No gravity constant, no alpha/qdd and no world yaw/attitude arguments.
    """
    omega=np.asarray(omega_bins,float);f=np.asarray(fIMU_bins,float);h=np.asarray(durations,float)
    if omega.ndim!=2 or omega.shape[1]!=3 or f.shape!=omega.shape or h.shape!=(len(f),) or not np.isfinite(omega).all() or not np.isfinite(f).all() or not np.isfinite(h).all() or np.any(h<=0):raise ValueError('bin shape/finite/duration')
    T=float(h.sum());R=np.eye(3);force=np.zeros(3);sum_rot=np.zeros((3,3));rot_start=[]
    for w,a,dt in zip(omega,f,h):
        rot_start.append(R.copy());S=integrated_rotation(w,float(dt));force+=R@S@a;sum_rot+=R@S;R=R@exp_rotation(w,float(dt))
    boundary=(R@v3(u_end)-v3(u_start))/T;average=force/T+boundary
    return {'average_COM_proper_start_frame3':average,'force_transport_average3':force/T,'velocity_boundary_average3':boundary,'R_relative_end':R,'R_bin_starts':rot_start,'integral_R_model':sum_rot,'T_s':T,'nominal_midpoint_age_s':T/2,'exact_for_declared_box_model_not_actual_capture_correlation':True}

def point_series_window(omega_points,fIMU_points,h,u_start,u_end):
    """Synthetic pointseries reference: midpoint gyro Lie steps, Simpson fW.
    Constant omega is integrated exactly; variable gyro has numerical truncation.
    """
    w=np.asarray(omega_points,float);f=np.asarray(fIMU_points,float)
    if w.ndim!=2 or w.shape[1]!=3 or f.shape!=w.shape or len(w)<3 or (len(w)-1)%2:raise ValueError('Simpson needs even interval count')
    R=np.eye(3);transport=[f[0].copy()]
    for i in range(1,len(w)):
        R=R@exp_rotation((w[i]+w[i-1])*.5,h);transport.append(R@f[i])
    y=np.asarray(transport);integral=h/3*(y[0]+y[-1]+4*y[1:-1:2].sum(axis=0)+2*y[2:-1:2].sum(axis=0));T=h*(len(w)-1)
    return {'average_COM_proper_start_frame3':integral/T+(R@v3(u_end)-v3(u_start))/T,'R_relative_end':R,'T_s':T,'nominal_midpoint_age_s':T/2}

@dataclass(frozen=True)
class BudgetAssumptions:
    gyro_axis_noise_rad_s: float=.125
    q_axis_noise_rad: float=.005
    qd_axis_noise_rad_s: float=.25
    proper_axis_noise_m_s2: float=.025*9.81
    wheel_axis_rate_noise_rad_s: float=.5
    angular_rate_slope_axis_rad_s2: float=50.
    joint_rate_slope_axis_rad_s2: float=100.
    proper_BODY_slope_axis_m_s3: float=50.
    wheel_rate_slope_abs_rad_s2: float=5000.
    encoder_zero_allowance_axis_rad: float=.01
    nominal_COM_position_error_norm_m: float=.005
    nominal_COM_velocity_error_norm_m_s: float=.02
    lever_position_error_norm_m: float=.0005
    local_COM_Jacobian_Lipschitz_m_rad2: float=1.
    relative_leg_angular_rate_abs_rad_s: float=100.
    mean_endpoint_age_s: float=.00525
    mean_abs_bin_time_distance_s: float=.0033375
    assumed_input_confidence_cap: float=.50
    frozen_cue_min_confidence: float=.60
    freefall_max_g: float=.25
    nonfreefall_min_g: float=.60

class EndpointModel:
    """Read-only public31body geometry; no qdd/alpha computation or input."""
    def __init__(self,geometry,lever=(.03,0.,.04),assumptions=BudgetAssumptions()):self.g=geometry;self.lever=v3(lever);self.a=assumptions
    def evaluate(self,q4,qd_mean4,omega_mean3,wheel_rate_mean2):
        a=self.a;q=np.asarray(q4,float);v=np.asarray(qd_mean4,float);w=v3(omega_mean3);spin=np.asarray(wheel_rate_mean2,float)
        r=self.g.com(q,[0.,0.]);J,W=self.g.jacobians(q,[0.,0.]);rd=J@v+W@spin;u=relative_velocity(w,r,rd,self.lever)
        qe=np.ones(4)*(a.q_axis_noise_rad+a.encoder_zero_allowance_axis_rad);ve=np.ones(4)*(a.qd_axis_noise_rad_s+a.joint_rate_slope_axis_rad_s2*a.mean_endpoint_age_s)
        we=math.sqrt(3)*(a.gyro_axis_noise_rad_s+a.angular_rate_slope_axis_rad_s2*a.mean_endpoint_age_s);qnorm=float(np.linalg.norm(qe));column=np.linalg.norm(J,axis=0)
        wheel_r=wheel_v=0.;wheel_details=[]
        for i,wh in enumerate(self.g.wheels):
            mr=wh['weight']*wh['radial_radius_m'];rate_error=a.wheel_axis_rate_noise_rad_s+a.wheel_rate_slope_abs_rad_s2*a.mean_endpoint_age_s
            position=2*mr;velocity=position*(a.relative_leg_angular_rate_abs_rad_s+abs(spin[i])+rate_error)+mr*rate_error;wheel_r+=position;wheel_v+=velocity
            wheel_details.append({'nominal_radial_eccentricity_m':wh['radial_radius_m'],'COM_position_fullphase_error_m':position,'COM_velocity_missing_error_m_s':velocity,'rate_error_bound_rad_s':rate_error,'not_actual_balance_calibration':True})
        re=float(column@qe)+.5*a.local_COM_Jacobian_Lipschitz_m_rad2*qnorm*qnorm+a.nominal_COM_position_error_norm_m+wheel_r
        rde=float(column@ve)+a.local_COM_Jacobian_Lipschitz_m_rad2*qnorm*(float(np.linalg.norm(v))+float(np.linalg.norm(ve)))+a.nominal_COM_velocity_error_norm_m_s+wheel_v
        rho=r-self.lever;rho_e=re+a.lever_position_error_norm_m;ue=(float(np.linalg.norm(w))+we)*rho_e+we*float(np.linalg.norm(rho))+rde
        return {'r_COM_B3':r,'rDot_COM_B3':rd,'omega_B3':w,'u_B3':u,'u_error_norm_m_s':ue,'r_error_norm_m':re,'rDot_error_norm_m_s':rde,'omega_endpoint_error_norm_rad_s':we,'q_axis_error_rad':float(qe[0]),'qd_endpoint_axis_error_rad_s':float(ve[0]),'wheel_bound':wheel_details,'window_mean_rates_not_declared_instant':True}

def capture_budget(solution,endpoint_start,endpoint_end,f_bins,durations,a=BudgetAssumptions()):
    """Worst-case triangle/operator budget; no statistical independence assumed.
    Exact formulas here are conditional on declared smoothness/geometry envelopes.
    """
    f=np.asarray(f_bins,float);h=np.asarray(durations,float);T=float(h.sum());nf=math.sqrt(3)*a.proper_axis_noise_m_s2;nw=math.sqrt(3)*a.gyro_axis_noise_rad_s
    slope_f=math.sqrt(3)*a.proper_BODY_slope_axis_m_s3;slope_w=math.sqrt(3)*a.angular_rate_slope_axis_rad_s2
    force_noise=nf;force_missing=slope_f*a.mean_abs_bin_time_distance_s;theta=0.;rot_transport=0.;theta_sup=[]
    for vec,dt in zip(f,h):
        sup=theta+(nw+slope_w*a.mean_endpoint_age_s)*dt;eta=min(2.,sup);rot_transport+=dt*eta*float(np.linalg.norm(vec));theta_sup.append(sup)
        theta+=dt*(nw+slope_w*a.mean_abs_bin_time_distance_s)
    rot_transport/=T;eta_end=min(2.,theta);R=solution['R_relative_end'];u1=endpoint_end['u_B3'];u0=endpoint_start['u_B3']
    boundary_measurement=(endpoint_start['u_error_norm_m_s']+endpoint_end['u_error_norm_m_s'])/T;boundary_orientation=eta_end*float(np.linalg.norm(u1))/T
    total=force_noise+force_missing+rot_transport+boundary_measurement+boundary_orientation
    magnitude=float(np.linalg.norm(solution['average_COM_proper_start_frame3']));interval=(max(0.,magnitude-total),magnitude+total);conditional_interval='overlap'
    if interval[1]<=a.freefall_max_g*9.81:conditional_interval='freefall_like_under_declared_radius_only'
    elif interval[0]>=a.nonfreefall_min_g*9.81:conditional_interval='nonfreefall_like_under_declared_radius_only'
    fixed_body_bias_operator=(R@skew(endpoint_end['omega_B3'])-skew(endpoint_start['omega_B3']))/T
    fixed_velocity_bias_operator=(R-np.eye(3))/T
    return {'proposed_error_radius_m_s2':float(total),'proposed_norm_interval_m_s2':interval,'proper_noise_not_reduced_with_N_m_s2':force_noise,'missing_proper_transport_sampling_m_s2':force_missing,'gyro_orientation_transport_m_s2':rot_transport,'boundary_endpoint_error_m_s2':boundary_measurement,'boundary_orientation_error_m_s2':boundary_orientation,'relative_end_angle_error_bound_rad':theta,'conditional_interval_NOT_trusted_cue':conditional_interval,'strict_cue':0,'conditional_cue':0,'conditional_confidence':min(.50,a.assumed_input_confidence_cap),'frozen_threshold_not_lowered':a.frozen_cue_min_confidence,'fixed_BODY_COM_bias_operator_bound_m_s2_if_that_specific_correlation_assumed':float(np.linalg.norm(fixed_body_bias_operator,2))*a.nominal_COM_position_error_norm_m,'fixed_BODY_velocity_bias_operator_bound_m_s2_if_that_specific_correlation_assumed':float(np.linalg.norm(fixed_velocity_bias_operator,2))*a.nominal_COM_velocity_error_norm_m_s,'fixed_bias_comparison_does_not_replace_default_triangle_budget':True,'no_alpha_or_qdd_differenced_for_estimator':True,'hardware_binding':False,'not_current_instant_cue':True}
