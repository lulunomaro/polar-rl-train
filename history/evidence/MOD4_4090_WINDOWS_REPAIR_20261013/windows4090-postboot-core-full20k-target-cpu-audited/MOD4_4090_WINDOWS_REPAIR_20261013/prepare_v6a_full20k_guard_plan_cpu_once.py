from pathlib import Path
import hashlib,json,time
D=Path(__file__).resolve().parent;W=D.parent
def ref(p):
    b=p.read_bytes();return dict(path=str(p.resolve()),bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
def main():
    oldscript=W/'MOD4_E1_WAVE50_ROUTE_SECOND_BOUNDED_20261012/stage_resource_reviewed_target_and_dispatch_once.py'
    oldreceipt=W/'MOD4_E1_WAVE50_ROUTE_SECOND_BOUNDED_20261012/reports/RESOURCE_DURABLE_RAM_GPU_ADMISSION_ACTUAL.json'
    text=oldscript.read_text(encoding='utf8')
    assert 'ram_required=int(36639764*1024*1.25)+658725376+337280000+2*1024**3' in text
    assert 'gpu_required=(2*9940+2048)*1024**2' in text
    source=D/'repair_payload/v6a_audited_cpu_payload/reports/V6A_CLOSED_WRAPPERS_ACTUAL_SOURCE_MATH_CPU_PASSED.json'
    fixture=json.loads(source.read_bytes());assert fixture['passed'] and fixture['max_formal_updates']==256
    resource=W/'MOD4_E1_WAVE50_EPISODE_LIFETIME_REPAIR_20261012/reports/LIFETIME459_ACTUAL_OUTPUT_AND_NEXT_RESOURCE_REFERENCE.json'
    original=json.loads(resource.read_bytes())
    whole=669884181
    assert whole in original.values()
    checkpoint_bound=3*19058124
    trace=fixture['trace_retained_upper_bytes'];stack=fixture['trace_incremental_stack_upper_bytes']
    observer_and_snapshot_margin=512*1024**2
    # Deliberate overcount of the old entire pipeline plus all new saved files,
    # uncompressed incremental trace, simultaneous stacks and source witnesses.
    pipeline=whole+129*checkpoint_bound+trace+2*stack+observer_and_snapshot_margin
    durable=2*pipeline+2*1024**3
    original_peak=36639764*1024;peak_margin=int(original_peak*.25)
    added_CPU=trace+stack+checkpoint_bound+128*1024**2
    assert added_CPU<peak_margin
    ram=int(original_peak*1.25)+658725376+337280000+2*1024**3
    gpu=(2*9940+2048)*1024**2
    out=D/'reports/V6A_FULL20K_RESOURCE_GUARD_PLANNING_CPU_ACTUAL.json';assert not out.exists()
    result=dict(epoch=time.time(),planning_passed=True,values_are_guard_requirements_not_available_snapshots=True,requirements=dict(durable_free_bytes=durable,RAM_available_bytes=ram,GPU_free_bytes=gpu),original_strict_RAM_GPU_floors_not_lowered=True,new_Windows_capacity_numerical_equivalence_not_claimed=True,original_guard_source=ref(oldscript),original_actual_guard_receipt=ref(oldreceipt),actual_old_pipeline_source=ref(resource),new_closed_source_math=ref(source),formula=dict(max_formal_updates=256,max_checkpoint_files=129,checkpoint_file_conservative_bound=checkpoint_bound,retention_list_uncompressed_bytes=trace,max_incremental_NPZ_stack_bytes=stack,original_peak25percent_margin_bytes=peak_margin,enumerated_new_CPU_allocations_bound_bytes=added_CPU,new_probe_observer_does_not_overlap_formal_retention_phase=True,old_whole_pipeline_bytes=whole,uncompressed_pipeline_overcount_bound=pipeline,two_times_pipeline_plus_2GiB=durable),actual_live_resources_and_OSlock_before_GPU_still_required=True,no_GPU_or_new_budget_or_deletion=True)
    out.write_text(json.dumps(result,indent=2),encoding='utf8');print(json.dumps(dict(report=str(out),requirements=result['requirements'],planning_only=True)))
if __name__=='__main__':main()
