"""UNUSED native88 formal FINAL initial CPU review. No R5 native model reread.

One initial load per new FINAL; one shared qualified normal86 frozen witness.
No actor/WM/critic forward, replay, scene, rollout, GPU or account write.
"""
from pathlib import Path
import sys
sys.path[:0]=[str(Path(__file__).resolve().parent),str(Path(__file__).resolve().parents[1]/'native88C_exact_reset_bank_lifecycle_source_v1')]
import argparse,os,json,hashlib,time,traceback,importlib.util
from native88_closing_protocol_v1 import (KEYS,SOURCES,BOOTSTRAP_SHA,require,validate_detached,validate_actual_GO_binding,validate_fees,native_window,verify_window,bind_prepared_detached)
from native88_initial_CPU_reader_primitives_v1 import (OneInitialLoadPool,PinnedSource,exact,finite,frozen_bootstrap,native_modules,original_physical_state,role_terminal)
from native88_event_curve_summary_v1 import read_curve
import native88_initial_CPU_reader_primitives_v1 as repaired_primitives
require(Path(repaired_primitives.__file__).resolve()==Path(__file__).resolve().parent/'native88_initial_CPU_reader_primitives_v1.py','exact new primitives import path')
require(hashlib.sha256(Path(repaired_primitives.__file__).read_bytes()).hexdigest()=='da0c81ae801c768578f199f280d86c73c2fd69a86ed16c56d31b7560d991a63f','exact dependency-only source repair')
def read(p):return json.loads(Path(p).read_bytes())
def H(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def put(R,name,v):
 with (R/name).open('x',encoding='utf8') as f:json.dump(v,f,indent=2,allow_nan=False)
def load_pinned_module(name,relative,pins):
 path=pins.B/relative;require(H(path)==pins.rows[relative]['SHA'],'actual CPU review imported source pin '+relative)
 sp=importlib.util.spec_from_file_location(name,path);module=importlib.util.module_from_spec(sp);sp.loader.exec_module(module);return module
def eligible_formal_roles(receipt,q):
 eligible=[];errors={}
 for key in KEYS:
  try:
   commit=role_terminal(receipt,key);native_window(commit,q['specs'][key]);rows=receipt['native_H1_method_fullstate'][key]
   require(len(rows)==1 and rows[0]['formal_manifest_passed'] is True and rows[0]['twohost_complete_SHA'] is True and rows[0]['SHA']==commit['final']['SHA'],'formal new native88 twohost FINAL required')
   require(rows[0]['SHA'] not in {BOOTSTRAP_SHA,*[s['SHA'] for s in SOURCES.values()]},'old native/RSL source cannot become new FINAL')
   eligible.append(key)
  except BaseException:errors[key]=traceback.format_exc()
 return eligible,errors
def review_role(full,witness,commit,spec,collected,pins,out):
 import torch
 finite(full);progress=native_window(commit,spec);publication=full['UniSuperMimic_publication'];window=publication['native88_migration_window'];c=verify_window(window,spec,True)
 sys.path[:0]=[str(pins.B),str(pins.B/'source'),str(pins.B/'source/sm_deps'),str(pins.B/'lib'),str(pins.B/'job0/runtime/isaac/mod4')]
 finalizer=load_pinned_module('native88_finalizer_initial_CPU_'+spec['key'],'source/native_finalization_own88_gas400.py',pins)
 finalizer.verify_native(full,publication)
 from native88_gas400_migration_v1 import NATIVE_CONTRACT
 require(exact(full['UniSuperMimic_test_contract'],NATIVE_CONTRACT),'new output NATIVE_CONTRACT exact types and values')
 require(NATIVE_CONTRACT['changed_plant700_to_nominal400'] is True and NATIVE_CONTRACT['native_objective_changed'] is True and NATIVE_CONTRACT['original_physics_and_success_unchanged'] is False,'changed plant/objective explicit output')
 final=commit['final'];producer=publication['producer'];native=full['UniSuperMimic_H1_test']
 require(exact(publication['native88_migration_window'],final['native88_migration_window']) and exact(full['UniSuperMimic_changed_plant_migration'],window),'formal/saved migration literal exact')
 require(native['iteration']==publication['native_iteration']==final['updates']==c['native_iteration'],'native final iteration source/window')
 require(native['sim_steps']-c['window_start_sim_steps']==c['completed_fresh_controls']*4096,'new actual complete transition denominator')
 for name in ('world_updates','policy_updates','run_token','save_token','producer'):require(exact(publication[name],final[name]),'atomic final publication '+name)
 require(producer['initial_native_source']==SOURCES[spec['key']] and producer['bootstrap_task_source_SHA']==BOOTSTRAP_SHA and producer['bootstrap_Adam']==832460,'native source distinct frozen witness')
 for name in ('gas400_parameter_source_contract_SHA','actual_gas400_asset_composition_report_SHA','own_step_objective_qualification_SHA'):require(producer[name]==spec[name],'actual typed producer '+name)
 require(producer['bridge_source_SHA']==pins.rows['source/native_own_fudan88_gas400_training_v2.py']['SHA'] and producer['finalization_source_SHA']==pins.rows['source/native_finalization_own88_gas400.py']['SHA'],'actual native publisher source bytes')
 objective_path=out/'NATIVE_OWN_REFERENCE_OBJECTIVE_CONTRACT_ACTUAL.json';require(H(objective_path)==spec['objective_contract_SHA']==producer['runtime_objective_contract_SHA'],'actual V2 objective contract')
 objective=read(objective_path);require(objective['schema']=='mod4.native88.own_wheel_step_objective.source_candidate.v2' and objective['selected_candidate'] is True and objective['physical_V8_and_success_unchanged'] is True,'selected positive own-wheel objective, original physical truth')
 pre=read(out/'NATIVE88_ACTUAL_GPU_PRECONTROL_ADMISSION.json')
 require(pre['actual_GPU_runtime_readback_passed'] is True and pre['before_first_native_physical_control_and_Pi'] is True and pre['actual_environment_count']==4096,'actual new4096 GPU readback')
 require(pre.get('original_first_reset_completed') is True,'original actual first reset did not complete')
 require(pre['source_SHA']==spec['source_SHA'] and pre['frozen_RSL_bootstrap_SHA']==BOOTSTRAP_SHA and pre['actual_reference_SHA']==spec['reference_artifact_SHA'],'actual source/witness/reference')
 require(pre['actual_static_context_dim']==31 and pre['actual_dynamic_aux_dim']==54 and pre['packed_state_dim']==127 and pre['actor_obs_dim']==86 and pre['goal_frame_dim']==146,'actual native dims')
 require(pre['actual_physics_dt']==.0025 and pre['actual_control_dt']==.01 and pre['actual_solver']==[1,32,4] and pre['original_true_physical_success_unchanged'] is True,'original solver/clock/success')
 contract=read(pins.B/'NATIVE88_SOURCE_CONTRACT_ACTUAL.json')
 require(pre['actual_joint_names']==contract['expected_runtime_joint_names'] and len(pre['actual_body_names'])==31 and pre['actual_leg_encoder_names']==objective['actual_leg_encoder_joint_names'],'actual ordered30/body31/encoder objective mapping')
 rsl=pre['actual_source_frozen_RSL_witness'];require(rsl['frozen_RSL_actor9_critic8_STD6_17Adam832460_exact'] is True and rsl['old700N_environment_DR_not_restored'] is True and pre['new_native_model_initialization'] is False,'restored models + fresh plant')
 gas=pre['actual_new_gas_parameters'];require(gas['actual_new_gas_parameters_passed'] is True and gas['nominal_stiffness_N_m']==2000. and gas['actual_hardlimits_backend_and_buffer_passed'] is True,'actual400N nominal/backend/hard limits')
 physical_name=contract.get('physical_precontrol_filename','NATIVE87_ACTUAL_BEFORE_FIRST_CONTROL_ADMISSION.json');require(Path(physical_name).name==physical_name,'contained physical precontrol report')
 plant=read(out/physical_name);require(plant['passed'] is True and plant['actual_fresh_D0_D7_backend_readback_passed'] is True and plant['actual_DR_audit']['actual_parameters_pass'] is True and plant['native700N_environment_DR_not_restored'] is True and plant['before_first_control_and_Pi'] is True,'actual new physical state proof')
 frozen=frozen_bootstrap(full,witness);physical=original_physical_state(full,pins);modules=native_modules(native,pins,spec['seed'])
 # Optimizer counters are native WM/Pi counters. No PPO20Adam rule is used.
 for name,counter in (('opt_wm','world_updates'),('opt_pi','policy_updates')):
  row=modules['three_optimizers'][name];require(row['min_step']==row['max_step']==publication[counter],'native optimizer/publication counter '+name)
 recipe=full['spring_pressure_recipe'];require(recipe['nominal_stiffness_N_m']==2000 and recipe['actual_stiffness_bounds_N_m']==[1800,2200],'new gas fullsave recipe')
 phase_path=out/'NATIVE_POLICY_PHASE_SAMPLE_COVERAGE_ACTUAL.json';phase=None;phase_error=None
 if phase_path.is_file():
  try:phase=read(phase_path)
  except BaseException:phase_error=traceback.format_exc()
 return dict(passed=True,key=spec['key'],seed=spec['seed'],final=collected,native_source_SHA=spec['source_SHA'],bootstrap_SHA=BOOTSTRAP_SHA,
  native_progress=progress,new_NativeContract_exact=True,whole_native_fullstate_finite=True,native_modules=modules,frozen_bootstrap=frozen,original_saved_D0_D7=physical,
  actual_GPU_precontrol=pre,actual_physical_precontrol=plant,actual_objective_contract=objective,
  original_first_reset_completed=True,reset_bank_exact_compatibility_source_CPU=pre.get('reset_bank_exact_compatibility_source_CPU'),reset_bank_source_proof_not_GPU_physics=True,
  optional_phase=dict(optional=True,model_gate=False,value=phase,reader_error=phase_error,counts_attempted_starts_not_completed_Pi=True),
  native_not_normal_H1_E2_or_recovery_production_source=True,not_physical_skill_graduation=True)
def main():
 os.environ['CUDA_VISIBLE_DEVICES']=''
 p=argparse.ArgumentParser()
 for name in ('stage','prepared-report','detached-report','collected-report','cpu-report','bootstrap-witness'):p.add_argument('--'+name,required=True)
 p.add_argument('--bootstrap-bytes',type=int,default=16868635);a=p.parse_args();N=Path(a.stage).resolve();R=N/'reports'
 require(N.name=='H1_STEP270_OWN_STEP_GAS400_NATIVE_RESOURCE_V88C_20261027','new88B review stage only')
 prepared=read(a.prepared_report);q=bind_prepared_detached(read(a.detached_report),prepared);validate_detached(q,prepared);receipt=read(a.collected_report);cpu=read(a.cpu_report)
 require(receipt['actual_finite_transport_returned'] is True and receipt['run_id']==q['run_id'] and receipt['active_keys']==list(KEYS),'actual same-run transport')
 validate_actual_GO_binding(receipt['authority72']['cohort']['go'],q)
 require(receipt['prepared_report_SHA']==H(a.prepared_report) and receipt['detached_report_SHA']==H(a.detached_report),'closing prepared/deployment receipt pins')
 eligible,meta_errors=eligible_formal_roles(receipt,q)
 if not eligible:
  put(R,'NATIVE88C_READER_REPAIRED_NO_FORMAL_FINAL_CPU_METADATA_ACTUAL.json',dict(passed=False,errors=meta_errors,no_checkpoint_or_bootstrap_model_read=True,original_canonical_cost_settled=receipt['original_canonical_cost_settled']));return False
 expected=N.parent/'H1_STEP270_THREE_GPU_NATIVE_CONTINUATION_RESOURCE_V86B_20261026/current_baseline_closed_models/h1/model_update138.pt'
 require(Path(a.bootstrap_witness).resolve()==expected.resolve() and a.bootstrap_bytes==16868635,'qualified normal86 witness exact original path/producer size')
 prior_path=R/'NATIVE88_TYPED_FINALS_AND_ORIGINAL_COST_CPU_ACTUAL.json'
 prior=read(prior_path);records=prior['initial_model_load_records']
 require(prior['passed'] is False and set(prior['errors'])==set(KEYS),'preserve exact original failed two-role reader')
 require(all("NameError: name 'H' is not defined" in prior['errors'][k] for k in KEYS),'only exact source dependency failure admitted')
 require(len(records)==1 and records[0]['completed'] is True and records[0]['producer_SHA']==BOOTSTRAP_SHA,'only old shared witness loaded; no NEW FINAL initial load was attempted')
 require(receipt['all_active_node_collection_passed'] is True and not receipt['collection_errors'],'actual complete case-safe collection required')
 # Actual source/metadata preflight before any required witness reread or NEW model load.
 for key in KEYS:
  spec=q['specs'][key];pins=PinnedSource(prepared['payloads'][key],spec)
  protocol=load_pinned_module('native88_repaired_preflight_'+key,'native88_protocol_v1.py',pins)
  envelope=cpu['results'][key]['ready_envelope']
  require(envelope['value'].get('exact_gas400_reset_bank_source_CPU_passed') is True,'actual installed source CPU reset proof')
  require(protocol.native88_valid_ready(dict(key=key,phase='ready',manifest_SHA=spec['manifest_SHA'],closed_source_CPU=envelope,original_error=False),spec),'original actual ready guard unchanged')
 put(R,'NATIVE88C_READER_REPAIRED_SOURCE_METADATA_PREFLIGHT_ACTUAL.json',dict(passed=True,old_failed_reader_report=str(prior_path),old_report_SHA=H(prior_path),old_load_records=records,NEW_FINAL_initial_loads_before_this_entry=0,shared_witness_prior_loads=1,additional_shared_witness_read_required_for_literal_frozen_comparison=True,not_a_replay_of_old_once=True))
 intent=dict(epoch=time.time(),purpose='complete actual88C formal qualification after pure-source H/read dependency repair; first2NEW FINAL loads plus1necessary shared witness reread',run_id=q['run_id'],
  each_new_FINAL_initial_load_maximum=1,shared_witness_reads_in_this_new_purpose=1,prior_shared_witness_loads=1,necessary_witness_reread_reason='old reader process exited before both NEW FINAL loads; literal frozen comparison requires the shared witness in this process',normal86_producer_SHA=BOOTSTRAP_SHA,
  R5_native_models_not_reloaded_or_rehashed=True,no_actor_WM_forward_GPU_scene_or_raw=True,no_retry_after_initial_error=True)
 put(R,'NATIVE88C_READER_REPAIRED_INITIAL_CPU_REVIEW_INTENT_ACTUAL.json',intent);put(R,'NATIVE88C_READER_REPAIRED_INITIAL_CPU_ENTRY_CONSUMED_ACTUAL.json',dict(epoch=time.time(),pid=os.getpid(),argv=sys.argv,intent=intent))
 import torch
 torch.set_num_threads(2);pool=OneInitialLoadPool();models={};errors=dict(meta_errors);fees=None;curves={};witness=None
 try:fees=validate_fees(receipt['authority72'],receipt['authority72']['cohort']['go'],q['owner_identity'])
 except BaseException:errors['original_fees']=traceback.format_exc();put(R,'NATIVE88C_READER_REPAIRED_ORIGINAL_FEE_CPU_ERROR_ACTUAL.json',dict(error=errors['original_fees'],original_flags_unmodified=True))
 try:witness=pool.load_qualified_shared_source(expected,16868635)
 except BaseException:errors['shared_normal86_witness']=traceback.format_exc();put(R,'NATIVE88C_READER_REPAIRED_SHARED_WITNESS_INITIAL_CPU_ORIGINAL_ERROR_ACTUAL.json',dict(error=errors['shared_normal86_witness'],no_second_initial_load=True))
 seen=set()
 for key in KEYS:
  out=N/'current_native88_closed_text'/key/'job0/production';nodefinal=((receipt.get('nodes',{}).get(key,{}).get('node_terminal') or {}).get('row') or {}).get('final') or {}
  curves[key]=read_curve(out/'ACTUAL_H1_CONVERGENCE_CURVE.jsonl',(nodefinal.get('final') or {}).get('original_H1_events'))
  if key not in eligible:continue
  try:
   spec=q['specs'][key];pins=PinnedSource(prepared['payloads'][key],spec);sys.path[:0]=[str(pins.B),str(pins.B/'source'),str(pins.B/'source/sm_deps')]
   protocol=load_pinned_module('native88_installed_protocol_initial_CPU_'+key,'native88_protocol_v1.py',pins)
   envelope=cpu['results'][key]['ready_envelope']
   require(envelope['value'].get('exact_gas400_reset_bank_source_CPU_passed') is True,'fresh installed exact gas400 reset-bank source CPU proof required')
   require(protocol.native88_valid_ready(dict(key=key,phase='ready',manifest_SHA=spec['manifest_SHA'],closed_source_CPU=envelope,original_error=False),spec),'actual installed-source CPU + waited proof exact ready')
   row=receipt['native_H1_method_fullstate'][key][0];require(row['SHA'] not in seen,'distinct two seed new FINAL');seen.add(row['SHA'])
   path=Path(row['local_path']).resolve();require(path.is_relative_to((N/'current_native88_method_fullstate'/key/'formal').resolve()),'collected new88 formal model containment')
   full=pool.load(path,row['SHA'],key+'_native88_FORMAL_FINAL');require(witness is not None,'normal86 frozen witness unavailable; no FINAL reload')
   value=review_role(full,witness,role_terminal(receipt,key),spec,row,pins,out);value['original_actual_role_cost_unmodified']=receipt['authority72']['original_segment']['experts'][key]
   value['event_curve']=curves[key];models[key]=value
   put(R,'NATIVE88C_READER_REPAIRED_HEALTHY_'+key.upper()+'_INITIAL_CPU_ACTUAL.json',dict(passed=True,value=value,independent_healthy_role_only=True,not_overall_pass=True))
  except BaseException:errors[key]=traceback.format_exc();put(R,'NATIVE88C_READER_REPAIRED_'+key.upper()+'_INITIAL_CPU_ORIGINAL_ERROR_ACTUAL.json',dict(error=errors[key],other_healthy_role_retained=True,no_second_initial_load=True))
 require(not torch.cuda.is_initialized(),'CPU review initialized CUDA')
 passed=set(models)==set(KEYS) and fees is not None and not errors
 result=dict(schema='mod4.native88.two_native.changed_plant_own_step.initial_CPU.v1',epoch=time.time(),passed=passed,models=models,errors=errors,original_fees=fees,
  original_canonical_cost_settled=receipt['original_canonical_cost_settled'],initial_model_load_records=pool.records,intent=intent,CUDA_initialized=False,
  R5_native_models_not_reloaded_or_rehashed=True,no_new_fee_refund_clamp_or_secondwriter=True,not_skill_graduation=True)
 put(R,'NATIVE88C_READER_REPAIRED_TYPED_FINALS_AND_ORIGINAL_COST_CPU_ACTUAL.json',result)
 put(R,'NATIVE88C_READER_REPAIRED_EVENT_CURVE_TEXT_SUMMARY_ACTUAL.json',dict(curves=curves,diagnostic_errors=errors,not_model_or_skill_gate=True))
 lines=['Native88 events: actual completed controls x4096; interval censored; restored source counters are not new progress.']
 for key,value in curves.items():
  latest=value.get('latest_complete_snapshot') or {};lines.append(key+': '+json.dumps(dict(diagnostic_passed=value['diagnostic_passed'],complete_controls=latest.get('control'),environment_control_transitions=latest.get('control',0)*4096,events=latest.get('counts'),intervals=value['event_increment_intervals'])))
 with (R/'NATIVE88C_READER_REPAIRED_EVENT_CURVE_TEXT_SUMMARY_ACTUAL.txt').open('x',encoding='utf8') as f:f.write('\n'.join(lines)+'\n')
 print(json.dumps(dict(passed=passed,healthy_native=list(models),errors=list(errors))));return passed
if __name__=='__main__':
 try:sys.exit(0 if main() else 1)
 except SystemExit:raise
 except BaseException:
  if '--stage' in sys.argv:
   R=Path(sys.argv[sys.argv.index('--stage')+1])/'reports'
   if R.is_dir():put(R,'NATIVE88C_READER_REPAIRED_REVIEW_ENTRY_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),no_second_initial_model_load=True))
  raise
