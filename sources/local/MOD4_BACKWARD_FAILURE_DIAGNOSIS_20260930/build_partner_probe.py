from pathlib import Path
import ast

root=Path(__file__).parent
s=(root/'diagnose_backward_trace.py').read_text(encoding='utf-8')
needle="    trace_buffers={}\n"
addition='''    # Read-only views: do not change collision filters, materials, joints or controls.
    import warp as wp
    from isaacsim.core.simulation_manager import SimulationManager
    from pxr import UsdPhysics
    partner_patterns=['/World/ground']+[f'/World/envs/env_{eid}/Robot/links/{name}' for eid in [40,14] for name in robot.body_names]
    sv=SimulationManager.get_physics_sim_view()
    partner_views=[sv.create_rigid_contact_view('/World/envs/env_14/Robot/links/'+name,
        filter_patterns=[],max_contact_data_count=4096) for name in ['left_wheel','right_wheel']]
    partner_frames=[]; net_frames=[]; all_root_frames=[]
    stage=env.scene.stage
    collision_audit=[]
    for prim in stage.Traverse():
        if prim.IsA(UsdPhysics.CollisionGroup):
            collision_audit.append({'path':str(prim.GetPath()),
                'relationships':{rel.GetName():[str(x) for x in rel.GetTargets()] for rel in prim.GetRelationships()},
                'attributes':{a.GetName():str(a.Get()) for a in prim.GetAttributes()}})
    scene_prim=stage.GetPrimAtPath(env.scene.physics_scene_path)
    partner_meta={'patterns':partner_patterns,'view_counts':[v.sensor_count for v in partner_views],
        'filter_counts':[v.filter_count for v in partner_views],
        'env_spacing':env.scene.cfg.env_spacing,'filter_collisions':env.scene.cfg.filter_collisions,
        'physics_backend':env.scene.physics_backend,'collision_groups':collision_audit,
        'all_initial_root_state':robot.data.root_state_w.detach().cpu().tolist(),
        'scene_collision_attributes':{a.GetName():str(a.Get()) for a in scene_prim.GetAttributes() if 'collision' in a.GetName().lower() or 'invert' in a.GetName().lower()},
        'raw_contact_capture_note':'Earlier filtered view yielded zero even on loaded ground: invalid negative evidence. This run uses unfiltered raw contacts and actor IDs.'}
    Path(args.trace_output+'.partners.json').write_text(json.dumps(partner_meta,indent=2))
    previous_update=env.scene.update
    partner_step=[0];raw_contact_rows=[]
    def update_and_read_partners(dt):
        previous_update(dt)
        partner_step[0]+=1
        now=partner_step[0]*env.physics_dt
        if 4.9<=now<=5.3:
            for wheel,v in enumerate(partner_views):
                force,point,normal,separation,count,start,ids=v.get_raw_contact_data(dt=env.physics_dt)
                nc=int(count.numpy()[0]);st=int(start.numpy()[0])
                if nc:
                    cpu_ids=wp.array(ids.numpy()[st:st+nc],dtype=wp.uint64,device='cpu')
                    paths=v.get_other_actor_paths_from_ids(cpu_ids)
                    fs=force.numpy()[st:st+nc].reshape(-1);pts=point.numpy()[st:st+nc];ns=normal.numpy()[st:st+nc];seps=separation.numpy()[st:st+nc].reshape(-1)
                    for z in range(nc):raw_contact_rows.append({'time_s':now,'wheel':wheel,'other_actor':paths[z],'force_N':float(fs[z]),'point':pts[z].tolist(),'normal':ns[z].tolist(),'separation_m':float(seps[z])})
        net_frames.append(torch.stack([wp.to_torch(v.get_net_contact_forces(dt=env.physics_dt)).reshape(-1,3).detach().clone() for v in partner_views]))
    env.scene.update=update_and_read_partners
    trace_buffers={}
'''
assert needle in s;s=s.replace(needle,addition,1)
s=s.replace("        arrays['env_ids']=trace_ids.cpu().numpy()", "        arrays['env_ids']=trace_ids.cpu().numpy()\n        arrays['partner_net_substep']=torch.stack(net_frames).cpu().numpy()\n        arrays['all_root_pos_control']=torch.stack(all_root_frames).cpu().numpy()\n        Path(args.trace_output+'.raw_contacts.json').write_text(json.dumps(raw_contact_rows,indent=2))",1)
s=s.replace("        record('action',action)","        all_root_frames.append(robot.data.root_pos_w.detach().clone())\n        record('action',action)",1)
ast.parse(s)
(root/'diagnose_contact_partners.py').write_text(s,encoding='utf-8')
print('Built isolated partner-force diagnostic; no production files edited.')
