"""Exactown80 factoryprefixes, source-onlyderivation;importsSDK onlyinsidecall."""
from types import SimpleNamespace
from pathlib import Path
import hashlib
from e1_fresh_runtime_bridge import attach_fresh_guard,fresh_full_dr_audit

def cpu(x):return x.detach().cpu().numpy().copy() if hasattr(x,'detach') else x.torch.detach().cpu().numpy().copy()
def js(x):return x.detach().cpu().tolist() if hasattr(x,'detach') else x.torch.detach().cpu().tolist()
def assignments(e):
 return dict(action={k:dict(delay_us=js(g['lag_steps']*2500),episode=js(g['episode'])) for k,g in e._physics_action_delay.queue.groups.items()},spring=dict(factor=js(e._spring_pressure.component.factor),episode=js(e._spring_pressure.component.episode)),gas=dict(factor=js(e._gas_damping.component.factor),episode=js(e._gas_damping.component.episode)),COM=dict(delta_m=js(e._chassis_com.component.delta_m),episode=js(e._chassis_com.component.episode)),PD=dict(factors={k:js(v) for k,v in e._explicit_pd.component.factor.items()},episode=js(e._explicit_pd.component.episode)),feedback_delay=js(e._feedback_delay_mild.lag_steps))

def _factory_curb_protected878(descriptor,case,identity,torch,np,wp,tensor):
    args=SimpleNamespace(steps=750,num_envs=80,seed=20260928,dr_profile='white_v3',device='cuda:0',output=str(case/'ORIGINAL_ROUTE_QUERY.json'))
    import mod4_task as task
    from e1_reset_evidence_training_env import E1ResetEvidenceLearningEnv
    from e1_terrain_training_health import declared_truncation_terms
    from e1_full_pose_reset import query
    from mod4v1_fresh_dr_guard import configure_new_task
    from curb20_geometry import configure_curb as configure_intro
    assert args.steps == 750 and args.num_envs == 80 and (args.seed == 20260928) and (args.dr_profile == 'white_v3')
    torch.manual_seed(args.seed)
    cfg = task.Mod4EnvCfg()
    cfg.seed = args.seed
    cfg.scene.num_envs = args.num_envs
    cfg.terminations.mimic.params={**cfg.terminations.mimic.params,"threshold":.01}
    configure_new_task(cfg,identity)
    cfg.sim.device=args.device
    for k,v in dict(gpu_max_rigid_contact_count=2**20,gpu_max_rigid_patch_count=2**16,gpu_found_lost_pairs_capacity=2**18,gpu_found_lost_aggregate_pairs_capacity=2**22,gpu_total_aggregate_pairs_capacity=2**20).items():setattr(cfg.sim.physics,k,v)
    recipe = configure_intro(cfg)
    gen = cfg.scene.terrain.terrain_generator
    assert gen.curriculum and gen.num_rows == gen.num_cols == 40
    keys = list(gen.sub_terrains)
    weights = np.array([gen.sub_terrains[k].proportion for k in keys])
    weights /= weights.sum()
    family = np.array([int(np.min(np.where(i / 40 + 0.001 < np.cumsum(weights))[0])) for i in range(40)])
    cols = np.flatnonzero(family == keys.index('random_uniform_for_rm'))
    assert len(cols) == 6
    size = np.asarray(gen.size, dtype=float)
    assert np.array_equal(size, [9.0, 9.0])
    ids = np.arange(80)
    tile_rows = ids // 2
    tile_cols = cols[ids % 2]
    centers = np.stack(((tile_rows + 0.5) * size[0] - 20 * size[0], (tile_cols + 0.5) * size[1] - 20 * size[1]), axis=-1)
    support = 0.4
    def whole_route_boundary(env):
        xy = env.scene['robot'].data.root_pos_w[:, :2] - env._g1_whole_route_centers
        return (xy[:, 0].abs() > 3.5) | (xy[:, 1].abs() > 3.0)
    cfg.terminations.rough_route_boundary.func = whole_route_boundary
    assert cfg.terminations.rough_route_boundary.time_out is True
    e = E1ResetEvidenceLearningEnv(cfg=cfg)
    r = e.scene['robot']
    guard=attach_fresh_guard(e,identity,torch,tensor)
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
    audit_before=fresh_full_dr_audit(e,guard,tensor)
    root_xy=tensor(r.data.root_pos_w)[:,:2]
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
    actual_world_ray_origins=cpu(torch.as_tensor(np.concatenate((xy,np.full((80,35,1),ceiling)),axis=-1),device=e.device,dtype=root_xy.dtype))
    from curb_worldmesh_query_contract_v1 import expected_ground
    expected_actual_ground,world_mesh_receipts,query_world_triangles=expected_ground(ray.geometry.vertices,ray.geometry.faces,centers,actual_world_ray_origins)
    actual_query_height_error=float(np.max(abs(sampled-expected_actual_ground)))
    assert actual_query_height_error<=1e-6
    query_evidence_path=Path(args.output).with_name(Path(args.output).name+'.worldmesh_query.npz')
    assert not query_evidence_path.exists()
    np.savez_compressed(query_evidence_path,actual_world_ray_origins=actual_world_ray_origins,actual_canonical_ray_x=(actual_world_ray_origins[:,:,0].astype(np.float64)-centers[:,None,0])*orientation[:,None],actual_sampled_ground=sampled,expected_actual_ground=expected_actual_ground,ideal_profile_ground=np.broadcast_to(expected[None,:],sampled.shape),world_triangles=query_world_triangles)
    assert all((r['mirrored']==bool(o<0)) for r,o in zip(world_mesh_receipts,orientation))
    route_scope.update(actual_world_ray_origins=actual_world_ray_origins.tolist(),actual_query_height_error_m=actual_query_height_error,actual_query_ground_tolerance_m=1e-6,expected_actual_sampled_ground=expected_actual_ground.tolist(),world_mesh_receipts=world_mesh_receipts,query_worldmesh_evidence=dict(path=str(query_evidence_path),bytes=query_evidence_path.stat().st_size,sha256=hashlib.sha256(query_evidence_path.read_bytes()).hexdigest()))
    assert e.physics_dt == 0.0025 and e.step_dt == 0.02 and (r.data.joint_pos.shape == (80, 30))
    assert torch.equal(tensor(r.data.joint_pos), e._rough_probe_expected_q)
    initial = dict(root=js(r.data.root_state_w), q=js(r.data.joint_pos), parameters=e.chassis_pd_audit(), assignments=assignments(e), reset=e._rough_probe_reset_receipt, actual_all_physical_parameters=audit_before['actual_parameters'])
    decl = declared_truncation_terms(e.termination_manager)
    names = tuple(e.termination_manager.active_terms)
    cmd = e.command_manager.get_term('twist')
    cmd.set_manual_evaluation_mode()
    groups = torch.arange(80, device=e.device) % 3
    targets = torch.tensor([0.3, -0.3, 0.0], device=e.device)[groups] * torch.as_tensor(orientation,device=e.device,dtype=torch.float32)
    return dict(env=e,robot=r,guard=guard,audit_before=audit_before,route_scope=route_scope,command=cmd,manual=True,groups=groups,targets=targets)


def _factory_curb_independent113(descriptor,case,identity,torch,np,wp,tensor):
    args=SimpleNamespace(steps=750,num_envs=80,seed=20260928,dr_profile='white_v3',device='cuda:0',output=str(case/'ORIGINAL_ROUTE_QUERY.json'))
    import mod4_task as task
    from e1_reset_evidence_training_env import E1ResetEvidenceLearningEnv
    from e1_terrain_training_health import declared_truncation_terms
    from e1_full_pose_reset import query
    from mod4v1_fresh_dr_guard import configure_new_task
    from curb20_geometry import configure_curb as configure_intro
    assert args.steps == 750 and args.num_envs == 80 and (args.seed == 20260928) and (args.dr_profile == 'white_v3')
    torch.manual_seed(args.seed)
    cfg = task.Mod4EnvCfg()
    cfg.seed = args.seed
    cfg.scene.num_envs = args.num_envs
    cfg.terminations.mimic.params={**cfg.terminations.mimic.params,"threshold":.01}
    configure_new_task(cfg,identity)
    cfg.sim.device=args.device
    for k,v in dict(gpu_max_rigid_contact_count=2**20,gpu_max_rigid_patch_count=2**16,gpu_found_lost_pairs_capacity=2**18,gpu_found_lost_aggregate_pairs_capacity=2**22,gpu_total_aggregate_pairs_capacity=2**20).items():setattr(cfg.sim.physics,k,v)
    recipe = configure_intro(cfg)
    gen = cfg.scene.terrain.terrain_generator
    assert gen.curriculum and gen.num_rows == gen.num_cols == 40
    keys = list(gen.sub_terrains)
    weights = np.array([gen.sub_terrains[k].proportion for k in keys])
    weights /= weights.sum()
    family = np.array([int(np.min(np.where(i / 40 + 0.001 < np.cumsum(weights))[0])) for i in range(40)])
    cols = np.flatnonzero(family == keys.index('random_uniform_for_rm'))
    assert len(cols) == 6
    size = np.asarray(gen.size, dtype=float)
    assert np.array_equal(size, [9.0, 9.0])
    ids = np.arange(80)
    tile_rows = ids // 2
    tile_cols = cols[ids % 2]
    centers = np.stack(((tile_rows + 0.5) * size[0] - 20 * size[0], (tile_cols + 0.5) * size[1] - 20 * size[1]), axis=-1)
    support = 0.4
    def whole_route_boundary(env):
        xy = env.scene['robot'].data.root_pos_w[:, :2] - env._g1_whole_route_centers
        return (xy[:, 0].abs() > 3.5) | (xy[:, 1].abs() > 3.0)
    cfg.terminations.rough_route_boundary.func = whole_route_boundary
    assert cfg.terminations.rough_route_boundary.time_out is True
    e = E1ResetEvidenceLearningEnv(cfg=cfg)
    r = e.scene['robot']
    guard=attach_fresh_guard(e,identity,torch,tensor)
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
    audit_before=fresh_full_dr_audit(e,guard,tensor)
    root_xy=tensor(r.data.root_pos_w)[:,:2]
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
    actual_world_ray_origins=cpu(torch.as_tensor(np.concatenate((xy,np.full((80,35,1),ceiling)),axis=-1),device=e.device,dtype=root_xy.dtype))
    from curb_worldmesh_query_contract_v1 import expected_ground
    expected_actual_ground,world_mesh_receipts,query_world_triangles=expected_ground(ray.geometry.vertices,ray.geometry.faces,centers,actual_world_ray_origins)
    actual_query_height_error=float(np.max(abs(sampled-expected_actual_ground)))
    assert actual_query_height_error<=1e-6
    query_evidence_path=Path(args.output).with_name(Path(args.output).name+'.worldmesh_query.npz')
    assert not query_evidence_path.exists()
    np.savez_compressed(query_evidence_path,actual_world_ray_origins=actual_world_ray_origins,actual_canonical_ray_x=(actual_world_ray_origins[:,:,0].astype(np.float64)-centers[:,None,0])*orientation[:,None],actual_sampled_ground=sampled,expected_actual_ground=expected_actual_ground,ideal_profile_ground=np.broadcast_to(expected[None,:],sampled.shape),world_triangles=query_world_triangles)
    assert all((r['mirrored']==bool(o<0)) for r,o in zip(world_mesh_receipts,orientation))
    route_scope.update(actual_world_ray_origins=actual_world_ray_origins.tolist(),actual_query_height_error_m=actual_query_height_error,actual_query_ground_tolerance_m=1e-6,expected_actual_sampled_ground=expected_actual_ground.tolist(),world_mesh_receipts=world_mesh_receipts,query_worldmesh_evidence=dict(path=str(query_evidence_path),bytes=query_evidence_path.stat().st_size,sha256=hashlib.sha256(query_evidence_path.read_bytes()).hexdigest()))
    assert e.physics_dt == 0.0025 and e.step_dt == 0.02 and (r.data.joint_pos.shape == (80, 30))
    assert torch.equal(tensor(r.data.joint_pos), e._rough_probe_expected_q)
    initial = dict(root=js(r.data.root_state_w), q=js(r.data.joint_pos), parameters=e.chassis_pd_audit(), assignments=assignments(e), reset=e._rough_probe_reset_receipt, actual_all_physical_parameters=audit_before['actual_parameters'])
    decl = declared_truncation_terms(e.termination_manager)
    names = tuple(e.termination_manager.active_terms)
    cmd = e.command_manager.get_term('twist')
    cmd.set_manual_evaluation_mode()
    groups = torch.arange(80, device=e.device) % 3
    targets = torch.tensor([0.3, -0.3, 0.0], device=e.device)[groups] * torch.as_tensor(orientation,device=e.device,dtype=torch.float32)
    return dict(env=e,robot=r,guard=guard,audit_before=audit_before,route_scope=route_scope,command=cmd,manual=True,groups=groups,targets=targets)


def _factory_slope135(descriptor,case,identity,torch,np,wp,tensor):
    args=SimpleNamespace(steps=750,num_envs=80,seed=20260928,dr_profile='white_v3',device='cuda:0',output=str(case/'ORIGINAL_ROUTE_QUERY.json'))
    import mod4_task as task
    from e1_reset_evidence_training_env import E1ResetEvidenceLearningEnv
    from e1_terrain_training_health import declared_truncation_terms
    from e1_full_pose_reset import query
    from mod4v1_fresh_dr_guard import configure_new_task
    from slope5_geometry import configure_slope as configure_intro
    assert args.steps == 750 and args.num_envs == 80 and (args.seed == 20260928) and (args.dr_profile == 'white_v3')
    torch.manual_seed(args.seed)
    cfg = task.Mod4EnvCfg()
    cfg.seed = args.seed
    cfg.scene.num_envs = args.num_envs
    cfg.terminations.mimic.params={**cfg.terminations.mimic.params,"threshold":.01}
    configure_new_task(cfg,identity)
    recipe = configure_intro(cfg)
    gen = cfg.scene.terrain.terrain_generator
    assert gen.curriculum and gen.num_rows == gen.num_cols == 40
    keys = list(gen.sub_terrains)
    weights = np.array([gen.sub_terrains[k].proportion for k in keys])
    weights /= weights.sum()
    family = np.array([int(np.min(np.where(i / 40 + 0.001 < np.cumsum(weights))[0])) for i in range(40)])
    cols = np.flatnonzero(family == keys.index('random_uniform_for_rm'))
    assert len(cols) == 6
    size = np.asarray(gen.size, dtype=float)
    assert np.array_equal(size, [9.0, 9.0])
    ids = np.arange(80)
    tile_rows = ids // 2
    tile_cols = cols[ids % 2]
    centers = np.stack(((tile_rows + 0.5) * size[0] - 20 * size[0], (tile_cols + 0.5) * size[1] - 20 * size[1]), axis=-1)
    support = 0.4
    def whole_route_boundary(env):
        xy = env.scene['robot'].data.root_pos_w[:, :2] - env._g1_whole_route_centers
        return (xy[:, 0].abs() > 3.5) | (xy[:, 1].abs() > 3.0)
    cfg.terminations.rough_route_boundary.func = whole_route_boundary
    assert cfg.terminations.rough_route_boundary.time_out is True
    e = E1ResetEvidenceLearningEnv(cfg=cfg)
    r = e.scene['robot']
    guard=attach_fresh_guard(e,identity,torch,tensor)
    e._g1_whole_route_centers = torch.as_tensor(centers, device=e.device, dtype=e.scene.env_origins.dtype)
    ray = query(e)
    xy = np.repeat(centers[:,None,:],2,axis=1)
    xy[:,0,0]-=2.;xy[:,1,0]+=2.
    ceiling=float(ray.geometry.vertices[:,2].max())+2.
    preliminary=ray.cast(torch.as_tensor(np.concatenate((xy,np.full((80,2,1),ceiling)),axis=-1),device=e.device,dtype=torch.float32),10.)
    preliminary_height=cpu(preliminary['height'])
    assert preliminary['hit'].all() and (preliminary['normal'][...,2]>.99).all()
    orientation=np.where(preliminary_height[:,1]>preliminary_height[:,0],1.,-1.)
    assert np.sum(orientation==1)==40 and np.sum(orientation==-1)==40
    assert np.max(abs(np.ptp(preliminary_height,axis=1)-2.*np.tan(np.deg2rad(5.))))<=1e-6
    assert np.max(abs(np.min(preliminary_height,axis=1)))<=1e-6
    starts=centers.copy()
    starts[:,0]+=orientation*np.where(ids%3==1,1.+support,-1.-support)
    assert len(np.unique(np.stack((tile_rows,tile_cols),axis=-1),axis=0))==80
    e.scene.env_origins[:,:2]=torch.as_tensor(starts,device=e.device,dtype=e.scene.env_origins.dtype)
    e.reset()
    audit_before=fresh_full_dr_audit(e,guard,tensor)
    root_xy=r.data.root_pos_w.torch[:,:2]
    assert isinstance(root_xy,torch.Tensor) and root_xy.dtype==torch.float32
    assert torch.allclose(root_xy,torch.as_tensor(starts,device=e.device,dtype=root_xy.dtype),atol=1e-6,rtol=0)
    samples=np.linspace(-1.4,1.4,35)
    xy=np.repeat(centers[:,None,:],35,axis=1)
    xy[:,:,0]+=orientation[:,None]*samples
    sample=ray.cast(torch.as_tensor(np.concatenate((xy,np.full((80,35,1),ceiling)),axis=-1),device=e.device,dtype=root_xy.dtype),10.)
    assert sample['hit'].all() and (sample['normal'][...,2]>.99).all()
    sampled=cpu(sample['height']);expected=np.clip((samples+1.)/2.,0.,1.)*(2.*np.tan(np.deg2rad(5.)))
    assert np.max(abs(sampled-expected[None,:]))<=1e-6
    wheel_ids=[r.body_names.index(n) for n in ('left_wheel','right_wheel')]
    initial_wheel=cpu(r.data.body_link_pos_w)[:,wheel_ids,:]
    initial_u=(initial_wheel[:,:,0]-centers[:,None,0])*orientation[:,None]
    assert (initial_u[ids%3!=1]<-1.).all() and (initial_u[ids%3==1]>1.).all()
    route_scope=dict(tile_rows=tile_rows.tolist(),tile_cols=tile_cols.tolist(),family='derived_continuous5deg_ramp',tile_centers=centers.tolist(),requested_starts=starts.tolist(),size_m=size.tolist(),flat_support_margin_m=support,orientation=orientation.tolist(),ramp_start_canonical_x_m=-1.,ramp_end_canonical_x_m=1.,angle_deg=5.,ramp_length_m=2.,height_m=2.*np.tan(np.deg2rad(5.)),required_after_support_m=.200,actual_sampled_canonical_x_m=samples.tolist(),actual_sampled_ground=sampled.tolist(),actual_sampled_normals=js(sample['normal']),actual_authored_ground_query_passed=True,initial_wheel_link_positions=initial_wheel.tolist(),initial_two_wheels_on_requested_side=True,no_vertical_riser=True,not_actual_RM_geometry=True,not_stair_flight=True,termination_change='evaluation-only declared truncation abs x3.5m or abs y3m',production_boundary_unchanged=True,not_training_or_RM70mm=True)
    assert e.physics_dt == 0.0025 and e.step_dt == 0.02 and (r.data.joint_pos.shape == (80, 30))
    assert torch.equal(r.data.joint_pos, e._rough_probe_expected_q)
    initial = dict(root=js(r.data.root_state_w), q=js(r.data.joint_pos), parameters=e.chassis_pd_audit(), assignments=assignments(e), reset=e._rough_probe_reset_receipt)
    decl = declared_truncation_terms(e.termination_manager)
    names = tuple(e.termination_manager.active_terms)
    cmd = e.command_manager.get_term('twist')
    cmd.set_manual_evaluation_mode()
    groups = torch.arange(80, device=e.device) % 3
    targets = torch.tensor([0.3, -0.3, 0.0], device=e.device)[groups] * torch.as_tensor(orientation,device=e.device,dtype=torch.float32)
    return dict(env=e,robot=r,guard=guard,audit_before=audit_before,route_scope=route_scope,command=cmd,manual=True,groups=groups,targets=targets)


def build_original_route80(role,descriptor,case,identity,torch,np,wp,tensor):
 assert role in ('CURB_PROTECTED878','CURB_INDEPENDENT113','SLOPE135')
 return globals()['_factory_'+role.lower()](descriptor,case,identity,torch,np,wp,tensor)
