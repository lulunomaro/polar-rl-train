"""LOCAL source/JSON assembly only; no model/NPZ/USD/raw stat/hash/decode."""
from pathlib import Path
import ast,hashlib,json,time,traceback
B=Path(__file__).resolve().parent;L=B.parent
OLD=L/'E2_93_NEW86_ORIGINAL_FLAT_HEIGHT_PROVIDER_REPAIR_SOURCE_20261029_V4';EARLY=L/'E2_93_EARLY_ORIGINAL_RESAMPLE_LIFECYCLE_SOURCE_20261029_V1';E0=L/'E0_82_NEW86_EARLY_RESAMPLE_COMPLETE_CASE_SOURCE_20261029_V2'
ROOT0='/data/robemo/polar-rl-train/evaluation_runs/E2_ADAPTED93_PROFILE_DOMAIN_20261029v4/e2';ROOT='/data/robemo/polar-rl-train/evaluation_runs/E2_ADAPTED93_EARLY_RESAMPLE_20261029v5/e2'
K0='MOD4_E2_ADAPTED93_NEW86_FROZEN_PROFILE_DOMAIN_V1';K='MOD4_E2_ADAPTED93_NEW86_EARLY_RESAMPLE_COMMAND_INSTANCES_V5'
IDX='FROZEN_E2_93_NEW86_EARLY_RESAMPLE_COMPLETE_SOURCE_INDEX_V5.json';MF='E2_NEW86_COMPLETE_INPUT_MANIFEST_V1.json'
WORK='evaluate_E2_adapted93_new86_frozen900_once_v1.py';CPU='E2_new86_target_source_SDK_metadata_admission_v1.py';SUP='detached_E2_new86_frozen_profile_supervisor_once_v1.py';CODE='E2_frozen_actual_receipts_readonly_CODE_v4.py'
ENTRY='upload_admit_detach_NEW86_E2_final93_profiles_secure_stdin_UNUSED_once_v4_originalHeight.py';REMOTE='remote_E2_new86_profile_install_and_detach_v4_originalHeight.py'
HELPER='e2_early_original_resample_observer_v2_complete.py';INST='e2_observed_command_instances_v1.py'
ops=[]
def H(b):return hashlib.sha256(b).hexdigest()
def put(n,v):
 with (B/n).open('x',encoding='utf8',newline='\n') as f:json.dump(v,f,indent=2,allow_nan=False)
def write(n,b):
 with (B/n).open('xb') as f:f.write(b)
def change(s,a,b,count=1):
 assert s.count(a)==count,(a,s.count(a),count);ops.append(dict(old=a,new=b,count=count));return s.replace(a,b)
def main():
 m=json.loads((OLD/MF).read_bytes());selected={Path(r['local_path']).name for r in m['files'] if Path(r['local_path']).parent==OLD}
 selected|={ENTRY,REMOTE,'run_E2_new86_readonly_secure_stdin_v4.py','read_E2_new86_FIRST_native24_queue_secure_stdin_UNUSED_once_v4.py','collect_E2_new86_TERMINAL_fulltext_secure_stdin_UNUSED_once_v4.py'}
 deriv=[]
 for name in sorted(selected):
  raw=(OLD/name).read_bytes();s=raw.decode();start=len(ops)
  for a,b in ((ROOT0,ROOT),(K0,K),('FROZEN_E2_93_NEW86_PROFILE_DOMAIN_SOURCE_INDEX_V4.json',IDX)):
   if a in s:s=change(s,a,b,s.count(a))
  if name==WORK:
   s=change(s," from e2_profile_domain_telemetry_v1 import E2Panel"," from e2_profile_domain_telemetry_v1 import E2Panel\n from e2_early_original_resample_observer_v2_complete import E2EarlyObserver",1)
   s=change(s,'panel=E2Panel(real,torch,OUT,task);oldterm=',"panel=E2Panel(real,torch,OUT,task)\n  def adopt_initial_packet(packet):\n   panel.instances.control=0;panel.instances.open(packet['ids'],panel.instance_context(),True)\n  early_adopted=early.adopt_actual_written_start(panel,on_observed_start=adopt_initial_packet)\n  packet=early.eligible\n  put('ACTUAL_E2_EARLY_POSTRESTORE_RESAMPLE_BEFORE_MEAN_ACTION.json',dict(kind='E2_actual_postrestore_original_resample_admission_v5',source_SHA=MODEL_SHA,actual_original_postrestore_event_adopted=early_adopted,initial_left_censored=not early_adopted,observed_ids_count=len(packet['ids']) if early_adopted else 0,sampled_timer_min=float(packet['time_left'].min()) if early_adopted else None,sampled_timer_max=float(packet['time_left'].max()) if early_adopted else None,actual_phase_zero=bool((packet['phase']==0).all()) if early_adopted else None,actual_physics_tick=int(real._sim_step_counter),diagnostic_errors=early.errors,observer_SHA=H(job/'"+HELPER+"'),actual_CPU_report_SHA=task['actual_CPU_report_SHA']))\n  oldterm=",1)
   integration=""" from e2_directional_spin_runtime_v1 import DirectionalSpinCommand
 import sensor_resume_contract,e2_command_checkpoint_v1
 early=E2EarlyObserver(torch,OUT/'early_original_resample',expected_n=20000)
 early.install(DirectionalSpinCommand,sensor_resume_contract,e2_command_checkpoint_v1)
"""
   s=change(s,' rescue_training.learn=work\n',integration+' rescue_training.learn=work\n',1)
   s=change(s," finally:put('APP_CLOSING.json',dict(epoch=time.time()));ns['app'].close()"," finally:\n  try:early.finish()\n  finally:put('APP_CLOSING.json',dict(epoch=time.time()));ns['app'].close()",1)
   s=change(s,"assert H(__file__)==task['worker_SHA']","assert H(__file__)==task['worker_SHA']\n assert H(job/'"+HELPER+"')==task['early_observer_SHA'] and H(job/'"+INST+"')==task['command_instances_SHA']",1)
  if name=='e2_profile_domain_telemetry_v1.py':
   s=change(s,'import gzip,json,math,types','import gzip,json,math,types\nfrom e2_observed_command_instances_v1 import CommandInstances',1)
   s=change(s,'self.episode=t.zeros(e.num_envs,device=e.device,dtype=t.long);self.command_uid=self.episode.clone()','self.episode=t.zeros(e.num_envs,device=e.device,dtype=t.long);self.command_uid=self.episode.clone()\n        self.instances=CommandInstances(t,e.num_envs,e.device);self.initial_start_adopted=False',1)
   s=change(s,'result=panel.old_reset(ids);selected=t.as_tensor(ids,device=e.device,dtype=t.long);panel.episode[selected]+=1',"selected=t.as_tensor(ids,device=e.device,dtype=t.long);panel.instances.close(selected,'reset');panel.episode[selected]+=1\n            result=panel.old_reset(ids)",1)
   s=change(s,'result=panel.old_resample(ids);panel.command_uid[ids]+=1',"selected=t.as_tensor(ids,device=e.device,dtype=t.long);panel.instances.close(selected,'resample')\n            result=panel.old_resample(ids);panel.command_uid[selected]+=1\n            panel.instances.open(selected,panel.instance_context(),True)",1)
   ctx="""    def instance_context(self):
        term=self.cmd;t=self.t
        return dict(key=classify(t,term.is_standing_env,term.is_pure_spin,term.is_moving_spin,term.is_transition_spin,term.command,term.signed_yaw),episode=self.episode,command_uid=self.command_uid,command=term.command,direction=term.world_direction,signed_yaw=term.signed_yaw)

"""
   s=change(s,'    def begin(self,index,obs):',ctx+'    def begin(self,index,obs):\n        self.instances.control=index+1',1)
   s=change(s,"self.book.observe(c,after,tm.terminated,tm.time_outs,[tm.get_term(k).bool() for k in self.names])","self.book.observe(c,after,tm.terminated,tm.time_outs,[tm.get_term(k).bool() for k in self.names]);self.instances.observe(c,after)",1)
   s=change(s,"self.uninstall();self.book.export(self.out/'E2_profile_phase_env_actual_denominators.npz')","self.uninstall();instances=self.instances.finish(self.out,self.task['source_SHA']);self.book.export(self.out/'E2_profile_phase_env_actual_denominators.npz')",1)
   s=change(s,"source_model_SHA=self.task['source_SHA']","command_instances=instances,source_model_SHA=self.task['source_SHA']",1)
   s=change(s,'first_written_phase_valid_initially_unknown=True','initial_written_phase_valid_from_actual_early_adoption=bool(self.initial_start_adopted),initial_left_censored=not bool(self.initial_start_adopted)',1)
  if name==CPU:
   insert=""" from e2_complete_case_source_contract_v5 import validate_installed_complete_case
 complete_contract=validate_installed_complete_case(J,m,Path(modules['isaaclab']).parent/'app/app_launcher.py')
 from E2_actual_target_early_method_CPU_fixture_v5 import run_actual_target_lifecycle
 command_path=Path(modules['isaaclab']).parent/'managers/command_manager.py';velocity_path=Path(modules['isaaclab']).parent/'envs/mdp/commands/velocity_command.py'
 method_lifecycle=run_actual_target_lifecycle(J,command_path.read_bytes(),velocity_path.read_bytes(),actual_target=True)
"""
   s=change(s,' result=dict(passed=True,kind=',insert+' result=dict(passed=True,kind=',1)
   s=change(s,'selected_constructor_fresh_CPU_API_fixture=constructor_proof,','selected_constructor_fresh_CPU_API_fixture=constructor_proof,complete_entry_CLI_source_receipt_contract=complete_contract,actual_target_CommandTerm_method_lifecycle=method_lifecycle,actual_target_CommandTerm_source_SHA=H(command_path),actual_target_velocity_source_SHA=H(velocity_path),',1)
  if name==REMOTE:
   s=change(s,'full_WM_tap_included=False)',"full_WM_tap_included=False,early_observer_SHA=H(J/'"+HELPER+"'),command_instances_SHA=H(J/'"+INST+"'),command_instance_producer_metadata_only=True)",1)
  ast.parse(s) if name.endswith('.py') else None;write(name,s.encode());deriv.append(dict(name=name,source_SHA=H(raw),selected_SHA=H(s.encode()),operations=ops[start:]))
 # E2-specific early observer extended only with observer-buffer adoption metadata
 # and streaming initial JSONL producer; original sampler code remains external.
 raw=(EARLY/'e2_early_original_resample_observer_v1.py').read_bytes();s=raw.decode()
 s=s.replace("if on_observed_start is not None:on_observed_start(p)","panel.initial_start_adopted=True\n  if on_observed_start is not None:on_observed_start(p)",1)
 s=s.replace('complete_command_instance_accumulator_NOT_included=True','complete_command_instance_accumulator_in_separate_component=True',1)
 s=s.replace("with (self.out/'E2_ORIGINAL_EARLY_RESAMPLE_WRITE_OBSERVER_ACTUAL.json').open", "if self.eligible is not None:\n   p=self.eligible;columns={k:v.detach().cpu().tolist() for k,v in p.items() if self.t.is_tensor(v)}\n   rows=({k:v[i] for k,v in columns.items()} for i in range(len(p['ids'])))\n   result['real_initial_sampled_command_JSONL_producer']=produce_typed_instance_JSONL_with_stream_SHA(self.out,'E2_REAL_INITIAL_SAMPLED_COMMANDS_ACTUAL.jsonl',rows)\n  with (self.out/'E2_ORIGINAL_EARLY_RESAMPLE_WRITE_OBSERVER_ACTUAL.json').open",1)
 base=(E0/'e0_early_original_resample_passthrough_observer_v1.py').read_text();prod=base[base.index('def produce_typed_instance_JSONL_with_stream_SHA('):];s+='\n\n'+prod;ast.parse(s);write(HELPER,s.encode())
 # Generic bookkeeping arithmetic reused, E2 catalog/producer/record domain explicit.
 raw=(E0/'e0_observed_command_instances_v1.py').read_bytes();s=raw.decode().replace('Read-only E0 command lifetimes','Read-only E2 command lifetimes').replace('from e0_early_original_resample_passthrough_observer_v1 import','from e2_early_original_resample_observer_v2_complete import').replace('from e0_original_profile_catalog_v1 import','from e2_original_profile_catalog_candidate_v1 import').replace('E0_OBSERVED_COMMAND_INSTANCE_RECORDS_ACTUAL.jsonl','E2_OBSERVED_COMMAND_INSTANCE_RECORDS_ACTUAL.jsonl')
 s=s.replace('self.count=self.uid.clone();self.error=',"self.first_acted=t.full_like(self.uid,-1);self.last_acted=t.full_like(self.uid,-1)\n        self.count=self.uid.clone();self.error=",1)
 s=s.replace('self.start[ids]=self.control;self.count[ids]=0;','self.start[ids]=self.control;self.first_acted[ids]=-1;self.last_acted[ids]=-1;self.count[ids]=0;',1)
 s=s.replace("self.count+=1;self.error+=self.t.stack(after['errors'],1)","self.first_acted=self.t.where(self.count==0,self.t.full_like(self.first_acted,self.control),self.first_acted);self.last_acted[:]=self.control\n        self.count+=1;self.error+=self.t.stack(after['errors'],1)",1)
 s=s.replace('start_observed=self.known[take],first_control=self.start[take],population_controls=self.count[take],','start_observed=self.known[take],observed_boundary_control=self.start[take],first_acted_control=self.first_acted[take],last_acted_control=self.last_acted[take],close_boundary_control=self.t.full_like(take,self.control),population_controls=self.count[take],',1)
 s=s.replace("row['start_control_is_first_observation_not_original_start']=not row['start_observed']","row['boundary_is_first_observation_not_original_start']=not row['start_observed']\n                    row['first_acted_control_is_minus1_for_zero_control']=row['first_acted_control']==-1\n                    row['actual_policy_dt_s']=.02\n                    row['source_domain']='E2_WORLD_MOVING_SIGNED4'",1)
 s=s.replace('initial_instances_left_censored=True','initial_instances_left_censored=bool((self.left>0).any())',1);ast.parse(s);write(INST,s.encode())
 # True E2 entry/CLI/learnhook contract derives from generic proven parser, explicit names.
 s=(E0/'e0_declared_entry_receipt_cli_contract_v1.py').read_text()
 changes=[('runtime/isaac/mod4/train_chassis_pd_resume_ppo.py','runtime/isaac/mod4/train_E2_full_resume_v1.py'),('f7ab426fe81444b1c5d0bae7db8173e1309dbbe4fec9eea16006cb7404aad135','e002234d12146cba31e6350e3ede6b362a66a5644b9404429d863512c6183812'),('evaluate_E0_adapted82_new86_frozen1000_once_v2_early.py',WORK),('detached_E0_new86_frozen_profile_supervisor_once_v2_early.py',SUP),('E0_frozen_actual_receipts_readonly_CODE_v2_early.py',CODE),('ACTUAL_NATIVE24_E0_40050_CLOCK_QUEUE.json','ACTUAL_NATIVE24_E2_40050_CLOCK_QUEUE.json'),("'.00038443359375000017'","'.00022500000000000002'"),('E0_new86_target_source_SDK_metadata_admission_v2_early.py',CPU)]
 for a,b in changes:
  assert a in s,(a,'entry contract');s=s.replace(a,b)
 ast.parse(s);write('e2_declared_entry_receipt_cli_contract_v5.py',s.encode())
 # Copy small already-saved E2 lifecycle source contracts/reference texts only.
 for name in ('REQUIRED_ACTUAL_E2_TARGET_METHOD_AND_DOMAIN_SOURCE_CONTRACT.json','E2_V4_INITIAL_RESAMPLE_GAP_SAVED_TEXT_AND_SOURCE_ORDER_EVIDENCE.json'):
  write(name,(EARLY/name).read_bytes())
 # Bound old samehost full900 evidence without another PT decode or reading large inputs.
 p=OLD/'reports/E2_V4_TERMINAL_ORIGINAL_RETURNED_ACTUAL.json';raw=p.read_bytes();v=json.loads(raw);require=v['passed_original_frozen_execution'] and v['requested900_controls_100warm_800steady_complete'] and v['original_terminal_and_allownout_proven'];assert require
 put('E2_PREVIOUS_SAMEHOST_FULL900_WITNESS.json',dict(passed_actual_samehost_full900=True,original_terminal_path=str(p),original_terminal_bytes=len(raw),original_terminal_SHA=H(raw),source_SHA=v['source_SHA'],native24=v['native24'],result=v['original_terminal']['result'],actual_waited=v['original_terminal']['actual_worker_waited'],returncode=v['original_terminal']['returncode'],private_EX_released=v['original_terminal']['private_EX_released'],known_original_supervisor=v['original_terminal']['supervisor'],known_original_worker=v['original_terminal']['worker'],original_errors=v['original_errors'],integrity=v['integrity'],not_a_new_model_CPU_load=True))
 m['target_stage']=m['target_root']=ROOT;m['kind']='E2_93_early_original_resample_complete_command_instance_case_SOURCE_ONLY_v5';m['source_version']='NEW V5 early callbacks +E2 instance denominators and producer metadata; no numeric worker loop change';m['coverage']=dict(num_envs=20000,controls=900,warmup100_steady800=True,simulated_seconds=18,original_command_domain='E2_WORLD_MOVING_SIGNED4',new_observer_not_new_sampler=True,no_skill_graduation=True)
 for r in m['files']:
  p=Path(r['local_path'])
  if p.parent==OLD:
   p=B/p.name;r.update(local_path=str(p),bytes=p.stat().st_size,SHA=H(p.read_bytes()))
 for name in (HELPER,INST,'e2_declared_entry_receipt_cli_contract_v5.py','REQUIRED_ACTUAL_E2_TARGET_METHOD_AND_DOMAIN_SOURCE_CONTRACT.json','E2_V4_INITIAL_RESAMPLE_GAP_SAVED_TEXT_AND_SOURCE_ORDER_EVIDENCE.json','E2_PREVIOUS_SAMEHOST_FULL900_WITNESS.json','E2_actual_target_early_method_CPU_fixture_v5.py','e2_complete_case_source_contract_v5.py','e2_producer_metadata_only_read_contract_v5.py'):
  p=B/name;assert p.is_file(),name;m['files'].append(dict(relative=name,local_path=str(p),bytes=p.stat().st_size,SHA=H(p.read_bytes()),index_kind='new_source_or_existing_saved_text_metadata'))
 assert len({r['relative'] for r in m['files']})==len(m['files']);put(MF,m)
 put('SELECTED_E2_V5_SOURCE_DERIVATION_AND_ORIGINAL_WORKER_INVERSE_OPERATIONS.json',dict(files=deriv,no_existing_PT_NPZ_USD_raw_stat_hash_or_decode=True,original_model_input_metadata_preserved=True,new_no_learning_scope=True))
 print(json.dumps(dict(prepared=True,inputs=len(m['files']),worker_SHA=H((B/WORK).read_bytes()),target=ROOT)))
if __name__=='__main__':
 try:main()
 except BaseException:put('LOCAL_E2_V5_ASSEMBLY_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(traceback=traceback.format_exc(),no_old_binary_or_remote=True));raise
