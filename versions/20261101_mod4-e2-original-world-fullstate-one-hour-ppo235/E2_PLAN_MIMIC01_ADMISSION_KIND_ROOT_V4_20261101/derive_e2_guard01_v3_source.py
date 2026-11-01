"""One independent LOCAL source derivation, no runtime or model imports."""
from pathlib import Path
import ast,hashlib,json,time,traceback
N=Path(__file__).resolve().parent;T=N.parent;R=N/'reports'
S=T/'E2_QUALIFIED_FULLSTATE_SOLO_PPO_SOURCE_NEXT_V1_20261101'
F=T/'E2_QUALIFIED_FULLSTATE_SOLO_PPO_SAVE_FINITE_V2_20261101'
C=T/'E2_QUALIFIED_FULLSTATE_SOLO_ROOT_CALLERS_PY314_V2_20261101'
P=T/'OLD_EXPERTS_NORMALIZATION_NEXT_READY_SOURCE_V213_20261101/source'
def put(p,v):
 with p.open('x',encoding='utf8') as f:json.dump(v,f,indent=2,allow_nan=False)
def ref(p):
 b=p.read_bytes();return dict(path=str(p),bytes=len(b),SHA=hashlib.sha256(b).hexdigest())
def write(p,s):
 ast.parse(s)
 with p.open('x',encoding='utf8',newline='\n') as f:f.write(s)
def once(s,a,b):
 assert s.count(a)==1,(a,s.count(a));return s.replace(a,b)
def row(p,relative):
 x=ref(p);return dict(relative=relative,local_path=str(p),bytes=x['bytes'],SHA=x['SHA'])

def main():
 assert json.loads((R/'DERIVE_GUARD01_V3_PURPOSE_FROZEN.json').read_bytes())['executions']==1
 assert ref(C/'INDEX_E2_SOLO_ROOT_CALLERS_FROZEN.json')['SHA']=='e1226e2b0401bdb3244d7669d285f11e78c508319d44d32c815bd8f0b791496c'
 put(R/'DERIVE_GUARD01_V3_ONCE_CONSUMED.json',dict(epoch=time.time(),source_only=True))
 entry=(P/'train_e2_213.py').read_text(encoding='utf8')
 entry=once(entry,'    env = Mod4Env(cfg=cfg)',"    from e2_guard01_before_constructor_v3 import enforce_before_constructor\n    enforce_before_constructor(cfg, os.environ['MOD4_E2_GUARD01_RECEIPT_PATH'])\n    env = Mod4Env(cfg=cfg)")
 write(N/'train_e2_213_guard01_v3.py',entry)
 worker=(F/'worker_e2_original_fullPPO.py').read_text(encoding='utf8')
 worker=once(worker,' validate_job(J,task,go)'," validate_job(J,task,go)\n from e2_guard01_repair_contract_v3 import validate_repair_task\n repair_evidence=read(J/'PRELAUNCH_E2_SOLO_ACTUAL_EVIDENCE.json');validate_repair_task(task,repair_evidence,go)")
 worker=once(worker,' import torch\n from source_cache213'," assert H(mod/'train_e2_213.py')==task['guard_entry_SHA']\n os.environ['MOD4_E2_GUARD01_RECEIPT_PATH']=str(OUT/'E2_GUARD01_BEFORE_ENV_CONSTRUCTOR_ACTUAL.json')\n put('E2_GUARD01_NEW_SOURCE_READ_PURPOSE_ACTUAL.json',repair_evidence['guard01_repair_admission'])\n import torch\n from source_cache213")
 worker=once(worker," entry=mod/'train_e2_213.py'", " typed.update(explicit_mimic_guard_tightening=True,original_inherited_mimic_threshold_radians=.05,planned_mimic_threshold_radians=.01,closure_threshold_m=.002,guard_entry_SHA=task['guard_entry_SHA'],new_selected_source_read_purpose_id=task['new_selected_source_read_purpose_id'])\n entry=mod/'train_e2_213.py'")
 worker=once(worker,"    assert runner.current_learning_iteration==ITER and runner.alg.learning_rate==LR", "    guard=read(OUT/'E2_GUARD01_BEFORE_ENV_CONSTRUCTOR_ACTUAL.json')\n    assert guard['passed'] and guard['original_mimic_radians']==.05 and guard['planned_effective_mimic_radians']==.01 and guard['closure_m']==.002 and guard['all_other_termination_params_unchanged_in_JSON_supported_projection']\n    assert runner.current_learning_iteration==ITER and runner.alg.learning_rate==LR")
 worker=once(worker,"     original_new_physical_episode_not_exact_PhysX_resume=True,startup_complete=startup", "     original_new_physical_episode_not_exact_PhysX_resume=True,actual_mimic_threshold_radians=.01,actual_closure_threshold_m=.002,guard_before_constructor=guard,startup_complete=startup")
 worker=once(worker,"     source_SHA=SHA,optimizer_updates=0,actual_RewardManager_dt_s=.02", "     source_SHA=SHA,optimizer_updates=0,actual_mimic_threshold_radians=.01,actual_closure_threshold_m=.002,actual_RewardManager_dt_s=.02")
 write(N/'worker_e2_original_fullPPO.py',worker)
 install=json.loads((F/'reports/INSTALL_E2_SOLO_ORIGINAL_SOURCE_V2.json').read_bytes())
 selected={'worker_e2_original_fullPPO.py':N/'worker_e2_original_fullPPO.py','runtime/isaac/mod4/train_e2_213.py':N/'train_e2_213_guard01_v3.py'}
 install['files']=[row(selected[x['relative']],x['relative']) if x['relative'] in selected else x for x in install['files']]
 for name in ('e2_guard01_before_constructor_v3.py','e2_guard01_repair_contract_v3.py'):install['files'].append(row(N/name,name))
 install.update(explicit_mimic_guard_tightening_V3=True,legacy_mimic_radians=.05,required_current_mimic_radians=.01,closure_m=.002,
  guard_entry_SHA=ref(N/'train_e2_213_guard01_v3.py')['SHA'],original_runtime_mod4_task_unchanged=True,
  prior235_source1_decode1_consumed=True,new_worker_source1_decode1_requires_new_ROOT_admission=True)
 put(R/'INSTALL_E2_GUARD01_V3.json',install)

 generator=(S/'prepare_e2_solo_Task_manifest_Ready_SOURCE_ONLY.py').read_text(encoding='utf8')
 generator=once(generator,'from pathlib import Path,PurePosixPath',"from pathlib import Path,PurePosixPath\nimport sys\nsys.path.insert(0,str(Path(__file__).resolve().parent.parent/'E2_QUALIFIED_FULLSTATE_SOLO_PPO_SOURCE_NEXT_V1_20261101'))\nfrom e2_guard01_repair_contract_v3 import prior_failed_closed,new_read_admission")
 generator=once(generator,"('saved-cpu','scoped-actual232','fresh-admission','install','out-new')", "('saved-cpu','scoped-actual232','fresh-admission','install','out-new','failed235-closing','actual235-work-order')")
 generator=once(generator,"p.add_argument('--run-id',required=True);", "p.add_argument('--new-source-read-purpose-id',required=True);p.add_argument('--run-id',required=True);")
 generator=once(generator," admission,fr=metadata(a.fresh_admission);fresh(admission)", " admission,fr=metadata(a.fresh_admission);fresh(admission)\n closed,closedref=metadata(a.failed235_closing);order,orderref=metadata(a.actual235_work_order)\n prior=prior_failed_closed(closed,order);repair=new_read_admission(prior,a.new_source_read_purpose_id,a.run_id)\n assert admission['checked_epoch']>=prior['closed_epoch']")
 generator=once(generator,"actual232_scoped_ref=sr,fresh_actual=admission", "actual232_scoped_ref=sr,guard01_repair_admission=repair,prior235_failed_closing_ref=closedref,prior235_work_order_ref=orderref,fresh_actual=admission")
 generator=once(generator," validate_task(task);tb=raw(task)", " task.update(explicit_mimic_guard_tightening=True,original_inherited_mimic_threshold_radians=.05,planned_mimic_threshold_radians=.01,closure_threshold_m=.002,guard_entry_SHA=names['runtime/isaac/mod4/train_e2_213.py']['SHA'],new_selected_source_read_purpose_id=a.new_source_read_purpose_id,legacy232_not_mimic01_proof=True)\n validate_task(task);tb=raw(task)")
 generator=once(generator," mb=raw(manifest);msha=hashlib.sha256(mb).hexdigest()", " manifest.update({k:task[k] for k in ('explicit_mimic_guard_tightening','original_inherited_mimic_threshold_radians','planned_mimic_threshold_radians','closure_threshold_m','guard_entry_SHA','new_selected_source_read_purpose_id','legacy232_not_mimic01_proof')})\n mb=raw(manifest);msha=hashlib.sha256(mb).hexdigest()")
 generator=once(generator," spec=dict(key=ROLE", " ready.update({k:task[k] for k in ('explicit_mimic_guard_tightening','original_inherited_mimic_threshold_radians','planned_mimic_threshold_radians','closure_threshold_m','guard_entry_SHA','new_selected_source_read_purpose_id','legacy232_not_mimic01_proof')})\n ready['V3_native24_under_mimic01_pending_before_PPO']=True\n spec=dict(key=ROLE")
 generator=once(generator,"max_parent_seconds=3900,exit_headroom_seconds=300,no_physics_change=True", "max_parent_seconds=3900,exit_headroom_seconds=300,no_physics_change=False,no_other_physics_change=True")
 generator=once(generator," assert valid_ready_value(ready,spec)", " spec.update({k:task[k] for k in ('explicit_mimic_guard_tightening','original_inherited_mimic_threshold_radians','planned_mimic_threshold_radians','closure_threshold_m','guard_entry_SHA','new_selected_source_read_purpose_id')})\n assert valid_ready_value(ready,spec)")
 write(N/'prepare_e2_solo_Task_manifest_Ready_GUARD01_V3.py',generator)

 control=json.loads((S/'reports/CONTROL_E2_SOLO_FROZEN_BINDINGS.json').read_bytes())
 protocol=(S/'e2_solo_protocol.py').read_text(encoding='utf8')
 protocol=once(protocol,"and s['no_physics_change']", "and s['no_physics_change'] is False and s['no_other_physics_change'] is True\n assert s['explicit_mimic_guard_tightening'] and s['original_inherited_mimic_threshold_radians']==.05 and s['planned_mimic_threshold_radians']==.01 and s['closure_threshold_m']==.002\n assert len(s['guard_entry_SHA'])==64 and s['new_selected_source_read_purpose_id'].startswith('ROOT_E2_MIMIC01_V3_')")
 protocol=once(protocol,"value.get('closed_source_CPU')", "value.get('closed_source_CPU')") if "value.get('closed_source_CPU')" in protocol else protocol
 protocol=once(protocol,"and valid_ready_value(value,spec))", "and valid_ready_value(value,spec) and all(value.get(k)==spec[k] for k in ('guard_entry_SHA','new_selected_source_read_purpose_id','planned_mimic_threshold_radians','original_inherited_mimic_threshold_radians','closure_threshold_m','explicit_mimic_guard_tightening')))")
 protocol=once(protocol,"return dict(role_key=ROLE", "return dict(explicit_mimic_guard_tightening=True,original_inherited_mimic_threshold_radians=.05,planned_mimic_threshold_radians=.01,closure_threshold_m=.002,guard_entry_SHA=s['guard_entry_SHA'],new_selected_source_read_purpose_id=s['new_selected_source_read_purpose_id'],role_key=ROLE")
 write(N/'e2_solo_protocol_guard01_v3.py',protocol)
 control['files']=[row(N/'e2_solo_protocol_guard01_v3.py','e2_solo_protocol.py') if x['relative']=='e2_solo_protocol.py' else x for x in control['files']]
 control.update(explicit_mimic_guard_tightening_V3=True,original_owner_node_sender_HMAC_twofcntl_charge_byte_unchanged=True)
 put(R/'CONTROL_E2_GUARD01_V3_FROZEN_BINDINGS.json',control)

 for name in ('caller_common.py','launch_e2_solo_install_FIRST_ROOT_ONLY_once.py','collect_e2_solo_original_formal_cost_normal900_ROOT_ONLY_once.py','review_e2_solo_NEW_formal_initial_whole_CPU_ROOT_ONLY_once.py','remote_e2_solo_payloads.py','remote_e2_solo_additions.py'):
  text=(C/name).read_text(encoding='utf8').replace('ROOT_E2_SOLO','ROOT_E2_GUARD01_V3')
  if name=='caller_common.py':
   text=once(text,"INDEX='INDEX_E2_SOLO_ROOT_CALLERS_FROZEN.json'", "INDEX='INDEX_E2_GUARD01_V3_FROZEN.json'")
  elif name.startswith('launch'):
   text=once(text,"from e2_solo_protocol import validate_schedule", "from e2_solo_protocol_guard01_v3 import validate_schedule\nfrom e2_guard01_repair_contract_v3 import prior_failed_closed,new_read_admission")
   text=once(text,"for name in ('saved-e2-cpu','scoped-actual232','auth-provider')", "for name in ('saved-e2-cpu','scoped-actual232','auth-provider','failed235-closing','actual235-work-order')")
   text=once(text,' a=p.parse_args()'," p.add_argument('--new-source-read-purpose-id',required=True)\n a=p.parse_args()")
   text=once(text,"scope,sr=metadata(a.scoped_actual232);scoped232(scope)", "scope,sr=metadata(a.scoped_actual232);scoped232(scope)\n closed,closedref=metadata(a.failed235_closing);order,orderref=metadata(a.actual235_work_order)\n prior=prior_failed_closed(closed,order);repair=new_read_admission(prior,a.new_source_read_purpose_id,a.run_id)")
   text=text.replace("R/'CPU_E2_SOLO_CALLERS_NEW_INTERFACE_ACTUAL.json'", "R/'CPU_E2_GUARD01_V3_NEW_INTERFACE_ACTUAL.json'")
   text=text.replace("FINITE/'reports/INSTALL_E2_SOLO_ORIGINAL_SOURCE_V2.json'", "N/'reports/INSTALL_E2_GUARD01_V3.json'")
   text=text.replace("SOURCE/'reports/CONTROL_E2_SOLO_FROZEN_BINDINGS.json'", "N/'reports/CONTROL_E2_GUARD01_V3_FROZEN_BINDINGS.json'")
   text=once(text,"assert install['before_use_worker_finite_V2']", "assert install['before_use_worker_finite_V2'] and install['explicit_mimic_guard_tightening_V3']")
   text=once(text,"saved_qualified_CPU_ref=cr,actual232_scoped_ref=sr,", "saved_qualified_CPU_ref=cr,actual232_scoped_ref=sr,prior235_failed_closing_ref=closedref,prior235_work_order_ref=orderref,NEW_guard01_source_read_purpose=repair,")
   text=text.replace("SOURCE/'prepare_e2_solo_Task_manifest_Ready_SOURCE_ONLY.py'", "N/'prepare_e2_solo_Task_manifest_Ready_GUARD01_V3.py'")
   text=once(text,"'--saved-cpu',str(a.saved_e2_cpu)", "'--failed235-closing',str(a.failed235_closing),'--actual235-work-order',str(a.actual235_work_order),'--new-source-read-purpose-id',a.new_source_read_purpose_id,\n   '--saved-cpu',str(a.saved_e2_cpu)")
  elif name.startswith('review'):
   text=once(text,"assert t['PhysX_exact_resume_claimed']", "assert t['explicit_mimic_guard_tightening'] and t['original_inherited_mimic_threshold_radians']==.05 and t['planned_mimic_threshold_radians']==.01 and t['closure_threshold_m']==.002\n assert len(t['guard_entry_SHA'])==64 and t['new_selected_source_read_purpose_id'].startswith('ROOT_E2_MIMIC01_V3_')\n assert t['PhysX_exact_resume_claimed']")
  write(N/name,text)
 put(R/'V3_SOURCE_DERIVATION_AND_LITERAL_SCOPE.json',dict(epoch=time.time(),original235V2_callers_INDEX=ref(C/'INDEX_E2_SOLO_ROOT_CALLERS_FROZEN.json'),
  finiteV2_worker=ref(F/'worker_e2_original_fullPPO.py'),original_train213=ref(P/'train_e2_213.py'),new_entry=ref(N/'train_e2_213_guard01_v3.py'),
  exact_change='Original E2 mimic termination .05 explicitly tightened to planned .01 before constructor;closure.002 unchanged',
  reward_commands_motors_DR_kinematics_solver_closure_other_guard_unchanged=True,finiteV2_tree_and_loss_checks_retained=True,
  original235V2_model1_decode1_consumed=True,V3_is_new_necessary_source_read_purpose_not_replay=True,
  historical232_not_mimic01_physics_proof=True,ROOT_actual_native24_FIRST_pending=True,
  model_asset_raw_Torch_SDK_network_Git=0))

if __name__=='__main__':
 try:main()
 except BaseException:put(R/'DERIVE_GUARD01_V3_ORIGINAL_ERROR.json',dict(error=traceback.format_exc()));raise
