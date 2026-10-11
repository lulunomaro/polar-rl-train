from repair_io import *
import numpy as np

def main():
    collection=json.loads(sorted(R.glob('ENTRY_NATIVE_COMPLETE_COLLECTION_*.json'))[-1].read_bytes())
    for row in collection['indices']:
        p=Path(row['local_path']);assert p.stat().st_size==row['bytes'] and H(p.read_bytes())==row['sha256']
    roots=D/'native_complete_actual';reviews={}
    for label,n,c,warm in (('ENTRY_SDK10',10,300,0),('ENTRY_NATIVE20K',20000,120,24)):
        v=json.loads((roots/(label+'.json')).read_bytes());h=v['health'];trace=roots/(label+'_trace')
        a=json.loads((trace/'RETENTION_COMMAND_ACTUAL.json').read_bytes())
        parts=[np.load(trace/name)['rows'] for name in a['trace_files']];x=np.concatenate(parts)
        assert x.shape==(c+warm,n,16) and np.isfinite(x).all()
        assert a['actual_controls']==h['control_steps']==len(x)
        assert h['actual_physics_callbacks']==h['expected_physics_callbacks']==len(x)*4
        assert v['physical_callback_count']==v['expected_callback_count']==c*4
        assert v['PPO_update_count']==0 and v['frozen_policy_only'] and not v['nonfinite']
        assert h['ordinary_episode_reset_events']==h['integrity_task_reset_events']==h['unknown_task_reset_events']==0
        assert h['termination_reason_coverage_exact'] and h['truncation_reason_coverage_exact'] and not h['nonfinite_observed'] and h['stop_reason'] is None
        assert v['E1_actual_ground_error_m']<=1e-6 and v['E1_height_reward_formula_error']<=1e-6 and v['actual_solver_readback']['all_position32_velocity4']
        assert v['checkpoint_sha256']==SHA
        assert v['E1_reset_receipt']['sample_points']==25200 and v['E1_reset_receipt']['sampled_min_clearance_m']>=.002-1e-5
        root=np.asarray(v['reset_root_before_physics'],dtype=np.float32);q=np.asarray(v['reset_joint_pos_before_physics'],dtype=np.float32)
        assert root.shape==(n,13) and q.shape==(n,30) and np.isfinite(root).all() and np.isfinite(q).all()
        # Entry receipt is the actual deterministic map written by the physical reset.
        assert H(np.asarray(root[:,:2],dtype='<f4').tobytes())==v['CURB_entry_map']['map_sha256']
        assignments=v['actual_generated_family_assignments'];ids=[];meta={}
        for cell in assignments:
            if cell['family']!='random_uniform_for_rm':continue
            b=np.asarray(cell['bounds']);selected=np.flatnonzero(((root[:,:2]>=b[0,:2])&(root[:,:2]<b[1,:2])).all(1))
            for idx in selected:
                assert int(idx) not in meta
                meta[int(idx)]=dict(row=cell['row'],column=cell['column'],orientation=1 if cell['row']<20 else -1,side=int(np.sign(root[idx,0]-(b[0,0]+b[1,0])*.5)))
                ids.append(int(idx))
        ids=np.array(sorted(ids));assert len(ids)==v['CURB_entry_map']['changed_environments']
        assert (x[:,ids,10]==5).all() and (x[:,ids,11]==0).all()
        assert np.abs(x[:,ids,8:10]).max()==0 and np.abs(x[:,ids,7]).max()<=.300001
        groups=[]
        for orientation in (1,-1):
            for side in (-1,1):
                chosen=[idx for idx in ids if meta[int(idx)]['orientation']==orientation and meta[int(idx)]['side']==side]
                z=x[:,chosen,7];forward=int((z>1e-7).sum());reverse=int((z< -1e-7).sum());standing=int((np.abs(z)<=1e-7).sum())
                groups.append(dict(actual_cell_orientation=orientation,world_entry_side=side,environments=len(chosen),positive_BODY_vx_control_samples=forward,negative_BODY_vx_control_samples=reverse,standing_control_samples=standing,initial_heading_before_min=float(x[0,chosen,6].min()) if chosen else None,initial_heading_before_max=float(x[0,chosen,6].max()) if chosen else None))
                if n==20000:assert forward>0 and reverse>0 and standing>0
        if n==20000:assert len(ids)==2820 and v['command_retention']['projection_error']<=1e-6
        if n==10:assert v['sensor_sdk_audit']['selected_reset']['other_bias_episode_exact']
        assert int(x[:,:,14].sum())==h['ordinary_episode_reset_events']+h['integrity_task_reset_events']+h['unknown_task_reset_events']
        assert int(x[:,:,15].sum())==h['actual_truncation_reset_events']
        delta=x[:,:,3:6]-x[:,:,:3]
        reviews[label]=dict(full_trace_shape=list(x.shape),full_trace_byteSHA_verified=True,source_sha256=v['checkpoint_sha256'],actual_ground_height_error=v['E1_actual_ground_error_m'],reward_formula_error=v['E1_height_reward_formula_error'],actual_physics_callbacks=h['actual_physics_callbacks'],timed_callbacks=v['physical_callback_count'],ordinary_events=h['ordinary_episode_reset_events'],integrity_events=h['integrity_task_reset_events'],unknown_events=h['unknown_task_reset_events'],unique_truncation_events=h['actual_truncation_reset_events'],reason_counts=h['termination_events_by_reason'],two_coverage_exact=True,closure_m=h['max_closure_error_m'],mimic_rad=h['max_mimic_error_rad'],actual_CURB_environments=len(ids),actual_signed_standing_mirror_histograms=groups,actual_entry_map=v['CURB_entry_map'],actual_cell_and_root30q_bound=True,per_step_pre_reset_delta_maxnorm_m=float(np.linalg.norm(delta,axis=2).max()),reset_teleport_excluded_by_before_and_prereset_roots=True,short_prefix_not_a_full_route_or_circle=True,contact_force_and_full_route_graduation_not_claimed=True)
    out=save('ENTRY_NATIVE_COMPLETE_TRACE_ACTUAL_REVIEW.json',dict(epoch=time.time(),review_complete=True,passed=True,new_actual_reset_scope_admitted_for_fullstate_preparation_only=True,SDK_native_exactSHA_reuse_no_replay=True,collection=str(sorted(R.glob('ENTRY_NATIVE_COMPLETE_COLLECTION_*.json'))[-1]),results=reviews,new_budget_seconds=0,PPO_or_fullstate_formal_not_yet_admitted=True))
    print(json.dumps(dict(report=str(out),review_complete=True,SDK_callbacks=1200,native_callbacks=576,CURB_environment_count=2820,fullstate_pending=True)))

if __name__=='__main__':main()
