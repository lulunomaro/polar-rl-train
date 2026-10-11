from direction_io import *

def main():
    owner=sorted(R.glob('DIRECTION_OWN_FORMAL_CPU_ACTUAL_[0-9]*.json'))[-1]
    own=json.loads(owner.read_bytes());assert own['passed'] and own['closeout_ready'] and own['actual_source_count']==423
    prior=W/'MOD4_E1_CURB20_ENTRY_FULLSTATE_PREPARE_20261011'
    common="from direction_io import *\nNEW=json.loads((R/'DIRECTION_STARTUP_ACTIVE_ROOT.json').read_bytes())['root']"
    source=(prior/'collect_entry139_actual.py').read_text(encoding='utf8')
    anchor='sys.path.insert(0,str(D));from stage_dispatch_seed_reviewed_once import NEW,save'
    assert source.count(anchor)==1
    collector=source.replace(anchor,common).replace('E1_CURB139_ASYNC_PUBLISHED.json','E1_CURB_DIRECTION_ASYNC_PUBLISHED.json').replace('e1_CURB20_entry_repair_observation_PASSED.json','e1_CURB20_direction_repair_observation_PASSED.json').replace('CURB139','CURB140')
    p=D/'collect_direction140_actual.py';assert not p.exists();p.write_text(collector,encoding='utf8')
    source=(prior/'review_entry139_schema_actual.py').read_text(encoding='utf8')
    anchor='sys.path.insert(0,str(D));from stage_dispatch_seed_reviewed_once import save';assert source.count(anchor)==1
    reviewer=source.replace(anchor,'from direction_io import *').replace('CURB139','CURB140')
    anchor="assert r['checkpoint']['finite_tensors']==b['checkpoint']['finite_tensors']==102"
    assert reviewer.count(anchor)==1
    reviewer=reviewer.replace(anchor,"assert r['checkpoint']['finite_tensors']==b['checkpoint']['finite_tensors']==ownCPU['actual_finite_tensor_count']")
    anchor="h=b['health'];assert";assert reviewer.count(anchor)==1
    reviewer=reviewer.replace(anchor,"ownCPU=read(sorted(R.glob('DIRECTION_OWN_FORMAL_CPU_ACTUAL_[0-9]*.json'))[-1]);assert ownCPU['passed'] and ownCPU['own_checkpoint']['sha256']==b['checkpoint']['sha256'] and ownCPU['actual_source_count']==423\n h=b['health'];assert")
    p=D/'review_direction140_actual.py';assert not p.exists();p.write_text(reviewer,encoding='utf8')
    compile(collector,str(D/'collect_direction140_actual.py'),'exec');compile(reviewer,str(p),'exec')
    segment=own['own_unique_completed_segment'][0]
    final=dict(epoch=time.time(),passed=True,own_final_CPU_report=str(owner),root=own['root'],checkpoint=own['own_checkpoint'],
        actual_source_count=423,actual_snapshot_file_count=own['actual_snapshot_file_count'],actual_finite_tensor_count=own['actual_finite_tensor_count'],
        formal_target_seconds=300,actual_load_learn_save_exit_seconds=segment['ended_epoch']-segment['started_epoch'],unique_original_parent_segment=segment,
        actual_updates=own['actual_updates'],control_steps=own['health']['control_steps'],environment_steps=own['actual_environment_steps'],callbacks=own['health']['actual_physics_callbacks'],health=own['health'],
        old_full_restore_and_new_direction_CPU_CUDA_diskroundtrip=own['startup_markers'],fresh_same_scope_direction_exact=own['fresh_same_scope_direction'],
        actual_all_exited=True,two_actual_OS_locks_free=True,active_segment_empty=True,supervisor_active_empty=True,published=own['published'],candidate140_complete_decision_pending=True,
        no_qualified_CURB_or_MoE_claim=True,no_more_PPO_until_complete_candidate140_review=True,original_failed421_small_cost_seconds=21.062857627868652,
        old_monitor_21_028_approximation_was_inaccurate_actual_unique_segment_priority=True,readers_only_no_GPU_queue_or_budget_write=True)
    save('DIRECTION_FORMAL_FINAL_ACTUAL_REVIEW.json',final)
    save('DIRECTION140_READERS_PREPARED.json',dict(epoch=time.time(),collector_SHA=H(collector.encode()),reviewer_SHA=H(reviewer.encode()),old132_ground_contact_fullraw_protocol_reused=True,old115_129_initial_parameters_recipes_assignments_signed_skill_exact_reused=True,
        candidate_tensor_count_bound_to_actual_own_CPU_not_source102=True,own_finite_tensors=own['actual_finite_tensor_count'],no_tolerance_or_result_changes=True,no_eval_replay=True))
    save('DIRECTION_LOCAL_OBSERVER_PATH_ERRORS_SUPPLEMENT.json',dict(epoch=time.time(),reader_only_no_runtime_changes=True,paths=[
        'MOD4_E1_CURB20_DIRECTION_REPAIR_20261011/payload/supervise_curb20_direction_startup_reviewed_once.py',
        'MOD4_E1_CURB20_DIRECTION_REPAIR_20261011/reports/DIRECTION_SOURCE_ACTUAL_BOUNDARY.json',
        'MOD4_E1_CURB20_ENTRY_FULLSTATE_PREPARE_20261011/dispatch_seed_reviewed_once.py',
        'MOD4_E1_CURB20_ENTRY_FULLSTATE_PREPARE_20261011/sync_entry139_complete_monitor_actual_once.py'],error='Local Get-Content/rg missing path, corrected through rg file inventory; no production mutation or GPU replay'))
    print(json.dumps(dict(prepared=True,own_final_passed=True,checkpoint_SHA=own['own_checkpoint']['sha256'],finite_tensors=own['actual_finite_tensor_count'],formal_seconds=final['actual_load_learn_save_exit_seconds'])))

if __name__=='__main__':main()
