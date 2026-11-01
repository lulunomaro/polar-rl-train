"""Build an isolated MOD4 asset candidate. Never edits frozen sources or starts simulation."""
from pathlib import Path
import argparse,copy,json,hashlib,shutil,traceback,datetime
import numpy as np
from scipy.spatial.transform import Rotation
from pxr import Usd,UsdGeom,UsdPhysics,UsdUtils,Sdf,Gf
from inspect_usd_asset import rot,serial
ROOT=Path(__file__).resolve().parent
SOURCE=Path(r'C:\Users\lulu\Desktop\claude\mjcf\MOD4_H1_SCUT_STEP270_ON_210_E3_CONTINUATION_20261021\MODEL2050_LITERAL_JUMP_400N50_ADAPT_V240_20261101\package\payload\job0\assets')
EXPECTED={'robot.usd':'bce9a7740fd9a2e2252d34a09c1fef7dab70e2a65f9d0ee2e422cec5f12c60e4','source_700N/robot.usd':'694e9d5414401972d9186c44baef25aa785e1e07409ce9acf1ef553b9279dd87','import_contract.json':'517cd6a4cc469455af08da75dc4b7f7cb596b375bafb4c3e566c7df5bc51df49'}
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def parallel(p):p=np.asarray(p,dtype=float);return (p@p)*np.eye(3)-np.outer(p,p)
def group(n):
 if n=='chassis':return 'chassis'
 if n in ('left_wheel','right_wheel'):return 'drive_wheels'
 if n.startswith('guide_roller_'):return 'passive_guide_rollers'
 if '_gas_' in n:return 'moving_spring_members'
 if '_drive_' in n:return 'rotating_transmission_members'
 return 'leg_links'
def attr(p,n,t,v):
 a=p.GetAttribute(n)
 if not a:a=p.CreateAttribute(n,t,custom=False)
 a.Set(v)
def ensure_api(p,name):
 op=p.GetMetadata('apiSchemas');tokens=list(op.GetAppliedItems()) if op else []
 if name not in tokens:p.SetMetadata('apiSchemas',Sdf.TokenListOp.CreateExplicit(tokens+[name]))
def build(version):
 out=ROOT/'candidates'/version
 assert not out.exists(),'Use a new candidate ID; never overwrite a prior attempt'
 out.mkdir(parents=True);receipt={'version':version,'started_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'source':str(SOURCE),'original_source_hashes':EXPECTED,'runtime_verified':False,'training_started':False}
 try:
  for rel,want in EXPECTED.items():assert sha(SOURCE/rel)==want,rel+' source hash changed'
  baseline=out/'baseline';baseline.mkdir()
  for rel in EXPECTED:
   dst=baseline/rel;dst.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(SOURCE/rel,dst)
  deps=UsdUtils.ComputeAllDependencies(Sdf.AssetPath(str(baseline/'robot.usd')));assert not deps[2],'Unresolved original dependencies';assert not deps[1],'External source assets need explicit packaging, not guessing'
  receipt['baseline_dependencies']={'layers':[l.realPath for l in deps[0]],'assets':list(map(str,deps[1])),'unresolved':list(map(str,deps[2]))}
  contract=json.loads((baseline/'import_contract.json').read_text(encoding='utf-8'));original=copy.deepcopy(contract)
  layer=Sdf.Layer.CreateNew(str(out/'enhancement.usda'));layer.subLayerPaths=['baseline/robot.usd'];stage=Usd.Stage.Open(layer);stage.SetDefaultPrim(stage.GetPrimAtPath('/Robot'))
  receipt['stage_metadata_before']={'meters_per_unit':UsdGeom.GetStageMetersPerUnit(stage),'up_axis':UsdGeom.GetStageUpAxis(stage)}
  UsdGeom.SetStageMetersPerUnit(stage,1.0);UsdGeom.SetStageUpAxis(stage,UsdGeom.Tokens.z);UsdPhysics.SetStageKilogramsPerUnit(stage,1.0)
  corrections=[];per_body={}
  for jn in ('left_hip','left_crank','right_hip','right_crank','left_wheel_spin','right_wheel_spin'):
   jp=stage.GetPrimAtPath('/Robot/joints/'+jn);j=UsdPhysics.Joint(jp);parent=str(j.GetBody0Rel().GetTargets()[0]);name=stage.GetPrimAtPath(parent).GetName();assert name==contract['joints'][jn]['parent']
   leg=jn in ('left_hip','left_crank','right_hip','right_crank');old=original['leg_motor']['mass_each_kg'] if leg else original['wheel_motor']['bare_motor_mass_assumption_kg'];new=0.963 if leg else 0.131
   correction={'joint':jn,'parent_body':name,'mass_before_kg':old,'mass_after_kg':new,'delta_kg':new-old,'assumed_delta_center_parent_m':serial(j.GetLocalPos0Attr().Get()),'basis':'OEM DM-J8009P-2EC V1.3 corrected963g' if leg else 'Human supplied131g each after original reducer removal','center_status':'parent joint-axis anchor approximation; not a new CAD COM measurement','intrinsic_delta_inertia':'zero; unknown small delta distribution not invented'}
   corrections.append(correction);per_body.setdefault(name,[]).append(correction)
  body_changes=[]
  for name,changes in per_body.items():
   p=stage.GetPrimAtPath('/Robot/links/'+name);m=UsdPhysics.MassAPI(p);oldm=float(m.GetMassAttr().Get());c=np.asarray(m.GetCenterOfMassAttr().Get(),float);q=m.GetPrincipalAxesAttr().Get();d=np.asarray(m.GetDiagonalInertiaAttr().Get(),float);I=rot(q)@np.diag(d)@rot(q).T;Io=I+oldm*parallel(c);h=oldm*c;newm=oldm
   for change in changes:
    dm=change['delta_kg'];point=np.asarray(change['assumed_delta_center_parent_m']);newm+=dm;h+=dm*point;Io+=dm*parallel(point)
   nc=h/newm;NI=(Io-newm*parallel(nc));NI=(NI+NI.T)/2;ev,axes=np.linalg.eigh(NI);assert newm>0 and np.all(ev>0),'Nonphysical corrected mass/inertia'
   if np.linalg.det(axes)<0:axes[:,2]*=-1
   qxyzw=Rotation.from_matrix(axes).as_quat();nq=[qxyzw[3],*qxyzw[:3]]
   m.GetMassAttr().Set(float(newm));m.GetCenterOfMassAttr().Set(Gf.Vec3f(*map(float,nc)));m.GetDiagonalInertiaAttr().Set(Gf.Vec3f(*map(float,ev)));m.GetPrincipalAxesAttr().Set(Gf.Quatf(float(nq[0]),Gf.Vec3f(*map(float,nq[1:]))))
   actual={'mass_kg':float(m.GetMassAttr().Get()),'com_m':serial(m.GetCenterOfMassAttr().Get()),'diagonal_inertia_kg_m2':serial(m.GetDiagonalInertiaAttr().Get()),'principal_axes_wxyz':serial(m.GetPrincipalAxesAttr().Get())}
   for k,v in actual.items():contract['bodies'][name][k]=v
   contract['bodies'][name]['enhancement_mass_basis']='Known motor mass corrections at parent-joint anchor, with first moment and parallel-axis inertia update; approximate COM placement, not newly measured CAD tensor.'
   body_changes.append({'body':name,'before':original['bodies'][name],'after':copy.deepcopy(contract['bodies'][name]),'corrections':changes})
  ar=stage.GetPrimAtPath('/Robot/links/chassis');attr(ar,'physxArticulation:solverPositionIterationCount',Sdf.ValueTypeNames.Int,32);attr(ar,'physxArticulation:solverVelocityIterationCount',Sdf.ValueTypeNames.Int,4)
  body_groups={}
  for p in list(Usd.PrimRange(stage.GetPseudoRoot(),Usd.TraverseInstanceProxies())):
   if not p.HasAPI(UsdPhysics.RigidBodyAPI):continue
   ensure_api(p,'PhysxRigidBodyAPI');attr(p,'physxRigidBody:enableGyroscopicForces',Sdf.ValueTypeNames.Bool,True);attr(p,'physxRigidBody:linearDamping',Sdf.ValueTypeNames.Float,0.0);attr(p,'physxRigidBody:angularDamping',Sdf.ValueTypeNames.Float,0.0);attr(p,'physxRigidBody:maxDepenetrationVelocity',Sdf.ValueTypeNames.Float,1.0)
   g=group(p.GetName());p.SetCustomDataByKey('mod4:rigidBodyGroup',g);body_groups.setdefault(g,[]).append(p.GetName())
  contract['physics_dt_s']=0.0025
  contract['leg_motor']['official_model']='DM-J8009P-2EC';contract['leg_motor']['mass_each_kg']=0.963;contract['leg_motor']['mass_status']='OEM nominal, manualV1.3 2026-09-10 corrected prior921g; CAD matching20240809 model, not hardwareV1.1'
  contract['wheel_motor']['bare_motor_mass_assumption_kg']=0.131;contract['wheel_motor']['bare_motor_mass_user_provided_kg']=0.131;contract['wheel_motor']['bare_motor_mass_status']='User provided131g per retained bare motor after removing original reducer; complete396g module not used'
  env={'RM_MOD4_USD':'assets/robot.usd','RM_PHYSICS_DT_S':'0.0025','RM_POLICY_HZ':'50','RM_SOLVER_POS':'32','RM_SOLVER_VEL':'4'}
  requirements={'physics_dt_s':0.0025,'policy_dt_s':0.02,'policy_hz':50,'feedback_hz':100,'solver_type':'TGS','solver_position_iterations':32,'solver_velocity_iterations':4,'closure_episode_reset_m':0.01,'mimic_tolerance_rad':0.01,'gas_nominal_force_n':400,'gas_stiffness_n_m':2000,'gas_damping_n_s_m':3,'environment_before_import':env,'does_not_change_rewards_observations_terrain_or_training_budget':True,'does_not_start_training':True}
  profile={'enabled_automatically':False,'nominal_asset':'assets/robot.usd','groups':body_groups,'scut_reference':{'chassis_mass_scale':[0.9,1.3],'leg_and_wheel_mass_scale':[0.9,1.1],'chassis_com_xyz_half_range_m':[0.04,0.02,0.02],'note':'Mass changes require coherent inertia handling; no per-CAD-bolt DR.'},'fudan_wide_reference':{'all_rigid_body_mass_scale':[0.8,1.2],'extra_base_mass_kg':[-2,3],'chassis_com_xyz_half_range_m':[0.05,0.05,0.05],'note':'Reference recipe only; absolute kg/cm ranges are not auto-copied to MOD4.'},'keep_existing_runtime_D0_D7_events_until_new_admission':True}
  provenance={'version':version,'source_root_sha256':EXPECTED['robot.usd'],'source_base_sha256':EXPECTED['source_700N/robot.usd'],'source_contract_sha256':EXPECTED['import_contract.json'],'gas400_wrapper_preserved':True,'mass_method':'known motor delta at mounting parent joint, first moment+parallel axis','full_current_SolidWorks_body_calibration_completed':False,'not_measured_rotor_armatures_preserved':True,'runtime_verified':False}
  stage.GetDefaultPrim().SetCustomDataByKey('mod4:enhancement',provenance);layer.customLayerData={'mod4EnhancementVersion':version,'sourceRootSHA256':EXPECTED['robot.usd'],'sourceBaseSHA256':EXPECTED['source_700N/robot.usd']};layer.Save()
  asset=out/'assets';asset.mkdir();flat=stage.Flatten();assert flat.Export(str(asset/'robot.usd'),args={'format':'usdc'})
  final=Usd.Stage.Open(str(asset/'robot.usd'));usdsha=sha(asset/'robot.usd');provenance['output_usd_sha256']=usdsha
  contract['enhancement']=dict(provenance,runtime_requirements=requirements,body_groups=body_groups,source_contract_original_physics_dt_s=original['physics_dt_s'],historical_source_fields_preserved=True)
  (asset/'import_contract.json').write_text(json.dumps(contract,ensure_ascii=False,indent=2),encoding='utf-8')
  (out/'runtime_requirements.json').write_text(json.dumps(requirements,ensure_ascii=False,indent=2),encoding='utf-8');(out/'dr_reference_profiles.json').write_text(json.dumps(profile,ensure_ascii=False,indent=2),encoding='utf-8');(out/'body_mass_changes.json').write_text(json.dumps(body_changes,ensure_ascii=False,indent=2),encoding='utf-8')
  fd=UsdUtils.ComputeAllDependencies(Sdf.AssetPath(str(asset/'robot.usd')));assert not fd[1] and not fd[2],'Enhanced standalone asset has external or unresolved dependencies'
  receipt.update({'status':'BUILT_STATIC_CANDIDATE','output_usd':str(asset/'robot.usd'),'output_usd_sha256':usdsha,'output_contract_sha256':sha(asset/'import_contract.json'),'stage_metadata_after':{'meters_per_unit':UsdGeom.GetStageMetersPerUnit(final),'up_axis':UsdGeom.GetStageUpAxis(final)},'body_mass_changes':body_changes,'known_motor_mass_delta_kg':sum(x['delta_kg'] for x in corrections),'standalone_asset_layer_count':len(fd[0]),'standalone_external_assets':list(map(str,fd[1])),'standalone_unresolved':list(map(str,fd[2])),'originals_unchanged':all(sha(SOURCE/p)==s for p,s in EXPECTED.items()),'runtime_verified':False,'finished_utc':datetime.datetime.now(datetime.timezone.utc).isoformat()})
  (out/'BUILD_RECEIPT.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2),encoding='utf-8');print(json.dumps({k:v for k,v in receipt.items() if k!='body_mass_changes'},ensure_ascii=False,indent=2));return out
 except Exception:
  receipt['status']='FAILED';receipt['error']=traceback.format_exc();(out/'BUILD_FAILURE.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2),encoding='utf-8');raise
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--version',default='v1');args=p.parse_args();build(args.version)
