from pathlib import Path
import ast,hashlib,importlib.metadata,importlib.util,json,sys,time,psutil
B=Path(__file__).resolve().parent;J=B/'job0';sys.path[:0]=[str(B),str(B/'source')]
def H(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 from native_flat90_source_guard_v1 import check_payload
 from native88C_to_flat_migration_v1 import KIND,FLAT_OBJECTIVE_CONTRACT
 p=psutil.Process()
 with (J/'FLAT90_SOURCE_CPU_STARTED_ACTUAL.json').open('x') as f:json.dump(dict(pid=p.pid,creation=p.create_time(),argv=p.cmdline(),exe=p.exe(),cwd=p.cwd(),before_model_load=True,models_not_loaded_this_metadata_only_purpose=True),f,indent=2)
 checked=check_payload(B,verify_model_bytes=False);task=checked['task'];binding=json.loads((B/'source/PRODUCER_FRAME_SHA_FIX_BINDING_ACTUAL.json').read_bytes())
 raw=(B/'source/ORIGINAL106_FULLSTATE_CPU_REPORT_ACTUAL.json').read_bytes();original=json.loads(raw);pr=(B/'source/ORIGINAL106_CPU_WAITED_PROOF_ACTUAL.json').read_bytes();proof=json.loads(pr)
 assert hashlib.sha256(raw).hexdigest()==binding['original_CPU_SHA'] and hashlib.sha256(pr).hexdigest()==binding['original_waited_SHA'] and proof['actual_waited'] and proof['returncode']==0 and proof['report_SHA']==binding['original_CPU_SHA']
 assert original['passed'] and original['source_SHA']==task['source_SHA'] and original['source_progress']==task['source_progress'] and original['fudan_step_task']==task['fudan_step_task'] and original['episode_clock']==task['episode_clock'] and original['physical_initial_seed']==task['native_seed'] and original['kind']==KIND
 entry=B/'source/native_flat5cm_training_entry_candidate_v4_typed_producer.py';new=entry.read_bytes();assert H(entry)==binding['new_entry_SHA'] and hashlib.sha256(new.replace(binding['correct_literal'].encode(),binding['original_literal'].encode())).hexdigest()==binding['original_entry_SHA']
 values={x.arg:x.value.value for x in ast.walk(ast.parse(new)) if isinstance(x,ast.keyword) and x.arg in ('private_phase_frame_source_SHA','real_callback_counter_source_SHA','source_reference_artifact_SHA') and isinstance(x.value,ast.Constant)}
 assert values['private_phase_frame_source_SHA']==FLAT_OBJECTIVE_CONTRACT['private_phase_frame_source_SHA']==H(B/'source/private_phase_frame_v1.py')
 assert values['real_callback_counter_source_SHA']==FLAT_OBJECTIVE_CONTRACT['real_callback_counter_source_SHA']==H(B/'h1_step270_sdk_runtime_candidate.py')
 from native88C_to_flat_migration_v1 import SOURCE_REFERENCE_SHA
 assert values['source_reference_artifact_SHA']==SOURCE_REFERENCE_SHA
 sdk=Path(next(iter(importlib.util.find_spec('isaaclab').submodule_search_locations)));rsl=Path(next(iter(importlib.util.find_spec('rsl_rl').submodule_search_locations)));source=json.loads((B/'NATIVE88_SOURCE_CONTRACT_ACTUAL.json').read_bytes());versions={n:importlib.metadata.version(n) for n in ('isaaclab','rsl-rl-lib','torch')};assert versions==source['expected_installed_versions'] and H(sdk/'utils/math.py')==source['expected_actual_SDK_math_SHA']
 for row in source['expected_actual_RSL_sources']:assert H(rsl/row['relative'])==row['SHA']
 for rel,SHA in binding['unchanged_original_Python_sources'].items():assert H(B/rel)==SHA
 value=dict(original,payload_manifest_SHA=checked['manifest_SHA'],source_contract_SHA=H(B/'FLAT90_SOURCE_CONTRACT_ACTUAL.json'),worker_SHA=H(B/'h1_native_flat90_worker_v1.py'),initial_loads=dict(selected104source=0,normal86=0),original106_initial_loads=original['initial_loads'],original106_fullstate_CPU_SHA=binding['original_CPU_SHA'],original106_waited_proof_SHA=binding['original_waited_SHA'],source107_metadata_only_producer_frame_SHA_fix_passed=True,source107_no_saved_weights_norms_opts_redecoded=True,source107_actual_SDK_sources_rechecked=True,producer_three_source_literals_bound=True)
 with (J/'FLAT90_SOURCE_SDK_CPU_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(value,f,indent=2,allow_nan=False)
 print(json.dumps(dict(passed=True,kind=KIND,metadata_only_extension_no_model_read=True)))
if __name__=='__main__':main()
