"""Ordinary supplement only for completed70; preserve all control errors and descriptive replay."""
from pathlib import Path
import ast,hashlib,json,time,traceback
N=Path(__file__).resolve().parent;T=N.parent;W=T.parent;G=W/'polar-rl-train';R=N/'reports'
def put(name,v):
 with (R/name).open('x',encoding='utf8') as f:json.dump(v,f,ensure_ascii=False,indent=2)
try:
 proof=json.loads((R/'PAIR_COMPLETE_MODELS_AND_ORIGINAL_COST_CPU_ACTUAL.json').read_bytes());assert proof['passed']
 put('LOCAL_CLOSED70_LOG_PATH_READER_ERRORS_RETAINED_ACTUAL.json',dict(epoch=time.time(),kind='local_reader_path_guesses_not_training_errors',original_errors=[dict(operation='rg',path='current_pair_closed_text/recovery/three_slot_finite_node_v1.log',error='System cannot find file; actual name node_CONSOLE.log was then listed and read'),dict(operation='rg',path='payloads/h1/job0/runtime/isaac/mod4_task.py',error='System cannot find file; rg --files located actual isaac/mod4/mod4_task.py')],no_mutation_or_lost_original_reports=True))
 put('CLOSED70_MODELS_CONTROL_EARLY_SAVE_REPLAY_WORK_ORDER_ACTUAL.json',dict(epoch=time.time(),models={k:dict(updates=v['updates'],Adam=v['Adam'],final=v['final'],original_cost=v['actual_cost']) for k,v in proof['models'].items()},actual_original_cost_sumonce=proof['actual_cost_sumonce'],remaining_closed_snapshot=proof['remaining_actual_snapshot'],allout_canonical_None_locks_free=proof['all_owner_nodes_children_actual_out'] and proof['original_canonical_cost_settled'] and proof['all_original_private_shared_locks_free'],E3='11 complete updates and source-control stop; not full nominal-duration learning. Original166 response-HMAC assertion errors and44 other transport errors preserved. Worker/node original_error false does not mean communication success.',network_diagnosis=str(R/'CONTROL_HTTP10_PARAMIKO_LIFETIME_REPRODUCTION_AND_FIX_CPU_ACTUAL.json'),latest_qualified_complete_sources='H1 131/795700 SHA8b7774eefc8fd6adf2785dc7a6d4356da9462ffa8a1402aeb1a3fbd6d2a5e769; E3 11/839240 SHA7f2244eff068de8e21d24e8feb19adbf77713c7bd0f4b4fac2e4c9aefe5b7238',saved70_motion='New adjacent129/130 producer snapshots,48 controls/.48s all20k,103 selected, derived3381884bytes SHA9f0453007c28779db024b83ce8bddb1a30c086dcb40cb09fce2314f71d3186d2; takeoffincrements293,landing/recovery/cross0. SameUSD kinematic PNG/GIF, no policy/GPU/physics.',not_whole_window_or_frozen_skill_evaluation=True,next71='New qualified70 continuation with exact network-channel ownership fix; actual installed target source/SDK/RSL passed and owner/nodes detached, firstGO/PPO not yet collected at this capture. No active70 or oldroot hotpatch; no secondwriter/account modification.',no_subagents_or_T2z_training=True))
 old=T/'MOD4_CLOSED68_ORIGINAL_HANDOFF_V69_COMBINED_RESTART_20261025/archive_closed69d_speed_replay_ordinary_once.py'
 source=old.read_text('utf8')
 start=source.index("D=Path(__file__).resolve().parent;");end=source.index("engine=T/",start)
 prefix="N=Path(__file__).resolve().parent;D=N;T=N.parent;W=T.parent;G=W/'polar-rl-train';R=N/'reports'\nF=T/'H1_STEP270_SAGITTAL_V6A_SAMPLING_OPT_NET_V5_RESOURCE_V71_20261025'\nU=T/'H1_STEP270_CLOSED70_SAVED_REPLAY_AFTER_V6A_20261025'\nS=G/'versions/20261025_mod4-step270-optimized70-qualified69-continuation'\ndest=S/'ordinary_closed70_control_failure_saved_replay'\n"
 source=source[:start]+prefix+source[end:]
 source=source.replace("'672d106d2988f1224a69af72b9d6ed0d9372e854'","'8af07b0839cd052925295534fa7caf55fbd0b611'")
 source=source.replace('1441','1442')
 start=source.index("mon=tomllib.loads(");end=source.index("assert json.loads((N/",start);source=source[:start]+source[end:]
 source=source.replace("S/'COMPLETE_FILE_CAPTURE_INDEX.json',S/'ordinary_source70_metadata_closed68_log_baseline/ORDINARY_CAPTURE_INDEX.json'","S/'COMPLETE_FILE_CAPTURE_INDEX.json'")
 source=source.replace('roots=[D,N/\'reports\',N/\'current_pair_closed_text\',N/\'current_pair_closed_models\',F,U]','roots=[N,U]')
 source=source.replace("for i in (98,99)","for i in (102,)")
 source=source.replace('CLOSED69D_STEP_TIMING_AND_REWARD_ALIGNMENT_DESCRIPTIVE_ACTUAL','CLOSED70_STEP_TIMING_AND_REWARD_ALIGNMENT_DESCRIPTIVE_ACTUAL')
 source=source.replace("'ordinary_combined69_completion_speed_saved_only_replay_and_source70_candidate'","'ordinary_closed70_complete_models_control_failure_speed_and_saved_replay'")
 start=source.index("add(dest/'ACTUAL_RESULT_NOTE.md'");end=source.index("git('add'",start)
 note='Closed70 H1 complete131/Adam795700, E3 complete11/839240. Both complete fullstate models passed CPU finite/17Adam x20/actor9 STD/critic8/clock checks; original writer fully settled4553.775024652481s and closedremaining730390.5752367973, all original children/locks/canonical closed. E3 was interrupted by source-control stop, not a full nominal learning window. Original166 HMAC assertion and44 other transport errors are retained. Deterministic actual HTTPClient/Paramiko send reproduction proves premature raw-channel close for split HTTP1.0 response bodies; borrowed channel view fixes this mechanism while unchanged signatures reject tamper/missing/truncated responses. No old active process or account was modified. New71 source fixes are separately reviewed and archived with their new real stage. New saved70 replay103selected/all20k48controls has takeoffincrements293,landing/recovery/cross0, not frozen/whole-window skill evaluation. Full timing report and original limited scopes retained. All binaries indexed using existing producer SHA only. Ordinary supplement to already-consumed70 trial, no new tag/record.\n'
 source=source[:start]+"add(dest/'ACTUAL_RESULT_NOTE.md',"+repr(note)+".encode('utf8'))\n"+source[end:]
 source=source.replace("'Record completed69 speed, original closure, saved replay and source70 follow-up'","'Record completed70 models, interrupted E3 control diagnostics and saved replay'")
 generated=N/'ARCHIVE70_ORDINARY_EXACT_SOURCE.py'
 with generated.open('x',encoding='utf8') as f:f.write(source)
 ast.parse(source);ns={'__name__':'ordinary70_capture','__file__':str(generated)};exec(compile(source,str(generated),'exec'),ns)
except BaseException:
 put('CLOSED70_ORDINARY_ARCHIVE_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(epoch=time.time(),error=traceback.format_exc(),resume_existing_commit_objects_only_no_repeat_record=True));raise
