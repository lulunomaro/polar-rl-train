"""New analytic10degree normal/query contract and unique frozen scope; CPU only."""
from slope_io import *
import ast,zipfile,importlib.util,traceback
import numpy as np
PROTOCOL='approved_E1_SLOPE_derived10deg_actualray_analyticnormal_mirrored_fullroute_behavior_v1'

def main():
    context=json.loads(sorted(R.glob('SLOPE10_PREPARATION_CONTEXT_ACTUAL_[0-9]*.json'))[-1].read_bytes())
    assert context['new138_not_yet_published'] and context['actual_worker']['attention'] is None
    decision=json.loads((R/'SLOPE137_COMPLETE_SCOPE_DECISION.json').read_bytes());assert decision['scoped8deg_mirrored_frozen_behavior_accepted']
    parent_info=json.loads((R/'SLOPE137_PREPARED.json').read_bytes())['package'];parent=Path(parent_info['path']);assert H(parent.read_bytes())==parent_info['sha256']
    with zipfile.ZipFile(parent) as z:members={n:z.read(n) for n in z.namelist()}
    manifest=json.loads(members['SOURCE_MANIFEST.json']);assert all(H(members[n])==h for n,h in manifest['files'].items())
    impl=D/'next_slope10_scope';assert not impl.exists();impl.mkdir()
    for name in ('slope10_geometry.py','slope10_profile.json'):(impl/name).write_bytes((D/'next_slope10_cpu'/name).read_bytes())
    gp=impl/'slope10_geometry.py';profile=json.loads((impl/'slope10_profile.json').read_bytes());assert profile['angle_deg']==10.
    spec=importlib.util.spec_from_file_location('slope10_138_geometry',gp);c=importlib.util.module_from_spec(spec);spec.loader.exec_module(c)
    # Independent triangle intersections include normals, mirrors, actual float32 world origins and joins.
    def hit(origin,v,f):
        direction=np.array([0.,0.,-1.]);found=[]
        for face in f:
            a,b,z=v[face];e1,e2=b-a,z-a;p=np.cross(direction,e2);det=e1@p
            if abs(det)<1e-12:continue
            delta=origin-a;u=(delta@p)/det;q=np.cross(delta,e1);w=(direction@q)/det;t=(e2@q)/det
            if u>=-1e-12 and w>=-1e-12 and u+w<=1+1e-12 and t>=0:
                normal=np.cross(e1,e2);normal/=np.linalg.norm(normal);found.append((float(t),normal))
        assert found
        closest=min(x[0] for x in found);return origin+closest*direction,[n for t,n in found if abs(t-closest)<1e-10]
    centers=(np.arange(80)//2+.5)*9.-180.;orientation=np.where(np.arange(80)%2==0,1.,-1.);requested=np.linspace(-1.4,1.4,35)
    origins=np.asarray(centers[:,None]+orientation[:,None]*requested,dtype=np.float32).astype(np.float64)
    actual=(origins-centers[:,None])*orientation[:,None];angle=np.deg2rad(10.);height=2.*np.tan(angle)
    errors=[];normal_errors=[];joins=[]
    for i in range(80):
        o=orientation[i];mesh,_=c.make_mesh((9.,9.),o==-1);v=mesh.vertices.copy();v[:,:2]-=4.5
        for x in actual[i]:
            position,normals=hit(np.array([o*x,0.,2.]),v,mesh.faces)
            expected=np.array([-o*np.sin(angle),0.,np.cos(angle)]) if -1.<x<1. else np.array([0.,0.,1.])
            errors.append(abs(position[2]-np.clip((x+1.)/2.,0.,1.)*height));normal_errors.append(min(float(np.max(abs(n-expected))) for n in normals))
    for o in (1.,-1.):
        mesh,_=c.make_mesh((9.,9.),o==-1);v=mesh.vertices.copy();v[:,:2]-=4.5
        for x in (-1.,1.):
            position,normals=hit(np.array([o*x,0.,2.]),v,mesh.faces)
            slope=np.array([-o*np.sin(angle),0.,np.cos(angle)]);flat=np.array([0.,0.,1.])
            assert all(min(np.max(abs(n-slope)),np.max(abs(n-flat)))<1e-10 for n in normals)
            joins.append(dict(orientation=o,canonical_x=x,intersected_triangle_normals=[n.tolist() for n in normals],height_m=float(position[2]),join_normal_ambiguity_explicit=True))
    assert max(errors)<1e-10 and max(normal_errors)<1e-10
    assert not np.any(np.abs(np.abs(actual)-1.)<=1e-10)
    old=members['runtime/isaac/mod4/frozen_history_flat.py'].decode()
    new=old.replace('from slope8_geometry import configure_slope as configure_intro','from slope10_geometry import configure_slope as configure_intro').replace('np.deg2rad(8.)','np.deg2rad(10.)').replace('angle_deg=8.','angle_deg=10.').replace('continuous8deg','continuous10deg').replace('approved_E1_SLOPE_derived8deg_actualray_mirrored_fullroute_behavior_v2',PROTOCOL)
    oldcheck="    assert sample['hit'].all() and (sample['normal'][...,2]>.99).all()\n"
    assert new.count(oldcheck)==1
    newcheck="""    assert sample['hit'].all()
    sampled_normals=cpu(sample['normal']).astype(np.float64)
    angle=np.deg2rad(10.)
    expected_normals=np.zeros_like(sampled_normals);expected_normals[:,:,2]=1.
    on_ramp=(actual_samples>-1.)&(actual_samples<1.)
    assert not np.any(np.abs(np.abs(actual_samples)-1.)<=1e-10)
    expected_normals[:,:,0]=np.where(on_ramp,-orientation[:,None]*np.sin(angle),0.)
    expected_normals[:,:,2]=np.where(on_ramp,np.cos(angle),1.)
    assert np.max(abs(np.linalg.norm(sampled_normals,axis=-1)-1.))<=1e-6
    assert (sampled_normals[:,:,2]>0.).all()
    sample_normal_error=float(np.max(abs(sampled_normals-expected_normals)))
    assert sample_normal_error<=1e-6
"""
    new=new.replace(oldcheck,newcheck).replace("actual_sampled_normals=js(sample['normal']),", "actual_sampled_normals=js(sample['normal']),expected_analytic_sampled_normals=expected_normals.tolist(),analytic_normal_max_abs_error=sample_normal_error,normal_component_tolerance=1e-6,normal_unit_tolerance=1e-6,query_samples_avoid_join_normal_ambiguity=True,new10deg_geometry_normal_contract=True,old8deg_normal_z_point99_check_not_production_threshold=True,")
    loop=lambda s:next(n for n in next(x for x in ast.parse(s).body if isinstance(x,ast.FunctionDef) and x.name=='main').body if isinstance(n,ast.For) and ast.unparse(n.target)=='step')
    assert ast.dump(loop(old),include_attributes=False)==ast.dump(loop(new),include_attributes=False)
    # The preliminary two support-flat probes retain their old normal_z>.99 requirement.
    assert "(preliminary['normal'][...,2]>.99).all()" in new and 'assert np.max(abs(sampled-expected))<=1e-6' in new
    compile(new,'frozen_history_flat_SLOPE138.py','exec');(impl/'frozen_history_flat_SLOPE138.py').write_text(new,encoding='utf8')
    changes={'runtime/isaac/mod4/frozen_history_flat.py':new.encode(),'runtime/isaac/mod4/slope10_geometry.py':gp.read_bytes(),'runtime/isaac/mod4/slope10_profile.json':(impl/'slope10_profile.json').read_bytes()}
    members.update(changes);manifest.update(protocol=PROTOCOL,parent_archive_sha256=parent_info['sha256'],current_geometry_revision004='E1_SLOPE10',
      explicit_new10deg_analytic_triangle_normal_query_contract=True,ground_tolerance_m=1e-6,normal_component_tolerance=1e-6,normal_unit_tolerance=1e-6,
      unchanged_production_ordinary_integrity_contact_hardware_thresholds=True,current_frozen_scope=dict(angle_deg=10.,ramp_length_m=2.,mirrored=True,approach_m=.4,after_support_m=.2,steps=1500,num_envs=80,seconds=15,optimizer_updates=0))
    manifest['files']={n:H(b) for n,b in members.items() if n!='SOURCE_MANIFEST.json'};manifest['new_or_changed_members']={n:H(b) for n,b in changes.items()};members['SOURCE_MANIFEST.json']=json.dumps(manifest,indent=2).encode()
    pkg=impl/'e1-slope10-derived-actualray-analyticnormal-mirrored-fullroute-frozen-v1.zip';assert not pkg.exists()
    with zipfile.ZipFile(pkg,'w',zipfile.ZIP_DEFLATED) as z:
        for name,b in members.items():z.writestr(name,b)
    with zipfile.ZipFile(pkg) as z:assert all(H(z.read(n))==h for n,h in manifest['files'].items())
    prior=json.loads((R/'SLOPE137_PUBLISHED.json').read_bytes())['jobs'][0];job=dict(prior);job.update(job_id='clk2500-closure-episode-d3-138-e1-slope10-source404-analyticnormal-mirrored-fullroute-flat',role='E1_SLOPE10_complete135_137_source404_frozen_anchor',protocol=PROTOCOL,actual_behavior_scope='Approved single angle8to10: new explicit10degree analyticnormal actualfloat32 query contract; complete2m mirrored ramp .4m approach200mm aftersupport, frozen only.')
    job['artifacts']=dict(job['artifacts']);info=dict(path=str(pkg.resolve()),bytes=pkg.stat().st_size,sha256=H(pkg.read_bytes()));job['artifacts']['runtime']=dict(path=E+'/artifacts/'+pkg.name,bytes=info['bytes'],sha256=info['sha256'])
    contract=dict(epoch=time.time(),trial_id='E1-SLOPE10-ANALYTICNORMAL-ACTUALQUERY-CPU-01',independent_actual_float32_input_triangle_rays=len(errors),max_height_error_m=float(max(errors)),max_normal_component_error=float(max(normal_errors)),join_cases=joins,actual_query_grid_avoids_joins=True,expected_slope_normal_z=float(np.cos(angle)),old8deg_z_above_point99_not_valid_for_new10deg_geometry=True,new_explicit_normal_component_tolerance=1e-6,new_explicit_unit_tolerance=1e-6,original_ground_tolerance_m=1e-6,support_flat_normal_z_above_point99_preserved=True,production_normal_health_contact_hardware_tolerances_unchanged=True,full_control_loop_AST_exact=True,CPU_only_not_physical_pass=True)
    save('SLOPE10_NORMAL_QUERY_CPU_CONTRACT_REVIEW.json',contract)
    row=dict(epoch=time.time(),trial_id='E1-SLOPE10-FROZEN138-PREPARE-01',package=info,jobs=[job],normal_query_contract=contract,profile=profile,source_checkpoint=decision['source_checkpoint'],source_complete135_137=True,source5deg_terraincommand_no8deg_trained_state=True,immutable_files_map_exact=len(manifest['files']),changed_members={n:H(b) for n,b in changes.items()},old_unchanged_members=len(members)-len(changes)-1,new_physical_result_pending=True,no_learning_or_GPU_queue_budget_write=True)
    save('SLOPE138_PREPARED.json',row);print(json.dumps(dict(package=info,rays=len(errors),height_error_m=max(errors),normal_error=max(normal_errors),files=len(manifest['files']),new_scope_CPU_prepared_only=True)))

if __name__=='__main__':
    try:main()
    except BaseException:save('SLOPE138_PREPARE_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),CPU_only=True,no_blind_replay=True));raise
