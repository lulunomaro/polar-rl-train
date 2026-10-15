"""Independent completed first-window whole CPU verification; behavior and full raw audit remain separate."""
from pathlib import Path
import sys,os,json,time,hashlib,math,torch
os.environ['CUDA_VISIBLE_DEVICES']=''
D=Path(__file__).resolve().parent;W=D.parent
sys.path[:0]=[str(D),str(W/'MOD4_S3_WAVE50_CLOSEOUT_S4_LIVE_ADAPTER_20261015'),str(W/'MOD4_S3_SCOPE_COST_S4_READINESS_AUDIT_20261014')]
from s4_checkpoint_tree_CPU_v1 import walk,equal
from s4_original_fullstate_migration_v2 import SCHEMA
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
    r=json.loads(sorted((D/'reports').glob('S4_FIRST_GATE_CLOSED_FINAL_ALL_INPUTS_TWOHOST_ACTUAL_*.json'))[-1].read_bytes())
    rows={v['relative']:v for v in r['files']}
    row=next(v for v in r['files'] if v['path']==r['final']['own_checkpoint']);assert row['sha256']==r['final']['own_checkpoint_SHA']
    p=Path(row['local_path']);assert sha(p)==row['sha256']
    c=torch.load(p,map_location='cpu',weights_only=False)
    source=json.loads((D/'reports/CLOSED_S4_ZERO_FULLSTATE_INDEPENDENT_CPU_ADMITTED.json').read_bytes())
    old=torch.load(source['local_source'],map_location='cpu',weights_only=False)
    assert c['S4_first_formal_source_SHA']==source['source_SHA']=='0681d5c0e901aba5ceb96ec8504bc6beb4d30c87ee73dbc0fd652d3011ff02ce'
    assert c['S4_GPU_learning_admitted'] is True and c['S4_native_integration_checkpoint_not_production_learning_source'] is False
    changed=[k for k,v in c['actor_state_dict'].items() if not torch.equal(v,old['actor_state_dict'][k])]
    assert changed and all(k.startswith('gate.') for k in changed)
    frozen=[k for k in c['actor_state_dict'] if not k.startswith('gate.')]
    assert len(frozen)==19 and all(torch.equal(c['actor_state_dict'][k],old['actor_state_dict'][k]) for k in frozen)
    critic_changed=[k for k,v in c['critic_state_dict'].items() if not torch.equal(v,old['critic_state_dict'][k])]
    assert critic_changed
    state=c['optimizer_state_dict']['state'];assert len(state)==14 and len(c['optimizer_state_dict']['param_groups'][0]['params'])==14
    steps=[float(v['step']) for v in state.values()];assert len(set(steps))==1 and steps[0]>0 and steps[0]%20==0
    updates=int(steps[0]/20);assert updates==r['final']['updates']
    controls=c['S4_shared_control_state']['completed_controls'];assert controls==updates*24==r['final']['complete_controls']
    own=c['S4_owned_learning']['actor_owned'];assert own['rollout_samples']==controls*20000 and own['historical_forwards']==updates*20
    assert own['routing_device']=='cuda:0' and own['routing_seed']==20261015
    assert c['S4_owned_learning']['expert_optimizer_resumed'] is False
    assert not torch.equal(own['private_routing_rng'],old['S4_owned_learning']['actor_owned']['private_routing_rng'])
    selection=c['S4_supported_training_exposure']['last_selection']
    assert selection==r['gate_rollout_index']['rows'][-1]['selection']
    assert selection['physical_envs']==20000 and selection['physical_controls']==24
    assert selection['eligible_samples']==selection['complete_supported_envs']*24 and selection['domain_is_actor_input'] is False
    prefix=dict(rows=r['gate_rollout_index']['rows'][:updates],source_SHA=r['gate_rollout_index']['source_SHA']);assert c['S4_full_rollout_audit_index_SHA']==hashlib.sha256(json.dumps(prefix,indent=2).encode()).hexdigest()
    assert len(r['gate_rollout_index']['rows'])==updates and all(x['optimizer_update_complete'] for x in r['gate_rollout_index']['rows'])
    assert sum(x['physical_controls'] for x in r['gate_rollout_index']['rows'])==controls
    cache=c['S4_shared_control_state']['cache'];assert cache['policy'].shape==(20000,35) and cache['critic'].shape==(20000,38)
    assert torch.equal(cache['policy'][:,22:28],c['S4_shared_control_state']['previous'])
    assert cache['s4_training_supported_domain'].shape==(20000,1)
    assert ((cache['s4_training_supported_domain']==0)|(cache['s4_training_supported_domain']==1)).all()
    tensors=list(walk(c));floats=[v for k,v in tensors if v.is_floating_point()]
    assert all(v.device.type=='cpu' for k,v in tensors) and all(torch.isfinite(v).all() for v in floats)
    startup=Path(rows['learning_logs/S4_LEARNING_STARTUP_ADMITTED_ACTUAL.json']['local_path'])
    s=json.loads(startup.read_bytes());assert s['passed'] is True and s['pid']==260257 and s['source_SHA']==source['source_SHA']
    assert c['S4_learning_actual_startup_SHA']==sha(startup)
    for k in ('source_gate_critic_optimizer_private_CUDA_roundtrip_exact','private_CUDA_sample_z_raw_joint_logp_next_draw_disk_exact','source_episode_plus_one','domain_label_not_deployment_input_or_expert_choice'):assert s[k] is True
    for name,fields in SCHEMA.items():
        v=json.loads(Path(rows['learning_logs/'+name]['local_path']).read_bytes())
        assert v['pid']==260257 and v['source_sha256']==source['source_SHA']
        for k in fields:assert v[k] is True,(name,k)
    manifest=Path(rows['S4_FIRST_FORMAL_ACTUAL_MANIFEST.json']['local_path']);m=json.loads(manifest.read_bytes())
    assert m['parent_pid']==260242 and m['source_SHA']==source['source_SHA'] and m['max_learning_window_seconds']==2700
    assert sha(Path(rows['S4_FIRST_FORMAL_SOURCE_FREEZE.json']['local_path']))==s['sourcefreeze_SHA']
    health=json.loads(Path(rows['learning_logs/CLOCK_TRAINING_HEALTH.json']['local_path']).read_bytes());assert health['control_steps']==controls and health['actual_physics_callbacks']==r['final']['callbacks'];assert health['version']==3 and health['control_steps']>0 and health['pid']==s['pid']
    assert health['actual_physics_callbacks']==health['control_steps']*4 and health['nonfinite_observed'] is False
    assert health['integrity_task_reset_events']==health['unknown_task_reset_events']==0 and health['stop_reason'] is None
    # Saved histogram is an independent complete physical-control count.
    histogram_delta=int(c['E1_retained_flat_command_state']['control_histogram'].sum()-old['E1_retained_flat_command_state']['control_histogram'].sum())
    assert histogram_delta==controls*20000
    for v in r['files']:
        q=Path(v['local_path']);assert q.stat().st_size==v['bytes'] and sha(q)==v['sha256']
    assert r['all_collected_twohost_SHA_exact'] and r['actual_parent_guardian_child_absent']
    assert r['canonical_readonly_snapshot']['active'] is None and all(v['held'] is False for v in r['actual_two_fcntl_free'])
    segment=r['unique_completed_segment'];assert segment['source_SHA']==source['source_SHA'] and segment['ended_epoch']==segment['accounted_through_epoch']
    assert r['parent_exit']['passed'] is True and r['child_exit']['returncode']==0 and r['child_exit']['charged_once'] is True
    old_shapes={k:(v.shape,v.dtype) for k,v in walk(old)};new_shapes={k:(v.shape,v.dtype) for k,v in walk(c)}
    assert all(k in new_shapes and new_shapes[k]==shape for k,shape in old_shapes.items())
    result=dict(epoch=time.time(),passed=True,own_save=dict(path=row['path'],local_path=row['local_path'],bytes=row['bytes'],sha256=row['sha256']),
        source_SHA=source['source_SHA'],all_tensors=len(tensors),floating_tensors=len(floats),perenv_tensors=sum(v.ndim>0 and v.shape[0]==20000 for k,v in tensors),
        updates=updates,controls=controls,physical_vector_env_steps=controls*20000,expected_callbacks_for_saved_controls=controls*4,
        saved_histogram_control_count_exact=True,saved_gate_changed=len(changed),saved_critic_changed=len(critic_changed),
        original18_expert_weights_STD_and_duplicated_std_buffer_exact=True,new_optimizer_states=14,all_new_Adam_steps=steps[0],
        saved_adaptive_learning_rate=c['S4_owned_learning']['adaptive_learning_rate'],private_CUDA_sample_and_disk_restore_actual=True,
        actual_original8_plus_S4_startup_PID_source_and_sourceepisode_verified=True,complete_rollout_index_prefix_SHA_matches_own_final=True,
        selected_gradient_samples_last_update=selection['eligible_samples'],qualified_whole24_supported_envs_last_update=selection['complete_supported_envs'],
        physical_vector_steps_not_equal_all_supported_PPO_samples=True,current_live_health_separate_phase=health,
        twohost_whole_file_SHA_and_independent_local_CPU=True,actual_formal_final_and_original_unique_cost_closed=True,canonical_unique_seconds=segment['ended_epoch']-segment['started_epoch'],actual_parent_guardian_child_out_and_twofcntlFree_canonicalidle=True,full_raw_trace_and_frozen_behavior_still_required=True,
        first_real_S4_gate_PPO_saved_verified=True,not_S5_MoE_or50_70_allskill_qualification=True,local_CUDA_not_initialized=not torch.cuda.is_initialized())
    out=D/'reports/S4_FIRST_GATE_OWN_FINAL_WHOLE_LOCAL_CPU_VERIFIED.json';assert not out.exists();out.write_text(json.dumps(result,indent=2));print(json.dumps({k:result[k] for k in ('passed','updates','controls','physical_vector_env_steps','saved_gate_changed','saved_critic_changed','all_new_Adam_steps','all_tensors','floating_tensors','selected_gradient_samples_last_update')}))
if __name__=='__main__':main()
