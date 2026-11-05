"""One actual bridge.geometry instance, one wheel_kinematics per side; no model/data/dynamics."""
from pathlib import Path
import os,sys,json,hashlib,traceback,importlib
for n in('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS'):os.environ[n]='1'
import numpy as np
D=Path(__file__).resolve().parent;R=D.parent;V1=R.parent/'mod4v1_lqr_mpc_robust_20261102'
COUNTS=dict(geometry_factory=0,wheel_kinematics_left=0,wheel_kinematics_right=0,internal_pose_left=0,internal_pose_right=0,model_compile=0,MjData=0,forward=0,integration=0,DARE=0,statics=0)
def rec(p):
 p=Path(p);b=p.read_bytes();s=p.stat();return dict(path=str(p),bytes=len(b),SHA=hashlib.sha256(b).hexdigest(),stat_size=s.st_size,mtime_ns=s.st_mtime_ns)
def save(n,x):
 with(D/n).open('x',encoding='utf-8',newline='\n')as f:json.dump(x,f,ensure_ascii=False,indent=2,allow_nan=False);f.write('\n')
def forbidden(name):
 def f(*a,**kw):COUNTS[name]+=1;raise RuntimeError('Forbidden in one-pose geometry API check: '+name)
 return f
def main():
 assert not(D/'RESULT.json').exists()and not(D/'INPUT_PINS.json').exists()
 refpath=R/'VMC_DIAGONAL_DESIGN_V1/RESULT.json';ref=json.loads(refpath.read_bytes());q=np.asarray(ref['q0_absolute'],float)
 assert np.array_equal(q,np.array([.2503281103649727,.0503281103649727]*2))
 srcs=[D/'PREEXEC.json',Path(__file__),refpath,R/'bridge_v2.py',R/'model_builder_v2.py',R/'v2_linearization.py',V1/'sensor_core.py',R.parent/'mod4v2_p0_mechanical_limits_20261105/candidates/HW300N60/package/reports/model_manifest.json']
 pins=[rec(x)for x in srcs];save('INPUT_PINS.json',dict(kind='BEFORE_FIRST_SDK_IMPORT_OR_ACTUAL_GEOMETRY_CALL',records=pins,raw_or_large_asset_read=0))
 import mujoco
 import scipy.linalg as sl
 class NoModel:
  def __new__(cls,*a,**kw):return forbidden('model_compile')(*a,**kw)
  from_xml_path=staticmethod(forbidden('model_compile'));from_xml_string=staticmethod(forbidden('model_compile'));from_binary_path=staticmethod(forbidden('model_compile'))
 old={k:getattr(mujoco,k)for k in('MjModel','MjData','mj_forward','mj_forwardSkip','mj_step','mj_step1','mj_step2','mj_Euler','mj_RungeKutta','mj_implicit')}
 oldDARE=sl.solve_discrete_are
 try:
  mujoco.MjModel=NoModel;mujoco.MjData=forbidden('MjData');mujoco.mj_forward=forbidden('forward');mujoco.mj_forwardSkip=forbidden('forward')
  for k in('mj_step','mj_step1','mj_step2','mj_Euler','mj_RungeKutta','mj_implicit'):setattr(mujoco,k,forbidden('integration'))
  sl.solve_discrete_are=forbidden('DARE')
  sys.path.insert(0,str(R));bridge=importlib.import_module('bridge_v2')
  assert Path(bridge.__file__).resolve()==(R/'bridge_v2.py').resolve()
  assert Path(sys.modules[bridge.LinkageGeometry.__module__].__file__).resolve()==(V1/'sensor_core.py').resolve()
  COUNTS['geometry_factory']+=1;g=bridge.geometry();pose=g.pose
  def counted_pose(hip,crank,side):COUNTS['internal_pose_'+side]+=1;return pose(hip,crank,side)
  g.pose=counted_pose
  policy=json.loads((D/'PREEXEC.json').read_bytes());tol=policy['tolerance_before_run'];rows=[];allpass=True
  for i,side in enumerate(('left','right')):
   COUNTS['wheel_kinematics_'+side]+=1
   velocity,r,J,knee=g.wheel_kinematics(float(q[2*i]),float(q[2*i+1]),0.,0.,0.,np.zeros(3),side)
   r=np.asarray(r,float);J=np.asarray(J,float);assert r.shape==(3,)and J.shape==(3,2)and np.isfinite(r).all()and np.isfinite(J).all()and np.isfinite([velocity,knee]).all()
   xz=r[[0,2]];Jxz=J[[0,2],:];length=float(np.linalg.norm(xz));assert length>0
   T=np.vstack((xz/length,np.array([-xz[1],xz[0]])/(length*length)))@Jxz
   e=ref['legs'][i];assert e['side']==side
   dr=xz-np.asarray(e['r_ROOT_xz_m']);dJ=Jxz-np.asarray(e['Jwheel_xz_absq_m_rad']);dT=T-np.asarray(e['T0'])
   good=bool(np.max(np.abs(dr))<=tol['position_abs_m']and np.max(np.abs(dJ))<=tol['J_xz_abs_m_per_rad']and np.max(np.abs(dT[0]))<=tol['T_length_abs_m_per_rad']and np.max(np.abs(dT[1]))<=tol['T_phi_abs_rad_per_rad'])
   allpass=allpass and good
   rows.append(dict(side=side,input=dict(hip_absolute_rad=float(q[2*i]),crank_absolute_rad=float(q[2*i+1]),hipdot=0.,crankdot=0.,spin=0.,gyro3=[0.,0.,0.]),actual=dict(root_forward_m_s=float(velocity),r_BODY_ROOT_xyz_m=r.tolist(),J_BODY_xyz_absHipCrank_m_rad=J.tolist(),relative_knee_rad=float(knee),l_m=length,phi_rad=float(np.arctan2(xz[0],-xz[1])),T_l_phi=T.tolist()),saved_reference=e,comparison=dict(XZ_J_T0_within_declared_FD_tolerance=good,dr_xz_m=dr.tolist(),dJxz_m_rad=dJ.tolist(),dT=dT.tolist(),max_abs_r_m=float(np.max(np.abs(dr))),max_abs_J_m_rad=float(np.max(np.abs(dJ))),max_abs_T=float(np.max(np.abs(dT))),full_Y_or_Jy_reference='UNKNOWN_NOT_SAVED_IN_OLD_RESULT; actualAPI_y/Jy_recorded_only',frame_units_sign='same BODY ROOT xz/metres/absolute hip-crank columns and phi=atan2(x,-z)'if good else'DIFFERENCE_REQUIRES_EXPLANATION_NO_AUTOFIX')))
  assert COUNTS['geometry_factory']==1 and COUNTS['wheel_kinematics_left']==COUNTS['wheel_kinematics_right']==1 and COUNTS['internal_pose_left']==COUNTS['internal_pose_right']==5
  assert all(COUNTS[n]==0 for n in('model_compile','MjData','forward','integration','DARE','statics'))
  for pin in pins:
   now=rec(pin['path']);assert now['SHA']==pin['SHA']and now['bytes']==pin['bytes']
  result=dict(status='ACTUAL_API_NOMINAL_XZ_J_T0_ALIGNED_NO_PHYSICS_OR_CONTROL_QUALIFICATION'if allpass else'ACTUAL_API_ALIGNMENT_DIFFERENCE_NO_RETRY',all_XZ_J_T0_within_predeclared_tolerances=allpass,counts=COUNTS,rows=rows,tolerances=tol,actual_functions=dict(factory='bridge_v2.geometry()',constructor=type(g).__module__+'.'+type(g).__name__,wheel='wheel_kinematics(hip,crank,hipdot,crankdot,spin,omega,side)',return_order=['forward_m_s','wheel_center_BODY_m3','J_BODY_absHipCrank_m_per_rad_3x2','relative_knee_rad'],source_frame_contract='chassis-frame metres; BODY ROOT, not thigh-relative or world placement',radius=float(g.radius),track=float(g.track),FD_epsilon_rad=1e-5),phi_conjugate_sign='u_phi=-physical Tp_y; not original leg_coordinates() angular coordinate',packet_order_note='source SensorPacket.joint_pos4=[Lhip,Lcrank,Rhip,Rcrank]. DR raw-order metadata alone is not a mapping bug; no packet/DR replay or new mapping change.',MuJoCo_version=mujoco.__version__,imports_allowed_new_scope_not_old_VMC_replay=True,old_nominal_model_derivatives_or_compute_once_or_3pose_QA_calls=0,old_raw_or_controller_change_or_Git_or_Goal_agents=0,old_files_unchanged=True)
  save('RESULT.json',result)
  print(json.dumps(dict(status=result['status'],counts=COUNTS,per_side=[dict(side=x['side'],comparison=x['comparison'])for x in rows]),ensure_ascii=False))
  return 0 if allpass else 1
 finally:
  for k,v in old.items():setattr(mujoco,k,v)
  sl.solve_discrete_are=oldDARE
if __name__=='__main__':
 try:raise SystemExit(main())
 except SystemExit:raise
 except BaseException:
  if not(D/'FIRST_ERROR.json').exists():save('FIRST_ERROR.json',dict(status='STOP_FIRST_API_CHECK_ERROR_NO_SILENT_RETRY',counts=COUNTS,error=traceback.format_exc()))
  raise
