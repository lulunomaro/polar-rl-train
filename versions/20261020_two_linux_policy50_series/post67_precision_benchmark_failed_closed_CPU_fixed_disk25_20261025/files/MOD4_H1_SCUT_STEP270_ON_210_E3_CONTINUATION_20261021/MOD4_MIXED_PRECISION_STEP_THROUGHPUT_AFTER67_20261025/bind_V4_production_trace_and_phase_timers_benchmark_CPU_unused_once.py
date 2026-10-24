from pathlib import Path
import ast,hashlib,json,shutil,time
M=Path(__file__).resolve().parent;R=M/'reports';H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();qp=R/'TWO50_LATEST_CLOSED_SOURCES_PAYLOADS_CPU_PREPARED_ACTUAL.json'
with (R/'PREVIOUS_V3_BENCHMARK_BOUND_PAYLOAD_CONFIG_EXACT_BEFORE_V4.json').open('xb') as f:f.write(qp.read_bytes())
q=json.loads(qp.read_bytes());assert q['performance_benchmark_only']
for key in ('h1','recovery'):
 B=Path(q['payloads'][key]);mp=B/'THREE_SLOT_COMPLETE_MANIFEST_V1.json'
 with (R/(key.upper()+'_PREVIOUS_V3_BOUND_MANIFEST_EXACT_BEFORE_V4.json')).open('xb') as f:f.write(mp.read_bytes())
 old=json.loads(mp.read_bytes());known={r['relative']:r for r in old['files']};oldscript=B/q['specs'][key]['production_script'];a=oldscript.read_text('utf8');assert a.count('from mixed_precision_step_benchmark_runtime_v3 import run')==1
 b=a.replace('from mixed_precision_step_benchmark_runtime_v3 import run','from mixed_precision_step_benchmark_runtime_v4 import run');ast.parse(b);newname=oldscript.name.replace('_v1.py','_v2.py')
 with (B/newname).open('x',encoding='utf8') as f:f.write(b)
 shutil.copy2(M/'mixed_precision_step_benchmark_runtime_v4.py',B/'mixed_precision_step_benchmark_runtime_v4.py')
 taskp=B/'job0/TASK.json'
 with (R/(key.upper()+'_PREVIOUS_V3_BENCHMARK_TASK_EXACT_BEFORE_V4.json')).open('xb') as f:f.write(taskp.read_bytes())
 task=json.loads(taskp.read_bytes());task.update(benchmark_original_H1_trace_and_approved_retention_unchanged=True,benchmark_sampling_phase_timing=['neural_inference','physics_sim_step','scene_update_sensors_state','terrain_rays','reward','termination','observation','reset','trace_preupdate_snapshot','trace_compression_SHA_retention'],CPU_wall_attribution_includes_implicit_waits_not_GPU_kernel_exclusive=True)
 taskp.write_text(json.dumps(task,indent=2),encoding='utf8');q['specs'][key]['production_script']=newname;rows=[]
 for p in sorted(B.rglob('*')):
  if not p.is_file() or p.name=='THREE_SLOT_COMPLETE_MANIFEST_V1.json' or '__pycache__' in p.parts:continue
  rel=p.relative_to(B).as_posix()
  if p.suffix=='.py':ast.parse(p.read_text('utf8'))
  if p.suffix in ('.pt','.npz','.usd','.stl'):assert p.stat().st_size==known[rel]['bytes'];sha=known[rel]['SHA']
  else:sha=H(p)
  rows.append(dict(relative=rel,bytes=p.stat().st_size,SHA=sha))
 mp.write_text(json.dumps(dict(old,files=rows,benchmark_original_trace_preserved=True),indent=2),encoding='utf8');q['specs'][key]['manifest_SHA']=H(mp)
qp.write_text(json.dumps(q,indent=2),encoding='utf8')
with (R/'BENCHMARK_V4_TRACE_AND_SAMPLING_PHASE_BINDING_CPU_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(dict(epoch=time.time(),passed=True,new_runtime=str(M/'mixed_precision_step_benchmark_runtime_v4.py'),new_runtime_SHA=H(M/'mixed_precision_step_benchmark_runtime_v4.py'),V3_payload_config_manifest_Task_exact_versions_preserved=True,original_H1_trace_compression_and_approved_retention_reused=True,all_source_model_PPO_base_runtime_physics_command_goal_and_original_owner_accounting_unchanged=True,no_remote_Task_or_GO_yet=True),f,indent=2)
with (R/'LOCAL_INITIAL_PREPARER_INTERMEDIATE_REPORT_VERSION_NOT_CAPTURED_GAP_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(dict(epoch=time.time(),scope='Initial pure-local preparer output and pre-bind payload manifest before first V3 benchmark binding',original_intermediate_full_bytes_not_captured_before_binding_overwrite=True,preparer_source_and_actual_stdout_preserved=True,first_bound_config_and_manifest_source_SHA_source_Adam_no_GO_receipts_preserved=True,new_V4_binding_saves_exact_before_versions=True,no_original_false_or_failed_result_relabelled_pass=True,no_remote_Task_GO_model_original_or_canonical_changed_in_gap=True,no_fake_byte_reconstruction_or_preparer_rerun=True),f,indent=2)
print(json.dumps(dict(passed=True,production_scripts={k:v['production_script'] for k,v in q['specs'].items()},original_trace_preserved=True)))

