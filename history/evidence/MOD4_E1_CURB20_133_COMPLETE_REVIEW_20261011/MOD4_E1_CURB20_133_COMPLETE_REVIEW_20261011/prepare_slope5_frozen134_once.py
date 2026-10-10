"""One genuinely new independent SLOPE5 component and frozen package; CPU only."""
from review133_io import *
import ast,zipfile,importlib.util,traceback
import numpy as np
PROTOCOL='approved_E1_SLOPE_derived5deg_mirrored_fullroute_behavior_v1'
SHA='3c97c14e91a5483d03cb979cd0de0858f7fd1f2a1758e8469c88b7546b02921e'

def main():
 save('SLOPE5_FROZEN_PREPARE_STARTED.json',dict(epoch=time.time(),trial_id='E1-SLOPE5-MIRRORED-FROZEN-SCOPE-01',CPU_only=True))
 assert json.loads((D.parent/'MOD4_MOE_TERRAIN_SUBEXPERT_REVISION_20261010/reports/REVISION_APPROVED.json').read_bytes())['approved']
 assert json.loads(sorted((P/'reports').glob('CURB133_SCHEMA_REVIEW_[0-9]*.json'))[-1].read_bytes())['review_complete']
 h=2.*np.tan(np.deg2rad(5.));xs=[-4.5,-1.,1.,4.5];zs=[0.,0.,h,h]
 vertices=[[x,y,z] for x,z in zip(xs,zs) for y in (-4.5,4.5)]
 faces=[]
 for j in range(3):k=2*j;faces.extend([[k,k+2,k+3],[k,k+3,k+1]])
 prof=dict(schema='derived_continuous5deg_ramp_cpu_component_v1',angle_deg=5.,ramp_length_m=2.,height_m=float(h),ramp_start_x_m=-1.,ramp_end_x_m=1.,
  tile_size_m=[9.,9.],vertices=vertices,triangles=faces,no_vertical_riser=True,lower_upper_support_m=3.5,
  derived_not_actual_RM_geometry=True,RM003_local5deg_entry_only=True,not_stair_flight=True,not_physical_traversal_pass=True)
 path=D/'implementation/slope5_profile.json';assert not path.exists();path.write_bytes(json.dumps(prof,indent=2).encode())
 sys.path.insert(0,str(D/'implementation'));import slope5_geometry as c
 spec=importlib.util.spec_from_file_location('independent_triangle_ray',D.parent/'MOD4_MOE_TERRAIN_SUBEXPERT_REVISION_20261010/prepare_curb_component_once.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
 errs=[];normals=[]
 for mirrored in (False,True):
  mesh,origin=c.make_mesh((9.,9.),mirrored);v=mesh.vertices.copy();v[:,:2]-=4.5;o=-1 if mirrored else 1
  for x in np.r_[np.linspace(-4.4,4.4,31),[-1.,1.]]:
   for y in (-4.,0.,4.):
    hit=m.ray(np.array([o*x,y,2.]),np.array([0.,0.,-1.]),v,mesh.faces)
    errs.append(abs(hit[2]-np.clip((x+1.)/2,0,1)*h))
  triangles=v[mesh.faces];slopefaces=np.ptp(triangles[:,:,2],axis=1)>1e-10
  angles=np.rad2deg(np.arccos(mesh.face_normals[slopefaces,2]));assert np.max(abs(angles-5.))<1e-10;normals.append(mesh.face_normals.tolist())
 assert max(errs)<1e-10
 parent=D.parent/'MOD4_E1_CURB20_INDEPENDENT_PREPARE_20261011/artifacts/e1-curb20-derived-mirrored-fullroute-frozen-v1.zip'
 assert H(parent.read_bytes())=='b91238eddc550555a70f2a09e4cf8ff085d66fad1cb00bcb5736da6a71b04e7d'
 with zipfile.ZipFile(parent) as z:members={n:z.read(n) for n in z.namelist()}
 manifest=json.loads(members['SOURCE_MANIFEST.json']);assert all(H(members[n])==s for n,s in manifest['files'].items())
 old=members['runtime/isaac/mod4/frozen_history_flat.py'].decode();new=old.replace('from curb20_geometry import configure_curb as configure_intro','from slope5_geometry import configure_slope as configure_intro')
 new=new.replace("xy[:,0,0]-=1.;xy[:,1,0]+=1.","xy[:,0,0]-=2.;xy[:,1,0]+=2.")
 new=new.replace('np.ptp(preliminary_height,axis=1)-.020','np.ptp(preliminary_height,axis=1)-2.*np.tan(np.deg2rad(5.))')
 new=new.replace('.075+support,-.075-support','1.+support,-1.-support')
 new=new.replace('np.linspace(-.475,.475,35)','np.linspace(-1.4,1.4,35)')
 new=new.replace('np.where(samples<-.075,0.,.020)','np.clip((samples+1.)/2.,0.,1.)*(2.*np.tan(np.deg2rad(5.)))')
 new=new.replace('(initial_u[ids%3!=1]<-.075)','(initial_u[ids%3!=1]<-1.)').replace('(initial_u[ids%3==1]>.075)','(initial_u[ids%3==1]>1.)')
 begin=new.index('    route_scope=dict(');end=new.index('    assert e.physics_dt',begin)
 new=new[:begin]+'''    route_scope=dict(tile_rows=tile_rows.tolist(),tile_cols=tile_cols.tolist(),family='derived_continuous5deg_ramp',tile_centers=centers.tolist(),requested_starts=starts.tolist(),size_m=size.tolist(),flat_support_margin_m=support,orientation=orientation.tolist(),ramp_start_canonical_x_m=-1.,ramp_end_canonical_x_m=1.,angle_deg=5.,ramp_length_m=2.,height_m=2.*np.tan(np.deg2rad(5.)),required_after_support_m=.200,actual_sampled_canonical_x_m=samples.tolist(),actual_sampled_ground=sampled.tolist(),actual_sampled_normals=js(sample['normal']),actual_authored_ground_query_passed=True,initial_wheel_link_positions=initial_wheel.tolist(),initial_two_wheels_on_requested_side=True,no_vertical_riser=True,not_actual_RM_geometry=True,not_stair_flight=True,termination_change='evaluation-only declared truncation abs x3.5m or abs y3m',production_boundary_unchanged=True,not_training_or_RM70mm=True)
'''+new[end:]
 new=new.replace('approved_E1_CURB_derived20mm_mirrored_fullroute_behavior_v1',PROTOCOL)
 getfor=lambda src:next(n for n in next(x for x in ast.parse(src).body if isinstance(x,ast.FunctionDef) and x.name=='main').body if isinstance(n,ast.For) and ast.unparse(n.target)=='step')
 assert ast.dump(getfor(old),include_attributes=False)==ast.dump(getfor(new),include_attributes=False)
 compile(new,'frozen_history_flat_SLOPE134.py','exec');(D/'implementation/frozen_history_flat_SLOPE134.py').write_bytes(new.encode())
 changes={'runtime/isaac/mod4/frozen_history_flat.py':new.encode(),'runtime/isaac/mod4/slope5_geometry.py':(D/'implementation/slope5_geometry.py').read_bytes(),'runtime/isaac/mod4/slope5_profile.json':path.read_bytes()}
 members.update(changes);manifest.update(protocol=PROTOCOL,parent_archive_sha256=H(parent.read_bytes()),current_geometry_revision004='E1_SLOPE5',current_geometry_is_G3_wave=False,current_geometry_is_CURB=False,
  derived_not_actual_RM_geometry=True,current_frozen_scope=dict(angle_deg=5.,ramp_length_m=2.,mirrored=True,approach_m=.4,after_support_m=.2,steps=1500,num_envs=80,seconds=15,optimizer_updates=0))
 manifest['files']={n:H(b) for n,b in members.items() if n!='SOURCE_MANIFEST.json'};manifest['new_or_changed_members']={n:H(b) for n,b in changes.items()};members['SOURCE_MANIFEST.json']=json.dumps(manifest,indent=2).encode()
 (D/'artifacts').mkdir(exist_ok=True);pkg=D/'artifacts/e1-slope5-derived-mirrored-fullroute-frozen-v1.zip';assert not pkg.exists()
 with zipfile.ZipFile(pkg,'w',zipfile.ZIP_DEFLATED) as z:
  for n,b in members.items():z.writestr(n,b)
 with zipfile.ZipFile(pkg) as z:assert all(H(z.read(n))==s for n,s in manifest['files'].items())
 prior=json.loads((D.parent/'MOD4_E1_CURB20_INDEPENDENT_PREPARE_20261011/reports/CURB_FROZEN_PREPARED.json').read_bytes())['jobs'][0]
 cp=dict(path=E+'/artifacts/e1-stable-own-'+SHA+'.pt',bytes=17615538,sha256=SHA);pkginfo=dict(path=str(pkg.resolve()),bytes=pkg.stat().st_size,sha256=H(pkg.read_bytes()))
 job=dict(prior);job.update(job_id='clk2500-closure-episode-d3-134-e1-slope5-source364-mirrored-fullroute-flat',role='E1_SLOPE5_source364_frozen_anchor',protocol=PROTOCOL,actual_curriculum_expert='E1_SLOPE',
  actual_behavior_scope='New independent derived continuous5degree2m ramp; mirrored complete lower support to both wheels over entire incline to200mm upper support and reverse. Frozen only.',
  artifacts=dict(runtime=dict(path=E+'/artifacts/'+pkg.name,bytes=pkginfo['bytes'],sha256=pkginfo['sha256']),checkpoint=cp))
 v=dict(epoch=time.time(),trial_id='E1-SLOPE5-MIRRORED-FROZEN-SCOPE-01',package=pkginfo,jobs=[job],CPU_component_and_package_passed=True,
  independent_triangle_rays=len(errs),max_vertical_ray_error_m=float(max(errs)),actual_mesh_normals=normals,immutable_files_map_exact=len(manifest['files']),old_unchanged_members=len(members)-len(changes)-1,
  changed_members={n:H(b) for n,b in changes.items()},profile=prof,physical_step_health_hardware_contact_auditor_AST_exact=True,
  source_selected_complete129_SHA=SHA,curb389_not_selected_as_warmstart=True,no_CURB_PPO_or_height_increase=True,
  new_SLOPE_SDK_native_fullstate_PPO_and_learning_executor_pending=True,no_GPU_or_canonical_mutation=True,new_budget_seconds=0)
 save('SLOPE5_FROZEN_PREPARED.json',v);print(json.dumps(dict(package=pkginfo,rays=len(errs),max_error=float(max(errs)),files=len(manifest['files']),prepared_not_physical_pass=True)))

if __name__=='__main__':
 try:main()
 except BaseException:save('SLOPE5_PREPARE_ERROR.json',dict(error=traceback.format_exc(),CPU_only=True,do_not_blind_replay=True));raise
