"""CPU evidence/formula snapshot for the earlier full20k V6 plan, not a launch guard."""
from pathlib import Path
import ast,hashlib,json,re,time,types,tempfile,numpy as np
W=Path(r'C:/Users/lulu/Desktop/claude/mjcf')
D=Path(__file__).resolve().parent.parent;P=D/'repair_payload';R=D/'reports'
OLD=W/'MOD4_E1_WAVE50_ROUTE_SECOND_BOUNDED_20261012'
T=W/'MOD4_WAVE50_FACTOR_DIAGNOSIS_20261013/io_dr'
A=W/'MOD4_LOCAL_WAVE50_TEMP_TRAIN_20261013/runtime/isaac/mod4'
H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def ref(p):return dict(path=str(p),bytes=Path(p).stat().st_size,sha256=H(p))
def main():
 old=OLD/'reports/RESOURCE_DURABLE_RAM_GPU_ADMISSION_ACTUAL.json';oj=json.loads(old.read_bytes());guard=oj['resources']
 peak=OLD/'reports/FAILED_SECOND_GPU_MEMORY_ACTUAL_1791792057346641700.json';pj=json.loads(peak.read_bytes())
 hw=int(re.findall(r'VmHWM:\s+([0-9]+) kB',pj['child_status'])[0]);assert hw==36639764
 assert '9940' in pj['GPU'][1]['stdout'] and '3340979' in pj['GPU'][1]['stdout']
 ram=int(hw*1024*1.25)+658725376+337280000+2*1024**3
 gpu=(2*9940+2048)*1024**2
 assert ram==guard['RAM_required']==50042386944 and gpu==guard['GPU_required']==22993174528
 storage=OLD/'reports/SECOND1800_DURABLE_STORAGE_ADMISSION_ACTUAL.json';sj=json.loads(storage.read_bytes())['resources'];whole=sj['actual_completed1800_wholeoutput_bytes'];assert whole==1515186413
 live=T/'WINDOWS4090_ENV_METADATA_NATIVE_CPU_RESOURCE_ACTUAL_1791874558336943500.json';lj=json.loads(live.read_bytes())
 trace=A/'retention_learning_env.py';tree=ast.parse(trace.read_text(encoding='utf8'))
 cl=next(x for x in tree.body if isinstance(x,ast.ClassDef) and x.name=='RetentionLearningEnv')
 f=next(x for x in cl.body if isinstance(x,ast.FunctionDef) and x.name=='write_retention_trace')
 code=ast.unparse(f)
 assert 'self._retention_trace[self._retention_trace_written:end]' in code
 assert 'self._retention_trace_written = end' in code and '.clear(' not in code
 root=R/'RESOURCE256_CPU_INCREMENTAL_TRACE_FIXTURE';assert root.is_dir()
 files=sorted(root.glob('*.npz'));assert [p.name for p in files]==['retention_prefix_0_48.npz','retention_prefix_48_96.npz']
 rows=[np.load(p)['rows'] for p in files];assert all(x.dtype==np.float32 and x.shape==(48,2,16) for x in rows)
 expected=np.stack([np.full((2,16),i,dtype=np.float32) for i in range(96)])
 assert np.array_equal(np.concatenate(rows),expected)
 N=20000;U=256;controls=U*24;tracebytes=controls*N*16*4;stack48=48*N*16*4
 margin=hw*1024//4
 cp=P/'WINDOWS20K_ABI_PLUS_OFFSET_AWARE_V3_CPU_FIXTURE_V2_CONTRACT_REVIEW.pt';M=cp.stat().st_size
 assert M==19058124
 # 3 complete-file equivalents cover source/loaded/staging maps as a planning
 # allowance, not a measured Windows driver/process-memory peak.
 known_ram_increment=tracebytes+stack48+3*M
 assert known_ram_increment<margin
 V=P/'v6_audited_cpu_payload';wrapper=V/'windows4090_training_runtime_audited_v6.py';ws=wrapper.read_text(encoding='utf8')
 assert "max_formal_updates==256" in ws and "runner.cfg['save_interval']=int(source['iter'])+max_formal_updates+1" in ws
 v6=V/'windows4090_substep_readback_v6.py'
 # Save2 <=128 periodic +1 current-update/final save; no legacy modulo10
 # checkpoint files after the explicit V6 save-interval transformation.
 save_count=U//2+1
 source_delta=sum(p.stat().st_size for p in V.glob('*.py') if p.name.endswith('_v6.py') or p.name=='v6_closed_source_wrapper.py')
 # The frozen trace writer emits incremental NPZs. Raw payload is linear;
 # conservative deflate/container expansion reserved per bounded48control file.
 trace_container_allowance=save_count*65536
 deflate_extra=sum(((min(48,controls-s)*N*16*4)>>12)+((min(48,controls-s)*N*16*4)>>14)+13 for s in range(0,controls,48))
 trace_disk_planning=tracebytes+deflate_extra+trace_container_allowance
 B=31;witness=2*8*(29*B*8+184)
 perenv_outputs=64*(10+N+N)
 readback_planning=perenv_outputs+3*witness+3*524288+3*65536
 numeric_reference_only=2*whole+2*1024**3+2*source_delta+(save_count+2)*M+trace_disk_planning+readback_planning
 report=dict(epoch=time.time(),passed_CPU_planning_arithmetic_only=True,values_are_guard_requirements_not_available_snapshots=True,
  no_SSH_no_GPU_no_new_training_or_budget_transaction=True,
  scope='Earlier full20k V6 plan preserved as evidence; newer human20GB small-capacity task is a separate explicitly authorized scope.',
  original_Cfree_reader_error_retained=ref(R/'RESOURCE_CPU_PLANNER_ORIGINAL_CFREE_SCHEMA_ERROR.json'),source_references=[ref(old),ref(peak),ref(storage),ref(live),ref(trace),ref(cp),ref(wrapper),ref(v6)],
  fixed_full20k_guard_requirements=dict(RAM_available_bytes=ram,GPU_free_bytes=gpu),
  legacy_actual_peak=dict(child_pid=3340979,VmHWM_KiB=hw,observed_process_GPU_MiB=9940,not_continuous_peak_or_Windows_equivalence=True,
   retained_RAM_formula='int(VmHWM_KiB*1024*1.25)+658725376+337280000+2GiB',retained_GPU_formula='(2*9940+2048)MiB'),
  current_reference_snapshot=dict(available_RAM_bytes=lj['available_RAM_bytes'],Cfree_bytes=lj['freeC'],GPU_memory_units=lj['gpu_memory_units'],GPU_csv=lj['gpu_csv'],
   full20k_RAM_floor_shortfall_bytes=max(0,ram-lj['available_RAM_bytes']),snapshot_not_newlaunch_actual=True),
  formal_bound=dict(maximum_updates=U,maximum_controls=controls,maximum_periodic_plus_final_save_calls=save_count,save_every_updates=2,
   wall_window_seconds=3600,first_reached_then_fullsave_exit=True,not_guaranteed3600continuous_PPO=True,
   disabled_legacy_RSL_modulo10_save=True,wrapper_source=ref(wrapper)),
  incremental_trace=dict(actual_source_SHA=H(trace),actual_CPU_fixture_files=[ref(p) for p in files],actual_fixture_rows_dtype='float32',
   write_slice='[written:end]',advance_written_offset=True,retained_list_not_cleared=True,no_repeated_previous_prefix_npz=True,
   raw_payload_total_bytes=tracebytes,largest_save2_increment_stack_bytes=stack48,
   container_allowance_bytes=trace_container_allowance,deflate_planning_expansion_bytes=deflate_extra,disk_payload_planning_bytes=trace_disk_planning),
  RAM_margin_review=dict(original25percent_margin_bytes=margin,trace_plus_stack_plus3_complete_checkpoint_reference_bytes=known_ram_increment,
   enumerated_known_increment_fits_original_margin=True,remaining_margin_for_small_headers_and_objects_bytes=margin-known_ram_increment,
   V6_observer_only_SDK300_native144_fullrestore120_not_formal_trace_phase=True,
   Windows_defaultcapacity_and_allocator_peak_not_measured_or_declared_Linux_equivalent=True,
   preserved50GB_floor_not_actual_newnative_admission_or_guarantee=True),
  bounded_readback_planning=dict(maxima_13f32_3i32_bytes_per_env=64,probe_envcounts=[10,20000,20000],probe_controls=[300,144,120],
   fullbody_count_reference=B,witness_first_last_envs_per_stage=8,double_body_fields=29,first_last_witness_tensor_payload_bytes_per_stage=witness,
   perenv_allstage_raw_output_bytes=perenv_outputs,JSON_planning_allowance_per_stage=524288,
   total_planning_output_bytes=readback_planning,not_future_actual_serialized_size=True,
   double_COM_transient_matrix_only_bytes=29*N*B*8,not_only4MB_contact_buffer_claim=True,
   actual_GPU_backend_transient_peak_and_query_import_overhead_pending=True),
  durable=dict(actual_reference_complete1800_wholeoutput_bytes=whole,retained_base_formula='2*wholeoutput+2GiB',
   source_delta_local_V6_wrapper_bytes=source_delta,new_sourcecopy_delta_actual_target_pending=True,
   actual_checkpoint_CPU_fixture_reference_bytes=M,reference_file=ref(cp),
   formula='2*wholeoutput + 2GiB + 2*new_source_delta + (129+2)*M_fullcheckpoint_cap + incremental_trace_container_bound + bounded_readback_output_bound',
   numeric_using_known_checkpoint_reference_only_bytes=numeric_reference_only,
   M_fullcheckpoint_strict_serialized_cap_not_granted=True,
   actual_new_fullGPU_checkpoint_and_metadata_serialization_bound_pending=True,
   cannot_treat_reference_size_as_final_GPU_exact_size=True),
  actual_launch_admitted=False,all20k_stage_live_free_and_newnative_peak_review_pending=True,
  SDK10_own_smallscope_not_blocked_by_this_full20k_floor=True,
  no_guard_reduction_no_deletion_no_OS_change=True,
  earlier_while_loop_oral_description_corrected=dict(original_runtime_actual=ref(P/'windows4090_training_runtime.py'),actual='runner.learn(num_learning_iterations=100000), with per-update wall deadline; V6 adds hard256 stop'),
  Git_supplement_owner_root=True)
 out=R/'WINDOWS4090_FULL20K_SAVE2_MAX256_RESOURCE_CPU_PLANNING_ACTUAL.json';assert not out.exists();out.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
 print(json.dumps(dict(report=str(out),planning_passed=True,actuallaunch=False,RAM=ram,GPU=gpu,tracebytes=tracebytes,save_count=save_count,durable_reference_only=numeric_reference_only)))
if __name__=='__main__':main()
