"""Optional83B motion diagnosis after full closure, never rerun a historical extractor."""
from pathlib import Path
import ast,hashlib,json,time
N=Path(__file__).resolve().parent;T=N.parent;R=N/'reports';P=T/'H1_STEP270_CLOSED77_SAVED_REPLAY_AFTER_V8_20261026';U=T/'H1_STEP270_CLOSED83B_SAVED_REPLAY_AFTER_V8_20261026';assert not U.exists();U.mkdir();(U/'reports').mkdir()
names={
'extract_closed77_last_two_saved_prefixes_CPU_unused_once.py':'extract_closed83B_last_two_saved_prefixes_CPU_unused_once.py',
'reconstruct_closed77_saved_motion_USD_CPU_unused_once.py':'reconstruct_closed83B_saved_motion_USD_CPU_unused_once.py',
'analyze_render_closed77_saved_step_timing_CPU_unused_once.py':'analyze_render_closed83B_saved_step_timing_CPU_unused_once.py'}
sources=[]
for old,new in names.items():
 text=(P/old).read_text('utf8');sourceSHA=hashlib.sha256((P/old).read_bytes()).hexdigest()
 for before,after in [('V77_20261026','V83B_20261026'),('2610v77/','2610v83b/'),('CLOSED77','CLOSED83B'),('Closed77','Closed83B'),('closed77','closed83B'),('complete77','complete83B'),('Unused77','Unused83B'),('New77','New83B')]:text=text.replace(before,after)
 ast.parse(text);assert 'V77_20261026' not in text and '2610v77/' not in text
 with (U/new).open('x',encoding='utf8') as f:f.write(text)
 sources.append(dict(source=str(P/old),source_SHA=sourceSHA,prepared_path=str(U/new),prepared_SHA=hashlib.sha256((U/new).read_bytes()).hexdigest()))
B=T/'H1_STEP270_REWARD_PATH_V1_20261022';text=(B/'same_authorized_session_compressed_transport_v139.py').read_text('utf8');needle='    assert target.name in {';assert text.count(needle)==1;text=text.replace(needle,needle+'\n        '+repr(names['extract_closed77_last_two_saved_prefixes_CPU_unused_once.py'])+',',1)
with (B/'same_authorized_session_compressed_transport_v140.py').open('x',encoding='utf8') as f:f.write(text)
with (R/'SOURCE_ONLY83B_NEW_RETAINED_MOTION_PROTOCOL_PREPARED_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(dict(epoch=time.time(),source_only=True,no_actual83B_closed_model_or_prefix_read_yet=True,requires_actual83B_three_FINAL_CPU_original_cost_allout=True,new_retained_last_two_adjacent_actualproducer_prefixes_only=True,sourcehelper67_AST_reference_not_reexecuted_as67=True,sources=sources,existing_native_geometry_reused_no_native_query_or_GPU=True,kinematic_closure_visual_diagnostic_not_training_gate=True,not_proof_of_fullwindow_or_frozen_success=True,local_native_save_search_glob_exclusion_failed_and_overbroad_output_truncated=True,subsequent_reads_used_exact_candidate_v5_and_worker_paths=True,no_native_finalization_cause_proven_or_runtime_change=True),f,indent=2)
print(json.dumps(dict(new83B_motion_source_only=True,helpers=len(names),no_binary_host_or_training_read=True)))
