"""Actual complete-model load and bounded mechanical regressions; no training or old weights."""
from pathlib import Path
import json,sys,math,traceback,xml.etree.ElementTree as ET
import numpy as np
import mujoco
from pxr import Usd,UsdPhysics
D=Path(__file__).resolve().parent;P=D/'candidates/HW300N60/package';OUT=D/'candidates/HW300N60/VALIDATION.json';assert not OUT.exists()
S=json.loads((D/'MECHANICAL_LIMITS_SPEC_V2_HW300N60.json').read_bytes());checks={};details={};errors=[]

def ck(name,value,detail=None):
 checks[name]=bool(value)
 if detail is not None:details[name]=detail
 if not value:raise AssertionError(name)

def normval(x):return None if not math.isfinite(float(x))else float(x)

try:
 sys.path.insert(0,str(P));import kinematics_v2 as kin
 xml=P/'mjcf/scene.xml';tree=ET.parse(xml);ck('explicit_MJCF_radian_units',tree.getroot().find('compiler').get('angle')=='radian')
 m=mujoco.MjModel.from_xml_path(str(xml));d=mujoco.MjData(m)
 ck('whole31robotbody_model_loads',m.nbody==32 and m.nq==37 and m.nv==36 and m.nu==6 and m.neq==10,dict(nbody_with_world=m.nbody,nq=m.nq,nv=m.nv,nu=m.nu,neq=m.neq))
 ck('nominal_mass_preserved',abs(float(m.body_mass.sum())-14.294140288606286)<1e-6,dict(mass_kg=float(m.body_mass.sum())))
 stage=Usd.Stage.Open(str(P/'assets/robot.usd'),load=Usd.Stage.LoadNone);ck('USD_loads',stage is not None)
 contract=json.loads((P/'assets/import_contract.json').read_bytes());params=json.loads((P/'model_parameters.json').read_bytes())
 bound_rows=[]
 for side in('left','right'):
  for short,pair in S['per_side_joint_bounds_SI'].items():
   name=side+'_'+short;j=m.joint(name);raw=m.jnt_range[j.id].copy();limited=bool(m.jnt_limited[j.id]);p=stage.GetPrimAtPath('/Robot/joints/'+name);is_slide=short=='gas_slide'
   u=[float(p.GetAttribute('physics:lowerLimit').Get()),float(p.GetAttribute('physics:upperLimit').Get())]
   if not is_slide:u=[math.radians(x)for x in u]
   both_free=pair==[None,None]
   ck(name+'_limited_semantics',limited is not both_free)
   for i,wanted in enumerate(pair):
    if wanted is None:
     ck(name+'_USD_unbounded_'+str(i),math.isinf(u[i])and(u[i]<0 if i==0 else u[i]>0))
     if not both_free:ck(name+'_MJCF_unbounded_'+str(i),math.isinf(float(raw[i]))and(raw[i]<0 if i==0 else raw[i]>0))
    else:
     ck(name+'_finite_boundary_'+str(i),abs(float(raw[i])-wanted)<1e-7 and abs(u[i]-wanted)<1e-7)
   bound_rows.append(dict(joint=name,MJCF_limited=limited,MJCF_range=[normval(x)for x in raw],USD_SI=[normval(x)for x in u],expected=pair))
 details['boundaries']=bound_rows
 gas=[]
 for side in('left','right'):
  j=m.joint(side+'_gas_slide');adr=int(j.qposadr[0]);dof=int(j.dofadr[0]);k=float(m.jnt_stiffness[j.id]);ref=float(m.qpos_spring[adr]);dam=float(m.dof_damping[dof]);lo,hi=m.jnt_range[j.id]
  p=stage.GetPrimAtPath('/Robot/joints/'+side+'_gas_slide');drive=UsdPhysics.DriveAPI.Get(p,'linear');uk=float(drive.GetStiffnessAttr().Get());ur=float(drive.GetTargetPositionAttr().Get());ud=float(drive.GetDampingAttr().Get())
  fext=k*(ref-hi);fcomp=k*(ref-lo)
  ck(side+'_gas_stroke60mm',abs(float(hi-lo)-.06)<1e-9)
  ck(side+'_gas_nominal_extension300N',abs(fext-300)<1e-6)
  ck(side+'_gas_USD_MJCF_same_law',abs(uk-k)<1e-6 and abs(ur-ref)<1e-7 and abs(ud-dam)<1e-7)
  gas.append(dict(side=side,slide_min_m=float(lo),slide_max_m=float(hi),stiffness_N_m=k,damping_N_s_m=dam,target_m=ref,force_extension_zero_velocity_N=float(fext),force_compressed_zero_velocity_N=float(fcomp),force_curve_calibrated=False))
 details['gas']=gas
 connects=[(x.attrib['site1'],x.attrib['site2'])for x in tree.getroot().find('equality').findall('connect')]
 def closure_max():return max(float(np.linalg.norm(d.site_xpos[m.site(a).id]-d.site_xpos[m.site(b).id]))for a,b in connects)
 def resetpose(left,right):
  mujoco.mj_resetData(m,d);d.qpos[:3]=[0.,0.,1.];d.qpos[3:7]=[1.,0.,0.,0.];kin.set_configuration(m,d,left=left,right=right,check_limits=True);return closure_max()
 base_xpos=None;turns=[]
 for alpha in(0.,2*math.pi,-2*math.pi):
  err=resetpose((alpha,alpha+.1),(alpha,alpha+.1));ck('common_turn_closure_'+str(alpha),err<1e-5)
  if base_xpos is None:base_xpos=d.xpos.copy()
  displacement=float(np.max(np.linalg.norm(d.xpos-base_xpos,axis=1)));ck('common_turn_periodic_geometry_'+str(alpha),displacement<1e-6)
  ck('common_turn_active_q_preserved_'+str(alpha),abs(float(d.qpos[m.joint('left_hip').qposadr[0]])-alpha)<1e-10)
  turns.append(dict(common_turn_rad=alpha,closure_max_m=err,max_body_position_delta_m=displacement))
 details['common_turns']=turns
 reports={side:kin.boundary_report(side)for side in('left','right')};details['mechanical_branch']=reports
 bounds={side:tuple(kin.mechanical_delta_bounds(side))for side in('left','right')}
 ck('mechanical_delta_low_matches_CAD',all(abs(v[0]-S['coordinate_convention']['source_mechanical_delta_min_rad'])<1e-6 for v in bounds.values()))
 for side,(lo,hi)in bounds.items():
  ck(side+'_feasible_branch_nonempty',lo<0<hi)
  for edge in(lo,hi):kin.leg_configuration(0.,edge,side=side,check_limits=True)
  rejected=False
  try:kin.leg_configuration(0.,lo-.01,side=side,check_limits=True)
  except ValueError:rejected=True
  ck(side+'_below_true_stop_rejected',rejected)
 bad=False
 try:kin.leg_configuration(-.3305,.357203,side='right',check_limits=True)
 except ValueError as exc:bad=True;details['earlier_screenshot_rejection']=str(exc)
 ck('earlier208mm_screenshot_not_forcefit_into200mm',bad)
 vals,pins=kin.leg_configuration(-.3305,.357203,side='right',check_limits=False)
 neutral=S['hardware_configuration']['neutral_eye_length_m'];eye=neutral+float(vals['gas_slide']);details['earlier_screenshot_eye_length_m']=eye
 ck('screenshot_geometry_conflict_explicit',eye>.20 and abs(eye-.2081539082652016)<1e-7)
 valid_delta=bounds['right'][1]-.01;err=resetpose((0.,.10805),(-.3305,-.3305+valid_delta));ck('corrected_stroke_valid_pose_closure',err<1e-5)
 details['valid_pose']=dict(left=[0.,.10805],right=[-.3305,-.3305+valid_delta],closure_m=err)
 # One bounded CPU dynamics smoke, fixed mechanical targets. No policy, DR edits or GPU.
 resetpose((0.,0.),(0.,0.));gravity=m.opt.gravity.copy();m.opt.gravity[:]=0.;leg_names=('left_hip','left_crank','right_hip','right_crank');aid={n:m.actuator(n+'_motor').id for n in leg_names};worst_closure=0.;finite=True
 for step in range(120):
  if step%4==0:
   for name in leg_names:
    j=m.joint(name);q=float(d.qpos[j.qposadr[0]]);v=float(d.qvel[j.dofadr[0]]);d.ctrl[aid[name]]=np.clip(-60*q-2*v,-40,40)
  mujoco.mj_step(m,d);finite=finite and bool(np.isfinite(d.qpos).all()and np.isfinite(d.qvel).all());worst_closure=max(worst_closure,closure_max())
 m.opt.gravity[:]=gravity
 ck('bounded_CPU_dynamics_finite',finite)
 ck('bounded_CPU_dynamics_original_closure10mm',worst_closure<.01)
 details['dynamics_smoke']=dict(physics_steps=120,physics_dt_s=float(m.opt.timestep),seconds=120*float(m.opt.timestep),held_torque_refresh_hz=100.,policy=None,gravity_temporarily_zero_for_isolated_mechanism=True,source_asset_unchanged=True,max_closure_m=worst_closure)
 ck('portable_mesh_files_resolve',all((P/'mjcf'/'assets'/x.get('file')).is_file()for x in tree.getroot().find('asset').findall('mesh')))
except BaseException:
 errors.append(traceback.format_exc())
result=dict(kind='MOD4V2_HW300N60_COMPLETE_MODEL_REGRESSION_V1',passed=not errors and all(checks.values()),checks=checks,details=details,errors=errors,hardware_geometry_user_confirmed=True,nominal_force_N=300.,force_curve_measured=False,target_PhysX_executed=False,hardware_dynamic_qualification=False,old_assets_or_checkpoints_modified=False,training_or_GPU_started=False)
OUT.write_text(json.dumps(result,indent=2,allow_nan=False),encoding='utf8');print(json.dumps(dict(receipt=str(OUT),passed=result['passed'],checks=len(checks),failed=[k for k,v in checks.items()if not v],errors=errors),indent=2));sys.exit(0 if result['passed']else 1)
