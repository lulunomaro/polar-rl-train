"""One new CURB package; old completed route evidence is never replayed."""
from curb_io import *
import ast, copy, importlib.util, traceback, zipfile
import numpy as np

def main():
    save('CURB_FROZEN_PREPARE_STARTED.json',dict(epoch=time.time(),trial_id='E1-CURB20-MIRRORED-FROZEN-SCOPE-01',once=True,CPU_only=True))
    save('CURB_LOCAL_READONLY_LOCATOR_ERRORS.json',dict(epoch=time.time(),trial_id='E1-CURB20-LOCAL-READER-01',
        errors=[dict(operation='Get-Content or rg',incorrect='N/episode_reviewed_payload/isaac/mod4/ppo_e1_command_retention_episode_reviewed.py',actual='train_e1_retention_episode_reviewed_resume_ppo.py'),
        dict(incorrect='L/prepare_g3_learning_scope_once.py',actual='G/prepare_g3_learning_scope_once.py'),
        dict(incorrect='Q/prepare_paired_approach_scope_once.py',actual='Q/prepare_paired_approach_diagnostic.py'),
        dict(incorrect='Q/review_g3_observation_actual.py',actual='L/review_g3_observation_actual.py'),
        dict(incorrect='rg Windows literal *review*.py path',actual='rg --files then filter exact filenames'),
        dict(operation='local next(probe.json) body_names',error="KeyError: 'body_names'",cause='selected a spin result instead of terrain result',repair='select full_route_raw schema before body_names')],
        all_read_only_before_remote_or_GPU_mutation=True,original_tool_errors_retained=True,no_training_or_physics_fault=True))
    M=W/'MOD4_MOE_TERRAIN_SUBEXPERT_REVISION_20261010'
    p=M/'next_curb_cpu/curb20_profile.json';raw=p.read_bytes()
    q=D/'implementation/curb20_profile.json';assert not q.exists();q.write_bytes(raw)
    sys.path.insert(0,str(D/'implementation'));import curb20_geometry as c
    spec=importlib.util.spec_from_file_location('curb_independent_ray',M/'prepare_curb_component_once.py')
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    errs=[];walls=[]
    for mirrored in (False,True):
        mesh,origin=c.make_mesh((9.,9.),mirrored)
        v=mesh.vertices.copy();v[:,:2]-=4.5;orient=-1 if mirrored else 1
        for x in np.linspace(-4.4,4.4,31):
            for y in (-4.,0.,4.):
                hit=module.ray(np.array([orient*x,y,1.]),np.array([0.,0.,-1.]),v,mesh.faces)
                errs.append(abs(hit[2]-(0. if x<-.075 else .020)))
        wall=module.ray(np.array([-orient,0.,.010]),np.array([float(orient),0.,0.]),v,mesh.faces)
        assert abs(wall[0]-orient*(-.075))<1e-10;walls.append(wall.tolist())
    assert max(errs)<1e-10
    source=W/'MOD4_E1_G3_MATCHED_REVIEW_20261010/artifacts/e1-g3-derived35mm-paired-approach040-frozen-v2.zip'
    assert H(source.read_bytes())=='858ad4ef431f188f3275dc8b3c3690bf1d987a5c074f9aed698e15343ad66d2b'
    with zipfile.ZipFile(source) as z:
        members={n:z.read(n) for n in z.namelist()}
    manifest=json.loads(members['SOURCE_MANIFEST.json'])
    for name,h in manifest['files'].items():assert H(members[name])==h,name
    old=members['runtime/isaac/mod4/frozen_history_flat.py'].decode()
    new=old.replace('from g3_cad_wave_geometry import configure_g3 as configure_intro','from curb20_geometry import configure_curb as configure_intro')
    first=new.index('    from g3_cad_wave_geometry import profile\n')
    last=new.index('    assert e.physics_dt',first)
    prefix='''    support = 0.4
    def whole_route_boundary(env):
        xy = env.scene['robot'].data.root_pos_w[:, :2] - env._g1_whole_route_centers
        return (xy[:, 0].abs() > 3.5) | (xy[:, 1].abs() > 3.0)
    cfg.terminations.rough_route_boundary.func = whole_route_boundary
    assert cfg.terminations.rough_route_boundary.time_out is True
    e = E1ResetEvidenceLearningEnv(cfg=cfg)
    r = e.scene['robot']
    e._g1_whole_route_centers = torch.as_tensor(centers, device=e.device, dtype=e.scene.env_origins.dtype)
    ray = query(e)
    xy = np.repeat(centers[:,None,:],2,axis=1)
    xy[:,0,0]-=1.;xy[:,1,0]+=1.
    ceiling=float(ray.geometry.vertices[:,2].max())+2.
    preliminary=ray.cast(torch.as_tensor(np.concatenate((xy,np.full((80,2,1),ceiling)),axis=-1),device=e.device,dtype=torch.float32),10.)
    preliminary_height=cpu(preliminary['height'])
    assert preliminary['hit'].all() and (preliminary['normal'][...,2]>.99).all()
    orientation=np.where(preliminary_height[:,1]>preliminary_height[:,0],1.,-1.)
    assert np.sum(orientation==1)==40 and np.sum(orientation==-1)==40
    assert np.max(abs(np.ptp(preliminary_height,axis=1)-.020))<=1e-6
    assert np.max(abs(np.min(preliminary_height,axis=1)))<=1e-6
    starts=centers.copy()
    starts[:,0]+=orientation*np.where(ids%3==1,.075+support,-.075-support)
    assert len(np.unique(np.stack((tile_rows,tile_cols),axis=-1),axis=0))==80
    e.scene.env_origins[:,:2]=torch.as_tensor(starts,device=e.device,dtype=e.scene.env_origins.dtype)
    e.reset()
    root_xy=r.data.root_pos_w.torch[:,:2]
    assert isinstance(root_xy,torch.Tensor) and root_xy.dtype==torch.float32
    assert torch.allclose(root_xy,torch.as_tensor(starts,device=e.device,dtype=root_xy.dtype),atol=1e-6,rtol=0)
    samples=np.linspace(-.475,.475,35)
    xy=np.repeat(centers[:,None,:],35,axis=1)
    xy[:,:,0]+=orientation[:,None]*samples
    sample=ray.cast(torch.as_tensor(np.concatenate((xy,np.full((80,35,1),ceiling)),axis=-1),device=e.device,dtype=root_xy.dtype),10.)
    assert sample['hit'].all() and (sample['normal'][...,2]>.99).all()
    sampled=cpu(sample['height']);expected=np.where(samples<-.075,0.,.020)
    assert np.max(abs(sampled-expected[None,:]))<=1e-6
    wheel_ids=[r.body_names.index(n) for n in ('left_wheel','right_wheel')]
    initial_wheel=cpu(r.data.body_link_pos_w)[:,wheel_ids,:]
    initial_u=(initial_wheel[:,:,0]-centers[:,None,0])*orientation[:,None]
    assert (initial_u[ids%3!=1]<-.075).all() and (initial_u[ids%3==1]>.075).all()
    route_scope=dict(tile_rows=tile_rows.tolist(),tile_cols=tile_cols.tolist(),family='derived20mm_vertical_curb_strip150',tile_centers=centers.tolist(),requested_starts=starts.tolist(),size_m=size.tolist(),flat_support_margin_m=support,orientation=orientation.tolist(),riser_canonical_x_m=-.075,strip_end_canonical_x_m=.075,height_m=.020,strip_width_m=.150,required_after_support_m=.200,actual_sampled_canonical_x_m=samples.tolist(),actual_sampled_ground=sampled.tolist(),actual_sampled_normals=js(sample['normal']),actual_authored_ground_query_passed=True,initial_wheel_link_positions=initial_wheel.tolist(),initial_two_wheels_on_requested_side=True,vertical_riser_unsmoothed=True,not_actual_RM002_height=True,not_stair_flight=True,termination_change='evaluation-only declared truncation at abs x from tile center3.5m or abs y3m',production_boundary_unchanged=True,not_training_or_RM70mm=True)
'''
    new=new[:first]+prefix+new[last:]
    new=new.replace("targets = torch.tensor([0.3, -0.3, 0.0], device=e.device)[groups]", "targets = torch.tensor([0.3, -0.3, 0.0], device=e.device)[groups] * torch.as_tensor(orientation,device=e.device,dtype=torch.float32)")
    new=new.replace("target = float((0.3, -0.3, 0.0)[i])", "target = data['targets_m_s'][ids][None,:]")
    new=new.replace('command_vx_m_s=target,','command_vx_m_s=target[0].tolist(),')
    new=new.replace('approved_E1_G3_derived35mm_paired_approach040_behavior_v2',PROTOCOL)
    # The actual stepping, health, force integral and callback auditor are exact.
    oa=ast.parse(old);na=ast.parse(new)
    om=next(n for n in oa.body if isinstance(n,ast.FunctionDef) and n.name=='main')
    nm=next(n for n in na.body if isinstance(n,ast.FunctionDef) and n.name=='main')
    of=next(n for n in om.body if isinstance(n,ast.For) and ast.unparse(n.target)=='step')
    nf=next(n for n in nm.body if isinstance(n,ast.For) and ast.unparse(n.target)=='step')
    assert ast.dump(of,include_attributes=False)==ast.dump(nf,include_attributes=False)
    compile(new,'frozen_history_flat_CURB132.py','exec')
    out=D/'implementation/frozen_history_flat_CURB132.py';assert not out.exists();out.write_bytes(new.encode())
    changes={'runtime/isaac/mod4/frozen_history_flat.py':new.encode(),
        'runtime/isaac/mod4/curb20_geometry.py':(D/'implementation/curb20_geometry.py').read_bytes(),
        'runtime/isaac/mod4/curb20_profile.json':raw}
    members.update(changes)
    manifest['files']={n:H(b) for n,b in members.items() if n!='SOURCE_MANIFEST.json'}
    # Historic sidecars remain explicit inherited references; current overlay is exact.
    manifest.update(protocol=PROTOCOL,new_or_changed_members={n:H(b) for n,b in changes.items()},
        parent_archive_sha256=H(source.read_bytes()),current_geometry_revision004='E1_CURB20',
        current_geometry_is_G3_wave=False,derived_not_actual_RM002_height=True,
        immutable_original_members_preserved_except_dispatcher=True,
        inherited_G1_G2_G3_annotations_historical_only=True,
        all_original_D0_D7_and_assets_byteexact_except_geometry_import=True,
        current_frozen_scope=dict(height_m=.020,strip_width_m=.150,mirrored=True,approach_m=.4,
            after_support_m=.2,steps=1500,num_envs=80,seconds=15,optimizer_updates=0))
    members['SOURCE_MANIFEST.json']=json.dumps(manifest,indent=2).encode()
    for n,h in manifest['files'].items():assert H(members[n])==h
    unchanged=[n for n in members if n not in changes and n!='SOURCE_MANIFEST.json']
    with zipfile.ZipFile(source) as z:
        assert all(members[n]==z.read(n) for n in unchanged)
    (D/'artifacts').mkdir(exist_ok=True)
    pkg=D/'artifacts/e1-curb20-derived-mirrored-fullroute-frozen-v1.zip';assert not pkg.exists()
    with zipfile.ZipFile(pkg,'w',zipfile.ZIP_DEFLATED) as z:
        for n,b in members.items():z.writestr(n,b)
    with zipfile.ZipFile(pkg) as z:
        check=json.loads(z.read('SOURCE_MANIFEST.json'))
        assert all(H(z.read(n))==h for n,h in check['files'].items())
    template=json.loads((W/'MOD4_E1_G3_35MM_SCOPE_PREPARE_20261010/reports/MANIFEST_TEMPLATE.json').read_bytes())
    cp=dict(path=E+'/artifacts/e1-stable-own-'+SHA+'.pt',bytes=17615538,sha256=SHA)
    artifact=dict(path=E+'/artifacts/'+pkg.name,bytes=pkg.stat().st_size,sha256=H(pkg.read_bytes()))
    template.update(job_id='clk2500-closure-episode-d3-132-e1-curb20-source364-mirrored-fullroute-flat',
        role='E1_CURB20_source364_frozen_anchor',protocol=PROTOCOL,actual_curriculum_expert='E1_CURB',
        expert_plan_revision='MOD4-MOE-TERRAIN-SUBEXPERT-REVISION-004',
        actual_behavior_scope='New derived20mm vertical curb,150mm strip continuous upper platform; mirrored actual lower/upper starts,two-wheel full curb crossing and200mm after support. Frozen only.',
        artifacts=dict(runtime=artifact,checkpoint=cp),scope_pending_actual_review=True)
    v=dict(epoch=time.time(),trial_id='E1-CURB20-MIRRORED-FROZEN-SCOPE-01',CPU_component_and_package_passed=True,
        package=dict(path=str(pkg.resolve()),bytes=artifact['bytes'],sha256=artifact['sha256']),jobs=[template],
        independent_new_SDK_coordinate_ray_count=len(errs),max_vertical_ray_error_m=max(errs),vertical_wall_hits=walls,
        old_CPU_component_SHA=H(p.read_bytes()),old_package_SHA=H(source.read_bytes()),
        immutable_files_map_exact=len(manifest['files']),unchanged_old_members=len(unchanged),changed_members={n:H(b) for n,b in changes.items()},
        physical_step_health_hardware_contact_auditor_AST_exact=True,no_GPU_yet=True,no_PPO_or_budget_write=True,
        SDK_native_CUDA_fullsave_fullresume_PPO_pending=True,new_budget_seconds=0)
    save('CURB_FROZEN_PREPARED.json',v)
    print(json.dumps(dict(package_SHA=artifact['sha256'],bytes=artifact['bytes'],files=len(manifest['files']),rays=len(errs),max_error=max(errs),prepared_not_physical_pass=True)))
if __name__=='__main__':
    try:main()
    except Exception:
        save('CURB_FROZEN_PREPARE_ERROR.json',dict(epoch=time.time(),error=traceback.format_exc(),CPU_only=True,no_production_mutation=True,do_not_replay_once=True));raise
