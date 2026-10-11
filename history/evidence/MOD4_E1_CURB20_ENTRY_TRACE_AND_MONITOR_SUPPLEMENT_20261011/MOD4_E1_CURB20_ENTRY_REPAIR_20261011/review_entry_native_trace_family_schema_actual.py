from repair_io import *
import numpy as np

def main():
    c=json.loads(sorted(R.glob('ENTRY_NATIVE_COMPLETE_COLLECTION_*.json'))[-1].read_bytes())
    for row in c['indices']:assert H(Path(row['local_path']).read_bytes())==row['sha256']
    base=D/'native_complete_actual';v=json.loads((base/'ENTRY_NATIVE20K.json').read_bytes());h=v['health'];trace=base/'ENTRY_NATIVE20K_trace';a=json.loads((trace/'RETENTION_COMMAND_ACTUAL.json').read_bytes())
    x=np.concatenate([np.load(trace/p)['rows'] for p in a['trace_files']]);assert x.shape==(144,20000,16) and np.isfinite(x).all()
    root=np.array(v['reset_root_before_physics'],dtype=np.float32);q=np.array(v['reset_joint_pos_before_physics'],dtype=np.float32)
    assert root.shape==(20000,13) and q.shape==(20000,30)
    assert H(np.asarray(root[:,:2],dtype='<f4').tobytes())==v['CURB_entry_map']['map_sha256']
    hist=[];allids=[]
    for orientation in (1,-1):
        for side in (-1,1):
            ids=[]
            for cell in v['actual_generated_family_assignments']:
                if cell['family']!='random_uniform_for_rm' or (1 if cell['row']<20 else -1)!=orientation:continue
                b=np.asarray(cell['bounds']);center=(b[0,0]+b[1,0])*.5
                selected=np.flatnonzero(((root[:,:2]>=b[0,:2])&(root[:,:2]<b[1,:2])).all(1)&(np.sign(root[:,0]-center)==side));ids.extend(selected.tolist())
            ids=np.asarray(ids,dtype=np.int64);assert len(ids)>0;allids.extend(ids.tolist())
            z=x[:,ids];assert (z[:,:,10]==4).all() and (z[:,:,11]==0).all() and abs(z[:,:,8:10]).max()==0 and abs(z[:,:,7]).max()<=.300001
            positive=int((z[:,:,7]>1e-7).sum());negative=int((z[:,:,7]<-1e-7).sum());standing=int((abs(z[:,:,7])<=1e-7).sum());assert min(positive,negative,standing)>0
            hist.append(dict(actual_cell_orientation=orientation,world_entry_side=side,environments=len(ids),positive_BODY_vx_control_samples=positive,negative_BODY_vx_control_samples=negative,standing_control_samples=standing))
    assert len(allids)==len(set(allids))==2820
    assert h['control_steps']==144 and h['actual_physics_callbacks']==h['expected_physics_callbacks']==576
    assert v['physical_callback_count']==v['expected_callback_count']==480 and v['PPO_update_count']==0 and v['checkpoint_sha256']==SHA
    assert h['ordinary_episode_reset_events']==h['integrity_task_reset_events']==h['unknown_task_reset_events']==0
    assert int(x[:,:,14].sum())==0 and int(x[:,:,15].sum())==h['actual_truncation_reset_events']==1
    assert h['termination_reason_coverage_exact'] and h['truncation_reason_coverage_exact'] and not h['nonfinite_observed'] and h['stop_reason'] is None
    assert v['E1_actual_ground_error_m']<=1e-6 and v['E1_height_reward_formula_error']<=1e-6 and v['actual_solver_readback']['all_position32_velocity4']
    assert v['E1_reset_receipt']['sample_points']==25200 and v['E1_reset_receipt']['sampled_min_clearance_m']>=.002-1e-5 and v['command_retention']['projection_error']<=1e-6
    sdk=json.loads((base/'ENTRY_SDK10.json').read_bytes());sr=np.array(sdk['reset_root_before_physics']);covered=[]
    for cell in sdk['SDK_CURB_actual_assignment_placement']['chosen_actual_assignments']:
        b=np.asarray(cell['bounds']);covered.extend(np.flatnonzero(((sr[:,:2]>=b[0,:2])&(sr[:,:2]<b[1,:2])).all(1)).tolist())
    assert not covered and sdk['CURB_entry_map']['changed_environments']==0
    out=save('ENTRY_NATIVE_COMPLETE_FAMILY_SCHEMA_ACTUAL_REVIEW.json',dict(epoch=time.time(),review_complete=True,native20k_scope_passed=True,SDK10_prior_exit_PASSED_preserved=True,SDK10_CURB_entry_scope_admission=False,SDK10_actual_CURB_start_environments=0,SDK10_declared_chosen_CURB_cells=10,diagnosis='SDK diagnostic changed env_origins after initial reset; cached _curb_entry_xy remained original pre-change points. Actual root before physics is outside all chosen CURB cells. Native20k no origin change and actual 2820 map/root/fulltrace exact.',old_readonly_reviewer_error=dict(type='IndexError',message='arrays used as indices must be of integer (or boolean) type',source=str(D/'review_entry_native_trace_actual.py'),before_GPU_or_mutation=True),missing_optional_prior_CPU_reader_path='environment_view_payload/isaac/mod4/validate_curb20_environment_view_cpu.py; no execution; actual source used instead',trace_family_schema_zero_based_CURB4_histogram_row5=True,second_reader_schema_error_preserved="V2 reader assumed histogram row5 equals trace family5; actual FAMILIES.index is4; AssertionError before any GPU/mutation",native_actual_signed_standing_histograms=hist,native_entry_map=v['CURB_entry_map'],native_callbacks=576,timed_callbacks=480,ordinary_events=0,unique_truncation_events=1,reason_counts=h['termination_events_by_reason'],two_coverage_exact=True,ground_error=v['E1_actual_ground_error_m'],reward_formula_error=v['E1_height_reward_formula_error'],closure_m=h['max_closure_error_m'],mimic_rad=h['max_mimic_error_rad'],all_actual_JSON_NPZ_byteSHA_verified=True,short_prefix_not_full_route_or_circle=True,fullstate_learning_requires_new_origin_bound_SDK10_only_no_native20k_replay=True))
    print(json.dumps(dict(report=str(out),native20k_passed=True,SDK10_scope_missing=True,new_SDK_repair_required=True,histograms=hist)))

if __name__=='__main__':main()
