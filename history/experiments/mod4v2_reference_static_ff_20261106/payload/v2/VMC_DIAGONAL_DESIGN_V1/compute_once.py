"""One NEW SDK-free nominal PD-coupling calculation + one tiny FK/work check."""
from pathlib import Path
import os
for k in('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
import ast,hashlib,importlib.util,json,math,sys,traceback
import numpy as np
D=Path(__file__).resolve().parent;R=D.parent;COUNTS=dict(nominal_jacobian=0,public_fk=0,tiny_extra_pose=0,model_compile=0,forward=0,step=0,old_validator=0)
def rec(p):
 p=Path(p);b=p.read_bytes();return dict(path=str(p),bytes=len(b),SHA=hashlib.sha256(b).hexdigest())
def ser(x):
 if isinstance(x,np.ndarray):return x.tolist()
 if isinstance(x,np.generic):return x.item()
 if isinstance(x,dict):return{k:ser(v)for k,v in x.items()}
 if isinstance(x,(tuple,list)):return[ser(v)for v in x]
 return x
def save(n,x):
 with(D/n).open('x',encoding='utf-8',newline='\n')as f:json.dump(ser(x),f,indent=2,ensure_ascii=False,allow_nan=False);f.write('\n')
def coord(r):
 l=float(np.linalg.norm(r));return np.array([l,math.atan2(float(r[0]),float(-r[1]))])
def main():
 assert not(D/'RESULT.json').exists()
 source=R/'CONTACT_PROXY_V2/nominal_model.py';constants=source.with_name('PUBLIC_NOMINAL_CONSTANTS.json');gainfile=R/'nominal_gain_v2.json'
 pins=[rec(p)for p in(D/'PREEXEC.json',Path(__file__),source,constants,gainfile)]
 save('PREEXEC_INPUT_PINS.json',dict(status='FROZEN_BEFORE_NEW_PUBLIC_GEOMETRY_IMPORT_OR_FK',files=pins,expected_constants_SHA='d394608bc662ce5c2b21dd9176668eaa68ebfca7eedac682b218c0a086abc546',no_SDK_statics_DARE_physics_or_oldraw=True))
 assert pins[3]['SHA']=='d394608bc662ce5c2b21dd9176668eaa68ebfca7eedac682b218c0a086abc546'
 spec=importlib.util.spec_from_file_location('vmc_v2_public_nominal_geometry',source);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
 m=module.NominalModel();original=m.fk
 def fk(*a,**kw):COUNTS['public_fk']+=1;return original(*a,**kw)
 m.fk=fk
 gain=json.loads(gainfile.read_bytes())['gain'];gq=np.asarray(gain['q'],float);q0=np.array([gq[3],gq[3]+gq[4],gq[5],gq[5]+gq[6]])
 COUNTS['nominal_jacobian']+=1;jac=m.derivatives(q0);pose=jac['pose'];legs=[]
 for side in range(2):
  r=pose['wheel_B'][side,[0,2]];l=float(np.linalg.norm(r));J=jac['Jwheel'][side][:,[2*side,2*side+1]][[0,2],:]
  T=np.vstack((r/l,np.array([-r[1],r[0]])/(l*l)))@J;inv=np.linalg.inv(T)
  K=inv.T@(120.*np.eye(2))@inv;C=inv.T@(4.*np.eye(2))@inv
  rho=float(K[0,1]/math.sqrt(K[0,0]*K[1,1]));diagK=np.diag(np.diag(K));diagC=np.diag(np.diag(C))
  Kj=T.T@diagK@T;Dj=T.T@diagC@T
  assert np.isfinite(T).all()and np.all(np.linalg.eigvalsh(K)>0)and np.all(np.linalg.eigvalsh(C)>0)and abs(rho)<1
  legs.append(dict(side=('left','right')[side],r_ROOT_xz_m=r,z_l_phi=coord(r),Jwheel_xz_absq_m_rad=J,T0=T,T0_inverse=inv,Kvirt=K,Dvirt=C,normalized_cross_coupling=rho,normalized_K=[[1.,rho],[rho,1.]],Kvirt_SPD=True,Dvirt_SPD=True,Kdiag=diagK,Ddiag=diagC,Kjoint_after_virtual_diagonal=Kj,Djoint_after_virtual_diagonal=Dj,joint_stiffness_eigenvalues_Nm_rad=np.linalg.eigvalsh(Kj),joint_damping_eigenvalues_Nms_rad=np.linalg.eigvalsh(Dj),relative_joint_stiffness_eigenvalues=np.linalg.eigvalsh(Kj)/120.,analytic_ratio_bounds=[1/(1+abs(rho)),1/(1-abs(rho))],Kjoint_change_eigenvalues=np.linalg.eigvalsh(Kj-120*np.eye(2)),mixed_units_condition_not_scale_invariant=float(np.linalg.cond(T))))
 # ONE additional tiny paired pose, not a second operating Jacobian.
 dq=np.array([1e-7,-2e-7,-1e-7,2e-7]);COUNTS['tiny_extra_pose']+=1;p1=m.fk(q0+dq);u=np.array([10.,.25]);linear=nonlinear=joint=0.;checks=[]
 for side in range(2):
  T=legs[side]['T0'];ds=dq[2*side:2*side+2];force=u if side==0 else-u;tau=T.T@force
  dy=T@ds;dy_actual=coord(p1['wheel_B'][side,[0,2]])-legs[side]['z_l_phi']
  wj=float(tau@ds);wl=float(force@dy);wn=float(force@dy_actual);joint+=wj;linear+=wl;nonlinear+=wn
  assert abs(wj-wl)<=1e-18 and abs(wj-wn)<=1e-11
  checks.append(dict(side=legs[side]['side'],delta_q_rad=ds,linear_delta_virtual=dy,one_tiny_FK_delta_virtual=dy_actual,effort_for_work_only_N_Nm=force,joint_torque_for_work_only_Nm=tau,joint_work_J=wj,linear_virtual_work_J=wl,nonlinear_tiny_virtual_work_J=wn,linear_work_abs_error_J=abs(wj-wl),tiny_FK_work_abs_error_J=abs(wj-wn)))
 T0=legs[0]['T0'];Kj=legs[0]['Kjoint_after_virtual_diagonal'];Dj=legs[0]['Djoint_after_virtual_diagonal']
 vL=dq[:2]/1e-6;vR=dq[2:]/1e-6;d=vL-vR;tauL=-.5*Dj@d;P=float(tauL@vL+(-tauL)@vR);expected=-.5*float(d@Dj@d)
 assert abs(P-expected)<=1e-12 and P<=0
 assert COUNTS==dict(nominal_jacobian=1,public_fk=10,tiny_extra_pose=1,model_compile=0,forward=0,step=0,old_validator=0)
 assert 'mujoco'not in sys.modules and 'scipy'not in sys.modules
 for item in pins:assert rec(item['path'])==item
 result=dict(status='COMPLETE_NEW_NOMINAL_GEOMETRY_COUPLING_NOT_M2_PHYSICS_OR_GAIN_QUALIFICATION',q0_absolute=q0,legs=legs,left_right_T0_max_abs_difference=float(np.max(abs(legs[0]['T0']-legs[1]['T0']))),units=dict(Trows=['m/rad','rad/rad'],Kvirt=[['N/m','N/rad'],['Nm/m','Nm/rad']],Dvirt=[['Ns/m','Ns/rad'],['Nms/m','Nms/rad']],F_positive='generalized outward length effort, NOT measured/support Fn',Tp_positive='conjugate phi=atan2(x,-z); this is minus physical wheel-force moment about body+y',SPD='energy-positive; mixed-unit raw eigen/condition not invariant to m/rad scaling',rho='dimensionless after treating rad as SI dimensionless; unchanged by positive axis unit scaling'),tiny_check=dict(q1=q0+dq,checks=checks,total_linear_work_error_J=abs(joint-linear),total_tiny_FK_work_error_J=abs(joint-nonlinear),damping_power_W=P,damping_power_expected_W=expected,no_force_estimation=True),counts=COUNTS,inputs=pins,proposal=dict(candidate_selection='NOT_SELECTED_BY_THIS_TASK; if measured crosscoupling is negligible, report no geometric basis for this M2 instead of forcing it',one_M2_candidate='HYPOTHETICAL ONLY: replace coordinated DIFFERENTIAL PD with shared nominal tangent virtual-diagonal equivalent Kj,Dj; common LQR/C1/FF/wheels/limits unchanged',virtual_error='e_tilde=T0*((qrefL-qL)-(qrefR-qR)); edot_tilde=T0*((vrefL-vL)-(vrefR-vR))',mapping='u=.5*(diag(Kvirt)*e_tilde+diag(Dvirt)*edot_tilde); delta_tauL=T0.T*u; delta_tauR=-delta_tauL',equivalent_joint='delta_tauL=.5*(Kj*(eqL-eqR)+Dj*(evL-evR)); delta_tauR=-delta_tauL',T0_anchor='left nominal; actual right computed/reported, not assumed bit identical',Kj=Kj,Dj=Dj,not_actual_nonlinear_length_errors=True,no_common_joint_torque_increment=True,unmeasured_Fn_alpha_or_contact_not_used=True,saturation_passivity_not_qualified=True),tradeoffs=dict(remove_virtual_offdiagonal='Changes energy ellipses, not uniform gain reduction: one joint direction softer, one stiffer; no automatic stability/contact improvement',actual_nonlinear_mapping='For actual z=[l,phi], TL/TR: uL=.5*(Kd*e_z+Dd*edot_z); uR=-uL; tauL=TL.T*uL,tauR=-TR.T*uL. Power-consistent and virtual-effort-zero-sum, but tauL+tauR=(TL.T-TR.T)*uL generally NONZERO',shared_nominal_mapping='Joint torque-zero-sum and stationary-reference damping nonpositive; actual efforts TL^-T*T0.T*u and -TR^-T*T0.T*u generally do not sumzero when TL!=TR',commonmode='LQR common-mode and actual geometric commonmode differ; same virtual errors and TL!=TR can couple; wheel torques untouched does not prove root pitch/roll load neutrality',support='Opposite length efforts do not imply opposite vertical support: body contact/Jac/frame/mass/gas/dynamics matter; no measured Fn signal',power='Static-reference tangent spring energyU=.25*ediff.T*Kj*ediff; dampingP=-.5*vdiff.T*Dj*vdiff<=0 BEFORE saturation/DR/PD/DC/delay. Moving refs may input energy; final clipping need not preserve passivity.'),no_new_gain_grid_or_axialD_or_MPC_or_physics=True,parent_owns_controller_and_actual_case=True)
 save('RESULT.json',result)
 print(json.dumps(ser(dict(status=result['status'],q0=q0,legs=legs,T_difference=result['left_right_T0_max_abs_difference'],counts=COUNTS,work=result['tiny_check'],Kj=Kj,Dj=Dj)),allow_nan=False))
if __name__=='__main__':
 try:main()
 except BaseException:
  if not(D/'FIRST_ERROR.json').exists():save('FIRST_ERROR.json',dict(status='STOP_FIRST_GEOMETRY_ERROR_NO_SILENT_RETRY',error=traceback.format_exc(),counts=COUNTS))
  raise
