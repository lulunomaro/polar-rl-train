"""Static USD/candidate-contract regression tests. No target-PhysX success is claimed."""
from pathlib import Path
import argparse,json,hashlib,shutil,traceback,copy
import numpy as np
from pxr import Usd,UsdGeom,UsdPhysics,UsdUtils,Sdf
from inspect_usd_asset import inspect,serial,rot
ROOT=Path(__file__).resolve().parent

def digest(v):
 try:
  a=np.asarray(v)
  if a.dtype.kind in 'biuf' and a.size:return hashlib.sha256(str((a.dtype.str,a.shape)).encode()+a.tobytes()).hexdigest()
 except (ValueError,TypeError):pass
 return hashlib.sha256(json.dumps(serial(v),sort_keys=True).encode()).hexdigest()
def geometry(stage):
 cache=UsdGeom.XformCache();rows={}
 for p in Usd.PrimRange(stage.GetPseudoRoot(),Usd.TraverseInstanceProxies()):
  if not p.IsA(UsdGeom.Gprim):continue
  a={}
  for n in ('points','faceVertexIndices','faceVertexCounts','normals','primvars:displayColor','radius','height','size','axis','extent','orientation','subdivisionScheme','doubleSided'):
   v=p.GetAttribute(n)
   if v:a[n]={'type':str(v.GetTypeName()),'data_sha256':digest(v.Get()),'time_samples':list(v.GetTimeSamples())}
  rows[str(p.GetPath())]={'type':p.GetTypeName(),'attributes':a,'world_transform_row':serial(cache.GetLocalToWorldTransform(p))}
 return rows

def validate(out):
 target=out/'assets/robot.usd';assert target.is_file();bp=out/'baseline/robot.usd';old=inspect(bp);new=inspect(target);report={'runtime_verified':False,'training_started':False,'checks':{},'failures':[]}
 def check(n,b,detail=None):
  report['checks'][n]={'passed':bool(b),'detail':detail}
  if not b:report['failures'].append(n)
 check('meters_kilograms_Z_up',new['meters_per_unit']==1 and new['kilograms_per_unit']==1 and new['up_axis']=='Z')
 check('31_bodies_36_joints_34_colliders_preserved',new['counts']==old['counts'],{'before':old['counts'],'after':new['counts']})
 check('positive_finite_mass_and_inertia',not new['body_property_errors'],new['body_property_errors'])
 ob={b['name']:b for b in old['bodies']};nb={b['name']:b for b in new['bodies']};check('all_rigid_body_frames_unchanged',all(ob[n]['world_transform_row']==nb[n]['world_transform_row'] for n in ob))
 check('all36_joint_types_frames_limits_drives_armatures_unchanged',old['joints']==new['joints'])
 check('six_excluded_spherical_closures_preserved',sum(j['type']=='PhysicsSphericalJoint' and j['exclude_from_articulation'] for j in new['joints'])==6)
 check('all_collision_attributes_material_bindings_filters_unchanged',old['colliders']==new['colliders'])
 check('tire_guide_and_generic_materials_unchanged',old['physics_materials']==new['physics_materials'])
 os=Usd.Stage.Open(str(bp));ns=Usd.Stage.Open(str(target));og=geometry(os);ng=geometry(ns);geom_changes=[n for n in set(og)|set(ng) if og.get(n)!=ng.get(n)]
 check('all_mesh_arrays_primitive_dimensions_and_visual_collider_poses_unchanged',not geom_changes,{'geometry_count':len(og),'changed_paths':geom_changes})
 c=json.loads((out/'assets/import_contract.json').read_text(encoding='utf-8'));contract_errors=[]
 for name,b in nb.items():
  e=c['bodies'][name];eq=rot(e['principal_axes_wxyz']);EI=eq@np.diag(e['diagonal_inertia_kg_m2'])@eq.T
  if not(np.isclose(b['mass'],e['mass_kg'],rtol=1e-6,atol=1e-8) and np.allclose(b['com'],e['com_m'],rtol=1e-6,atol=1e-8) and np.allclose(b['inertia_tensor_body'],EI,rtol=1e-5,atol=1e-8)):contract_errors.append(name)
 check('all31_mass_COM_full_inertia_match_new_contract',not contract_errors,contract_errors)
 changed=[n for n in ob if ob[n]['mass']!=nb[n]['mass']];check('only_known_mounting_bodies_mass_corrected',set(changed)=={'chassis','left_shin','right_shin'},changed)
 dm=new['nominal_mass_sum_kg']-old['nominal_mass_sum_kg'];check('known_motor_delta_plus74g',abs(dm-0.074)<2e-6,{'before_kg':old['nominal_mass_sum_kg'],'after_kg':new['nominal_mass_sum_kg'],'delta_kg':dm})
 check('OEM963g_user131g_and_replacement_gearbox_scope',c['leg_motor']['mass_each_kg']==0.963 and c['wheel_motor']['bare_motor_mass_assumption_kg']==0.131 and c['wheel_motor']['total_gear_ratio']==15.8)
 check('selected_physics_clock_in_new_contract',c['physics_dt_s']==0.0025)
 a=new['articulations'][0]['attrs'];check('standalone_solver32_4_matches_selected_runtime',a['physxArticulation:solverPositionIterationCount']['value']==32 and a['physxArticulation:solverVelocityIterationCount']['value']==4)
 gas=[j for j in new['joints'] if j['name'] in ('left_gas_slide','right_gas_slide')];check('gas400_wrapper_settings_preserved',all(j['attrs']['drive:linear:physics:stiffness']['value']==2000 and abs(j['attrs']['physics:upperLimit']['value']-0.020639440248416612)<1e-8 for j in gas))
 deps=UsdUtils.ComputeAllDependencies(Sdf.AssetPath(str(target)));check('standalone_no_external_or_unresolved_assets',len(deps[0])==1 and not deps[1] and not deps[2])
 portable=out/'portable_probe';assert not portable.exists();portable.mkdir();shutil.copy2(target,portable/'robot.usd');ps=Usd.Stage.Open(str(portable/'robot.usd'));pd=UsdUtils.ComputeAllDependencies(Sdf.AssetPath(str(portable/'robot.usd')));pr=list(Usd.PrimRange(ps.GetPseudoRoot(),Usd.TraverseInstanceProxies()));check('relocated_single_file_loads_with31bodies',sum(p.HasAPI(UsdPhysics.RigidBodyAPI) for p in pr)==31 and not pd[1] and not pd[2])
 report['status']='PASS_STATIC_CANDIDATE' if not report['failures'] else 'FAIL_STATIC_CANDIDATE';report['output_usd_sha256']=hashlib.sha256(target.read_bytes()).hexdigest();report['usd_version']=Usd.GetVersion();report['mass_sum_kg']=new['nominal_mass_sum_kg'];report['not_validated']=['targetIsaacSim/PhysX parsing and short dynamics','rollout stability and real-robot robustness','complete updatedSolidWorks per-body nominal properties','provisional motor rotor inertia and torque-speed envelope remain unchanged'];report['new_asset_inventory']=new
 (out/'VALIDATION.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8');print(json.dumps({k:v for k,v in report.items() if k!='new_asset_inventory'},ensure_ascii=False,indent=2));assert not report['failures'],report['failures'];return report
if __name__=='__main__':
 a=argparse.ArgumentParser();a.add_argument('--version',default='v1');x=a.parse_args();out=ROOT/'candidates'/x.version;assert not(out/'VALIDATION.json').exists()
 try:validate(out)
 except Exception:
  (out/'VALIDATION_FAILURE_001.json').write_text(json.dumps({'status':'reader_or_validation_failed','error':traceback.format_exc(),'runtime_verified':False},ensure_ascii=False,indent=2),encoding='utf-8');raise
