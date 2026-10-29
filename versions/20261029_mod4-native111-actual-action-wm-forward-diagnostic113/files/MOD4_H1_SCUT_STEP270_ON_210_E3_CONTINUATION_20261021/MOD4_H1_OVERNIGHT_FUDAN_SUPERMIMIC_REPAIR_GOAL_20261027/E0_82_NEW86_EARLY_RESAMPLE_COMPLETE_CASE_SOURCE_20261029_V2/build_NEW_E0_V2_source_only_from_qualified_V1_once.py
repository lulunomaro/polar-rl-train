"""LOCAL source derivation only; zero PT/raw/NPZ/USD/SDK/host reads."""
from pathlib import Path
import ast,hashlib,json
B=Path(__file__).resolve().parent;L=B.parent
OLD=L/'E0_82_NEW86_N20K_LONG_COMMAND_FROZEN_SOURCE_20261029_V1'
EARLY=L/'E0_EARLY_ORIGINAL_RESAMPLE_LIFECYCLE_SOURCE_20261029_V1'
OLDJOB='/data/robemo/polar-rl-train/evaluation_runs/E0_ADAPTED82_LONG_COMMAND_20261029v1/e0'
JOB='/data/robemo/polar-rl-train/evaluation_runs/E0_ADAPTED82_EARLY_RESAMPLE_20261029v2/e0'
NAMES={
'evaluate_E0_adapted82_new86_frozen1000_once_v1.py':'evaluate_E0_adapted82_new86_frozen1000_once_v2_early.py',
'detached_E0_new86_frozen_profile_supervisor_once_v1.py':'detached_E0_new86_frozen_profile_supervisor_once_v2_early.py',
'E0_new86_target_source_SDK_metadata_admission_v1.py':'E0_new86_target_source_SDK_metadata_admission_v2_early.py',
'remote_E0_new86_long_command_install_and_detach_v1.py':'remote_E0_new86_early_command_install_and_detach_v2.py',
'upload_admit_detach_NEW86_E0_final82_long_command_secure_stdin_UNUSED_once_v1.py':'upload_admit_detach_NEW86_E0_final82_early_command_secure_stdin_UNUSED_once_v2.py',
'E0_frozen_actual_receipts_readonly_CODE_v1.py':'E0_frozen_actual_receipts_readonly_CODE_v2_early.py',
'run_E0_new86_readonly_secure_stdin_v1.py':'run_E0_new86_readonly_secure_stdin_v2_early.py',
'read_E0_new86_FIRST_native24_queue_secure_stdin_UNUSED_once_v1.py':'read_E0_new86_FIRST_native24_early_queue_secure_stdin_UNUSED_once_v2.py',
'collect_E0_new86_TERMINAL_fulltext_secure_stdin_UNUSED_once_v1.py':'collect_E0_new86_TERMINAL_fulltext_secure_stdin_UNUSED_once_v2.py',
'FROZEN_E0_82_NEW86_LONG_COMMAND_SOURCE_INDEX_V1.json':'FROZEN_E0_82_NEW86_EARLY_RESAMPLE_COMPLETE_SOURCE_INDEX_V2.json',
'E0_NEW86_COMPLETE_INPUT_MANIFEST_V1.json':'E0_NEW86_COMPLETE_INPUT_MANIFEST_V2.json'}
def H(raw):return hashlib.sha256(raw).hexdigest()
def write(n,s):
 with (B/n).open('xb') as f:f.write(s.encode() if isinstance(s,str) else s)
def sub(s,a,b):assert a in s,a;return s.replace(a,b)
shared=('project_clone_launch_helpers_v1.py','lossless_snapshot_pinned75d683.py','original_flat_height_provider_v1.py','GROUND_PROVIDER_SOURCE_CONTRACT.json','e0_profile_unused')
for n in shared[:-1]:write(n,(OLD/n).read_bytes())
for n in ('e0_original_profile_catalog_v1.py','e0_observed_command_instances_v1.py','e0_long_command_domain_telemetry_v1.py','selected_telemetry_constructor_API_fixture_v1.py','e0_declared_entry_receipt_cli_contract_v1.py','e0_frozen_worker_call_guard_v1.py'):
 s=(OLD/n).read_text(encoding='utf8')
 for a,b in NAMES.items():s=s.replace(a,b).replace(a[:-3] if a.endswith('.py') else a,b[:-3] if b.endswith('.py') else b)
 write(n,s)
for a,b in NAMES.items():
 if a.endswith('.py'):
  s=(OLD/a).read_text(encoding='utf8').replace(OLDJOB,JOB)
  for x,y in NAMES.items():s=s.replace(x,y)
  # Module references without .py are explicit names; no broad expert replacement.
  s=s.replace('run_E0_new86_readonly_secure_stdin_v1','run_E0_new86_readonly_secure_stdin_v2_early').replace('E0_V4_','E0_V2_')
  write(b,s)
for n in ('e0_early_original_resample_passthrough_observer_v1.py','REQUIRED_TARGET_COMMANDTERM_METHOD_SOURCE_CONTRACT_V1.json'):
 write(n,(EARLY/n).read_bytes())
# One small derivative of actual SAMEHOST closed proof, not a new model read.
p=OLD/'reports/E0_V4_TERMINAL_ORIGINAL_RETURNED_ACTUAL.json';raw=p.read_bytes();v=json.loads(raw)
assert v['requested1000_controls_100warm_900steady_complete'] and v['original_terminal_and_allownout_proven'] and v['passed_original_frozen_execution']
write('E0_PREVIOUS_SAMEHOST_FULL1000_WITNESS.json',json.dumps(dict(kind='actual_samehost_E0_V1_complete1000_witness_reference_v1',received_original_report_path=str(p),received_original_report_SHA=H(raw),source_SHA=v['source_SHA'],old_job=OLDJOB,original_terminal=v['original_terminal'],native24=v['native24'],original_errors=v['original_errors'],integrity=v['integrity'],source_GPU_case_complete=True,no_model_decode_for_this_derivative=True),indent=2))
# Worker: only early observer and its evidence. The original numerical For loop stays EXACT.
p=B/NAMES['evaluate_E0_adapted82_new86_frozen1000_once_v1.py'];s=p.read_text(encoding='utf8')
a=' import torch,rescue_training\n';b=a+''' import directional_spin_runtime,sensor_resume_contract
 from e0_early_original_resample_passthrough_observer_v1 import EarlyResampleObserver
 early=EarlyResampleObserver(torch,OUT/'early_original_resample',expected_n=20000)
 early.install(directional_spin_runtime.DirectionalSpinCommand,sensor_resume_contract)
''';s=sub(s,a,b)
a="  panel=E0Panel(real,torch,OUT,task);oldterm="
b="""  panel=E0Panel(real,torch,OUT,task)
  early_adopted=early.verify_current_unchanged_at_first_control(cmd)
  if early_adopted:early.adopt_only_actually_observed_start(panel)
  packet=early.eligible
  put('ACTUAL_E0_EARLY_POSTRESTORE_RESAMPLE_BEFORE_MEAN_ACTION.json',dict(kind='E0_actual_postrestore_original_resample_admission_v2',source_SHA=MODEL_SHA,actual_CPU_report_SHA=task['actual_CPU_report_SHA'],observer_SHA=task['early_observer_SHA'],actual_original_postrestore_event_adopted=early_adopted,initial_left_censored=not early_adopted,observed_ids_count=len(packet['ids']) if packet is not None else 0,sampled_timer_min=float(packet['time_left'].min()) if packet is not None else None,sampled_timer_max=float(packet['time_left'].max()) if packet is not None else None,actual_phase_zero=bool((packet['phase']==0).all()) if packet is not None else False,actual_physics_tick=real._sim_step_counter,original_events=early.events,diagnostic_errors=early.errors,no_extra_reset_resample_RNG_actor=True))
  oldterm=""";s=sub(s,a,b)
s=sub(s," assert H(job/'e0_long_command_domain_telemetry_v1.py')==task['telemetry_component_SHA']", " assert H(job/'e0_long_command_domain_telemetry_v1.py')==task['telemetry_component_SHA']\n assert H(job/'e0_early_original_resample_passthrough_observer_v1.py')==task['early_observer_SHA']")
s=sub(s," finally:put('APP_CLOSING.json',dict(epoch=time.time()));ns['app'].close()", """ finally:
  try:early.finish()
  except BaseException:put('FROZEN_E0_EARLY_OBSERVER_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(epoch=time.time(),traceback=traceback.format_exc(),original_error_receipts_not_replaced=True))
  put('APP_CLOSING.json',dict(epoch=time.time()));ns['app'].close()""")
p.write_text(s,encoding='utf8',newline='\n')
# Measurement-only acted/zero-control denominators and streaming producer index.
p=B/'e0_observed_command_instances_v1.py';s=p.read_text(encoding='utf8');s=sub(s,'from e0_original_profile_catalog_v1 import','from e0_early_original_resample_passthrough_observer_v1 import produce_typed_instance_JSONL_with_stream_SHA\nfrom e0_original_profile_catalog_v1 import')
s=sub(s,'self.complete=self.closed.clone();self.reset=self.closed.clone();self.left=self.closed.clone();self.right=self.closed.clone();self.full12=self.closed.clone()', 'self.complete=self.closed.clone();self.reset=self.closed.clone();self.left=self.closed.clone();self.right=self.closed.clone();self.full12=self.closed.clone()\n        self.acted=self.closed.clone();self.zero=self.closed.clone();self.acted_left=self.closed.clone();self.acted_reset=self.closed.clone();self.acted_right=self.closed.clone();self.all_instance_controls=self.closed.clone()')
s=sub(s,'        self.closed[idx]+=1;self.complete[idx]+=full.long();self.reset[idx]+=int(reason==\'reset\')', "        acted=count>0\n        self.acted[idx]+=acted.long();self.zero[idx]+=(~acted).long();self.all_instance_controls[idx]+=count\n        self.acted_left[idx]+=(acted&~known).long();self.acted_reset[idx]+=acted.long()*int(reason=='reset');self.acted_right[idx]+=acted.long()*int(reason=='window_end')\n        self.closed[idx]+=1;self.complete[idx]+=full.long();self.reset[idx]+=int(reason=='reset')")
s=sub(s,'    def finish(self,out):','    def finish(self,out,source_SHA):')
s=sub(s,"rows.append(dict(profile=k,label=label,closed_instance_events=total,unique_env_with_closed_instance=int((self.closed[k]>0).sum()),", "rows.append(dict(profile=k,label=label,closed_instance_events=total,unique_env_with_closed_instance=int((self.closed[k]>0).sum()),acted_instance_events=int(self.acted[k].sum()),zero_control_instance_events=int(self.zero[k].sum()),unique_env_with_acted_instance=int((self.acted[k]>0).sum()),unique_env_with_zero_control_instance=int((self.zero[k]>0).sum()),all_acted_instance_population_controls=int(self.all_instance_controls[k].sum()),acted_initial_left_censored_events=int(self.acted_left[k].sum()),acted_reset_ended_events=int(self.acted_reset[k].sum()),acted_window_end_events=int(self.acted_right[k].sum()),")
start=s.index("        p=Path(out)/'E0_OBSERVED_COMMAND_INSTANCE_RECORDS_ACTUAL.jsonl'");end=s.index('        return dict(',start)
s=s[:start]+'''        def record_rows():
            for reason,columns in self.records:
                data={k:v.tolist() for k,v in columns.items()}
                for i in range(len(data['env_id'])):
                    row={k:v[i] for k,v in data.items()};row['end_reason']=reason
                    row['acted_instance']=row['population_controls']>0
                    row['fully_observed_original_command_lifetime']=bool(row['start_observed'] and reason=='resample' and row['acted_instance'])
                    row['start_control_is_first_observation_not_original_start']=not row['start_observed']
                    yield row
        p=Path(out)/'E0_OBSERVED_COMMAND_INSTANCE_RECORDS_ACTUAL.jsonl'
        producer=produce_typed_instance_JSONL_with_stream_SHA(out,p.name,record_rows(),source_SHA=source_SHA)
''' +s[end:]
s=sub(s,'return dict(profiles=rows,instance_record_rows=', 'return dict(profiles=rows,typed_JSONL_producer_index=producer,acted_and_zero_control_denominators_separate=True,instance_record_rows=')
p.write_text(s,encoding='utf8',newline='\n')
p=B/'e0_long_command_domain_telemetry_v1.py';s=p.read_text(encoding='utf8');s=sub(s,'instances=self.instances.finish(self.out)',"instances=self.instances.finish(self.out,self.task['source_SHA'])");p.write_text(s,encoding='utf8',newline='\n')
# Original numerical loop must be structurally identical to already-qualified V1.
def loop(raw):return next(n for n in ast.walk(ast.parse(raw)) if isinstance(n,ast.For) and isinstance(n.target,ast.Name) and n.target.id=='i' and isinstance(n.iter,ast.Call) and isinstance(n.iter.func,ast.Name) and n.iter.func.id=='range')
oldloop=ast.dump(loop((OLD/'evaluate_E0_adapted82_new86_frozen1000_once_v1.py').read_bytes()),include_attributes=False);newloop=ast.dump(loop((B/NAMES['evaluate_E0_adapted82_new86_frozen1000_once_v1.py']).read_bytes()),include_attributes=False);assert oldloop==newloop
write('SOURCE_V1_TO_V2_NUMERICAL_LOOP_AND_IMMUTABLE_INPUTS_PROOF.json',json.dumps(dict(passed=True,original_numerical_For_AST_exact=True,original_for_AST_SHA=H(oldloop.encode()),new_for_AST_SHA=H(newloop.encode()),baseline_source=str(OLD),new_namespace=JOB,old_source_not_modified=True,model_PD_DR_physics_clock_mean_actor_population_controls_caps_unchanged=True,new_changes='only early observer lifecycle, new path/task/source metadata, acted/zero counters, typed producer index/collector',source_only_no_model_raw_SDK_or_remote=True),indent=2))
write('EXPLICIT_PENDING_SOURCE_V2.json',json.dumps(dict(status='EXPLICIT_PENDING_SOURCE_ONLY',new_target=JOB,remaining='target SDK method fixture/actual source CPU metadata, samehostcopy route, first/normal producer graph, whole local lifecycle test and frozenhandoff',no_execution=True),indent=2))
(B/'reports').mkdir()
print(json.dumps(dict(passed_source_first_derivation=True,original_numerical_loop_AST_exact=True,new_target=JOB)))
